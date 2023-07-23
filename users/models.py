from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from .managers import CustomManager
from django.urls import reverse
#from PIL import Image

SEX = [
    ('Male', 'Male'),
    ('Female', 'Female')
    ]
class RoomUser(AbstractBaseUser):
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	ghana_card_number = models.CharField(max_length=50)
	telephone = models.CharField(help_text='0597856551', max_length=20)
	gender = models.CharField(max_length=10, choices=SEX)
	your_emmergency_contact = models.CharField(help_text='0597856551', max_length=20)
	name_of_emmergency_contact = models.CharField('His/Her Name', max_length=50)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	date_joined = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = 	['telephone']

	objects = CustomManager()


	def __str__(self):
		return f'{self.first_name} {self.last_name}'

	def has_perm(self, perm, obj=None):
		"Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
		return True

	def has_module_perms(self, app_label):
		return True


	@property
	def is_staff(self):
		return self.is_admin


class Complain(models.Model):
	email = models.EmailField()
	phone = models.CharField(help_text='0597856551', max_length=10)
	address = models.CharField(max_length=300)
	full_name = models.CharField(max_length=300)
	message = models.TextField()
	date_added = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse('complain') #kwargs={'pk': self.pk})

	def __str__(self):
		return self.full_name



class Contact(models.Model):
	email = models.EmailField()
	phone = models.CharField(help_text='0597856551', max_length=10)
	address = models.CharField(max_length=300)
	full_name = models.CharField(max_length=300)
	message = models.TextField()
	date_added = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse('contact') #kwargs={'pk': self.pk})

	def __str__(self):
		return self.full_name


