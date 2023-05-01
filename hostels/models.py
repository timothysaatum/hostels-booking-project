from django.urls import reverse
from django.db import models
from django.utils import timezone
from datetime import date
from ckeditor_uploader.fields import RichTextUploadingField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from PIL import Image
from .distance import calc_distance
from .tasks import add_after_expiry_task
from django.utils.text import slugify

room_user = get_user_model()


'''
this model define the blueprint for adding a school to our database
'''
class School(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    school_coordinates = models.CharField(max_length=100)
    '''
    return the name of the school
    '''
    def __str__(self):
        return self.name




class Apartment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    num_bedrooms = models.IntegerField()
    num_bathrooms = models.IntegerField()
    max_guests = models.IntegerField()
    price_per_month = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Hostel(models.Model):
    '''
    these are the categories the hostels will be grouped into
    '''
    CATEGORIES = [(1, 'GHS500-GHS1000'), (2, 'GHS1100-GHS1500'),
              (3, 'GHS1600-GHS2000'), (4, 'GHS2100-GHS2500'),
              (5, 'GHS2600-GHS3000'), (6, '3000 & above')]
    '''
    defining the database fields of the databases
    '''
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    campus = models.CharField(max_length=100, default='Main Campus')
    hostel_name = models.CharField(max_length=50, default='unnamed hostel')
    contact = PhoneNumberField()
    image = models.ImageField(blank=True,
                              upload_to='static/images',
                              default=None)
    date_added = models.DateTimeField(default=timezone.now)
    no_of_rooms = models.IntegerField()
    hostel_coordinates = models.CharField(max_length=100)
    category = models.IntegerField(choices=CATEGORIES, default=1)
    cost_per_room = models.FloatField()
    duration = models.IntegerField()
    wifi = models.CharField(max_length=20)
    details = RichTextUploadingField()


    '''
    trimming images to an appropriate size before saving to the database
    '''
    def save(self, *args, **kwargs):
        super(Hostel, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        #if img.height > 500 or img.width > 500:
        output_size = (500, 500)
        img.thumbnail(output_size)
        img.save(self.image.path)
    
    def __str__(self):
        return self.hostel_name

    def get_absolute_url(self):
        return reverse('hostel-detail', kwargs={'pk': self.pk})
    '''
    a method to get the cost of a romm
    '''
    def get_cost(self):
        return self.cost_per_room
    '''
    calculating the distance of the hostel to the campus
    '''

    def get_dist(self):
        try:
            time_to_walk = calc_distance(hostel_coordinates=self.hostel_coordinates, school_coordinates=self.school.school_coordinates)
        except Exception as e:
            return e
        return time_to_walk


    def get_booked_hostel_url(self):
        return reverse('book-hostel', kwargs={'pk': self.pk})

    def get_decline_choice_url(self):
        return reverse('decline-choice', kwargs={'pk': self.pk})



'''
The booking model will contain the data base for all the transactions 
made on the site
'''
class Booking(models.Model):
    '''
    defining the database fields
    '''
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    tenant = models.ForeignKey(room_user, on_delete=models.CASCADE)
    check_in = models.DateTimeField(default=timezone.now)
    momo_no = models.CharField(max_length=10, null=True, blank=True)
    cost = models.FloatField()
    room_no = models.IntegerField()
    account_no = models.CharField(max_length=100, null=True, blank=True)
    message = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)

    '''
    get and return the message of name of the message sent
    '''
    def __str__(self):
        return self.message

    def get_absolute_url(self):
        return reverse('booking-details', kwargs={'pk': self.pk})
    '''
    getting the price of the hostel
    '''
    def price(self):
        return self.hostel.get_cost()
    '''
    getting the hostel name
    '''
    def get_hostel(self):
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