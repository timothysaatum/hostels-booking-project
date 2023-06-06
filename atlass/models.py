from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import secrets
from django.urls import reverse
from .transaction  import  Paystack
from datetime import date
from hostels.tasks import add_after_expiry_task
from hostels.models import Hostel


user = get_user_model()


#an account for each user to store their payments
class Account(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='GHS')
    balance = models.DecimalField(max_digits=1000000000, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.user.__str__()


#model for storing a user bookings
class Booking(models.Model):

    tenant = models.ForeignKey(user, on_delete=models.CASCADE, blank=True, null=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    room_no = models.PositiveIntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.EmailField()
    city_or_town = models.CharField(max_length=100)
    university_identification_number = models.PositiveIntegerField()
    region_of_residence = models.CharField(max_length=100)
    digital_address = models.CharField(max_length=100)
    ref = models.CharField(max_length=200)
    email = models.EmailField()
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
    getting the price of the hostel
    '''
    def price(self):
        return self.hostel.get_cost()


    '''assigning a room number to the tenant'''

    def get_rooms(self):
        number_of_rooms = self.hostel.no_of_rooms
        rn = 0
        for i in range(1, number_of_rooms):

            room = yield i

            rn = rn + room.next()
        return rn


    '''
    getting the hostel name
    '''
    def hostel_booked(self):
        return self.hostel.hostel_name


    '''
    auto calculating the expiry date of the rent
    '''
    def expiration_date(self):
        delta = self.check_in + timezone.timedelta(days=366)
        return delta


    '''
    a method that checks when user rent expires and increase the number of hostels by 1
    '''
    def increase_number_of_rooms(self):
       add_after_expiry_task.apply_async(args=(self.pk, self.hostel), countdown=5)


    def days_remaining(self):
        full_dur = self.check_in + timezone.timedelta(days=366)

        days_rem = full_dur - timezone.now()

        days_left =days_rem.days

        if days_left == 1:
            return f'{days_left} day left'
        elif days_left == 0:
            return 'Your rent has expired'
        else:
            return f'{days_left} days left'