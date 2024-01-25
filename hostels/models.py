from django.urls import reverse
from django.db import models
from django.utils import timezone
#from datetime import date
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from PIL import Image
from .distance import calc_distance
#import secrets
#from atlass.transaction import Paystack


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


#amenities for each hostel
class Amenities(models.Model):
    amenity = models.CharField(max_length=100)
    fontawesome_icon = models.CharField(max_length=100, default='fa fa-check')

    def __str__(self):
        return self.amenity


#hostel model
class Hostel(models.Model):

    created_by = models.ForeignKey(user, on_delete=models.CASCADE)
    owner_name = models.CharField(max_length=100, default='unarcom', help_text='Enter name of hostel owner')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    campus = models.CharField(max_length=100, default='Main Campus', help_text='Enter campus the hostel is located')
    hostel_name = models.CharField(max_length=50, default='unnamed hostel')
    contact = models.CharField(help_text='0589 693 6595', max_length=10)
    display_image = models.ImageField(blank=True, upload_to='unarcom/hostel/images', default=None)
    date_added = models.DateTimeField(default=timezone.now)
    no_of_rooms = models.PositiveIntegerField(help_text='E.g 20')
    description = RichTextUploadingField()
    hostel_coordinates = models.CharField(max_length=100, help_text='latitude, longitude')
    cost_range = models.CharField(max_length=200, help_text='4500')
    duration_of_rent = models.PositiveIntegerField(help_text='2')
    wifi = models.CharField(max_length=50)
    hostel_amenities = models.JSONField(null=True, default=dict, blank=True)
    amenities = models.ManyToManyField(Amenities)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=10, decimal_places=1)

    '''
    trimming images to an appropriate size before saving to the database
    '''
    def save(self, *args, **kwargs):
        super(Hostel, self).save(*args, **kwargs)

        img = Image.open(self.display_image.path)

        #if img.height > 500 or img.width > 500:
        output_size = (350, 350)
        img.thumbnail(output_size)
        img.save(self.display_image.path, optimize=True, quality=95)

    def __str__(self):
        return self.hostel_name

    def get_absolute_url(self):
        return reverse('hostel-detail', kwargs={'pk': self.pk})

    '''
    a method to get the cost of a romm
    '''
    def get_cost(self):
        return self.cost_range

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
This model defines the inferface for a creating a roomtype
in each hostel
'''
class RoomType(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=100)
    room_display_image = models.ImageField(upload_to='unarcom/room_type/images', default=None, null=True, blank=True)
    room_type_number = models.PositiveIntegerField()
    room_numbers = models.JSONField(default=dict)
    room_capacity = models.PositiveIntegerField()
    max_capacity = models.PositiveIntegerField()
    cost_per_head = models.DecimalField(max_digits=65, decimal_places=2)
    db_use_only = models.PositiveIntegerField()
    details = RichTextUploadingField()


    def __str__(self):
        return f'{self.room_type} - {self.hostel}'

    def save(self, *args, **kwargs):
        super(RoomType, self).save(*args, **kwargs)

        img = Image.open(self.room_display_image.path)

        #if img.height > 500 or img.width > 500:
        output_size = (350, 350)
        img.thumbnail(output_size)
        img.save(self.room_display_image.path, optimize=True, quality=95)


    def get_hostel(self):
        return self.hostel

    #get total number of beds remaining
    def get_number_beds(self):

        total_beds_available = self.room_type_number * self.room_capacity

        return total_beds_available



class RoomTypeImages(models.Model):
    room = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_type_images = models.ImageField(blank=True, upload_to='unarcom/room_type/images', default=None)


    def __str__(self):
        return f'Room type: {self.room}'

    class Meta:
        verbose_name_plural = 'Room Images'


    def save(self, *args, **kwargs):
        super(RoomTypeImages, self).save(*args, **kwargs)

        img = Image.open(self.room_type_images.path)

        #if img.height > 500 or img.width > 500:
        output_size = (500, 500)
        img.thumbnail(output_size)
        img.save(self.room_type_images.path, optimize=True, quality=95)


    def return_first_four_photos(self):
        photos = self.room_type_images.all()[0:4]
        return photos

    def get_hostel(self):
        return self.room.hostel



class Room(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    room_occupant_gender = models.CharField(max_length=7, blank=True)
    is_booked = models.BooleanField(default=False)
    is_full = models.BooleanField(default=False)

    def __str__(self):
        return self.room_number


    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def hostel(self):
        return self.room_type.hostel

    def get_campus(self):
        return self.room_type.hostel.campus

    def cost_per_head(self):
        return self.room_type.cost_per_head

    def get_hostel_distance(self):
        return self.room_type.hostel.get_dist()


    def original_amount(self):

        #original_rate = (float(self.room_type.cost_per_head) / 1.04)
        original_rate = (float(self.room_type.cost_per_head) - float(50))

        return original_rate
