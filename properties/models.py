from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
owner = get_user_model()

class Apartment(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)
    description = RichTextUploadingField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/apartment_images', default=None)
    num_bedrooms = models.IntegerField()
    num_bathrooms = models.IntegerField()
    max_guests = models.IntegerField()
    price_per_month = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Apartment, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        output_size = (500, 500)
        img.thumbnail(output_size)
        img.save(self.image.path)

class Property(models.Model):
    owner = models.ForeignKey(owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    property_type = models.CharField(max_length=200)
    description = RichTextUploadingField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    	return self.name  
