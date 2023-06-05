from django.urls import reverse
from django.db import models
from django.utils import timezone
from datetime import date
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from PIL import Image
from .distance import calc_distance
from .tasks import add_after_expiry_task
import secrets
from atlass.transaction import Paystack


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




#model class for creating a hostel
class Hostel(models.Model):

    user_name = models.ForeignKey(user, on_delete=models.CASCADE)
    owner_name = models.CharField(max_length=100, default='unarcom', help_text='Enter name of hostel owner')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    campus = models.CharField(max_length=100, default='Main Campus', help_text='Enter campus the hostel is located')
    hostel_name = models.CharField(max_length=50, default='unnamed hostel')
    contact = models.CharField(help_text='0589 693 6595', max_length=10)
    display_image = models.ImageField(blank=True, upload_to='unarcom/hostel/images', default=None)
    date_added = models.DateTimeField(default=timezone.now)
    no_of_rooms = models.PositiveIntegerField(help_text='E.g 20')
    hostel_coordinates = models.CharField(max_length=100, help_text='latitude, longitude')
    cost_per_room = models.DecimalField(max_digits=8, decimal_places=2, help_text='4500')
    duration_of_rent = models.PositiveIntegerField(help_text='2')
    wifi = models.CharField(max_length=50)
    hostel_amenities = models.JSONField(null=True, default=dict, blank=True)
    details = RichTextUploadingField(help_text='Enter anything that is not in the amenities')


    '''
    trimming images to an appropriate size before saving to the database
    '''
    def save(self, *args, **kwargs):
        super(Hostel, self).save(*args, **kwargs)

        img = Image.open(self.display_image.path)

        #if img.height > 500 or img.width > 500:
        output_size = (250, 350)
        img.thumbnail(output_size)
        img.save(self.display_image.path)
    
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


#model for bulk upload of hostel images
class HostelImages(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    images = models.ImageField(blank=True, upload_to='unarcom/hostel/images', default=None)

    class Meta:
        verbose_name_plural = 'Hostel Images'
