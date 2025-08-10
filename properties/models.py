from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
owner = get_user_model()

class City(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

class Apartment(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    contact = models.CharField(max_length=10)
    description = RichTextUploadingField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='unarcom/apartment/images', default=None)
    num_bedrooms = models.PositiveIntegerField()
    num_bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
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
    image = models.ImageField(upload_to='unarcom/properties/images', default=None)
    location = models.CharField(max_length=100)
    property_type = models.CharField(max_length=200)
    rating = models.PositiveIntegerField()
    description = RichTextUploadingField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
    	return self.name  

    def save(self, *args, **kwargs):
        super(Property, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        output_size = (500, 500)
        img.thumbnail(output_size)
        img.save(self.image.path)