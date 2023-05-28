from django.urls import reverse
from django.db import models
from django.utils import timezone
from datetime import date
#from ckeditor_uploader.fields import RichTextUploadingField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from PIL import Image
from .distance import calc_distance
from .tasks import add_after_expiry_task
from multiselectfield import MultiSelectField
#from django.utils.text import slugify

user = get_user_model()


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



#class HostelImages(models.Model):
#    files = models.ImageField(blank=True,
#                              upload_to='static/images',
#                              default=None)

class Hostel(models.Model):
    '''    
    defining the database fields of the databases
    '''
    owner_name = models.CharField(max_length=100, default='unarcom')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    campus = models.CharField(max_length=100, default='Main Campus')
    hostel_name = models.CharField(max_length=50, default='unnamed hostel')
    contact = PhoneNumberField()
    image = models.ImageField(blank=True, upload_to='unarcom/hostel/images', default=None)
    date_added = models.DateTimeField(default=timezone.now)
    no_of_rooms = models.PositiveIntegerField()
    hostel_coordinates = models.CharField(max_length=100)
    cost_per_room = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.PositiveIntegerField()
    wifi = models.CharField(max_length=20, null=True, blank=True)
    toilet = models.CharField(max_length=100, null=True, blank=True)
    study_area = models.CharField(max_length=100, null=True, blank=True)
    water = models.CharField(max_length=100, null=True, blank=True)
    bath_rooms = models.CharField(max_length=200, null=True, blank=True)
    ac_fan = models.CharField('AC/Fun', max_length=100, null=True, blank=True)
    power_supply = models.CharField(max_length=200, null=True, blank=True)
    details = models.TextField()


    '''
    trimming images to an appropriate size before saving to the database
    '''
    def save(self, *args, **kwargs):
        super(Hostel, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        #if img.height > 500 or img.width > 500:
        output_size = (250, 350)
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
    tenant = models.ForeignKey(user, on_delete=models.CASCADE)
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
    is_verified = models.BooleanField(default=False)

    '''
    get and return the message of name of the message sent
    '''
    def __str__(self):
        return self.hostel.hostel_name

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