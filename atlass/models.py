from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from django.urls import reverse
from .transaction  import  Paystack
import datetime
from hostels.models import Room, RoomType, Hostel
from .utils import send_email_with_transaction
from django.contrib import messages


user = get_user_model()


#an account for each user to store their payments
class Account(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='GHS')
    balance = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.user.__str__()


#model for storing a user bookings
SEX = [
    ('Male', 'Male'),
    ('Female', 'Female')
    ]

class Booking(models.Model):

    tenant = models.ForeignKey(user, on_delete=models.CASCADE, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    check_in = models.DateField(help_text='YYYY-MM-DD')
    number_of_guests = models.PositiveIntegerField(default=1)
    phone_number = models.CharField(max_length=17, null=True, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    room_no = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(help_text='Male/Female', max_length=10, choices=SEX)
    email_address = models.EmailField()
    city_or_town = models.CharField(max_length=100)
    university_identification_number = models.PositiveIntegerField()
    region_of_residence = models.CharField(max_length=100)
    digital_address = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=100)
    ref = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"Payment: {self.cost}"

    def amount_value(self):
        return int(self.cost) * 100

    def verify_payment(self):
    	paystack = Paystack()
    	status, result = paystack.verify_payment(self.ref, self.cost)
    	if status:
    		if result['cost'] / 100 == self.cost:
    			self.verified = True
    		self.save()
    	if self.verified:
        	return True
    	return False


    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Booking.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref

        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('booking-details', kwargs={'pk': self.pk})


    '''
    getting the room type
    '''
    def hostel(self):
        return self.room_type.hostel


    '''
    auto calculating the expiry date of the rent
    '''
    def expiration_date(self):
        delta = self.check_in + datetime.timedelta(days=366)
        return delta


    def days_remaining(self):
        full_dur = self.check_in + datetime.timedelta(days=366)

        days_rem = datetime.datetime.combine(full_dur, datetime.datetime.min.time()) - datetime.datetime.now()
        #days_rem = self.expiration_date() - datetime.date()

        days_left =days_rem.days

        if days_left == 1:
            return f'{days_left} day left'
        elif days_left == 0:
            return 'Your rent has expired'
        else:
            return f'{days_left} days left'

    def get_account_number(self):
        return self.room_type.hostel.account_number


    def account_name(self):
        return self.room_type.hostel.account_name

    def get_hostel(self):
        return self.room_type.hostel


    def get_seed_amount(self):
        original_rate = (float(self.cost) / 1.04)

        return original_rate

    def send_email(self):
        landlord = self.room_type.hostel.created_by.email
        print(landlord)

        try:
            subject = f'{self.email_address} has just paid you!'
            body = f'''\n
            {self.email_address} has just booked {self.room_no}. He is expected to arrive on {self.check_in}
            Your rent should be expected within 24hrs for our system to remit the money to your account.
            You can view this transaction on your dashboard - www.trustunarcom.com/admin/dashboard/
            \n
            Do not hesitate to contact us if you have not received your funds:

            Contact details
            Tel: 0594438287/0503835921
            Email: timothysaatum@gmail.com
            '''
            send_email_with_transaction(subject, body, landlord)

        except Exception as e:
            pass
  


class LeaveRequests(models.Model):
    hostel = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    your_course = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=14)
    purpose = models.TextField()
    i_affirm_everything_in_my_room_is_intact = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    appoval_id = models.CharField(max_length=10, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.room.room_number
