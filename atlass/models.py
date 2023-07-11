from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from django.urls import reverse
from .transaction  import  Paystack
import datetime
from hostels.models import Room, RoomType, Hostel


user = get_user_model()


#an account for each user to store their payments
class Account(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
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

    tenant = models.ForeignKey(user, on_delete=models.CASCADE, blank=True, null=True, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, editable=False)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, editable=False)
    check_in = models.DateField(help_text='YYYY-MM-DD', default=datetime.datetime.now)
    number_of_guests = models.PositiveIntegerField(default=1)
    phone_number = models.CharField(max_length=17, null=True, blank=True, editable=False)
    cost = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    room_no = models.CharField(max_length=20, editable=False)
    first_name = models.CharField(max_length=50, editable=False)
    last_name = models.CharField(max_length=50, editable=False)
    gender = models.CharField(help_text='Male/Female', max_length=10, choices=SEX)
    email_address = models.EmailField(editable=False)
    city_or_town = models.CharField(max_length=100, editable=False)
    university_identification_number = models.PositiveIntegerField(editable=False)
    region_of_residence = models.CharField(max_length=100, editable=False)
    digital_address = models.CharField(max_length=100, editable=False)
    receipt_number = models.CharField(max_length=100, editable=False)
    ref = models.CharField(max_length=200, editable=False)
    is_verified = models.BooleanField(default=False, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)

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

        days_left =days_rem.days

        if days_left == 1:
            return f'{days_left} day left'
        elif days_left == 0:
            return 'Your rent has expired'
        else:
            return f'{days_left} days left'

    def get_account_number(self):
        return self.room_type.hostel.account_number

    def get_hostel(self):
        return self.room_type.hostel
  


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
