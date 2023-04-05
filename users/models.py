from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from .managers import CustomManager
from django.contrib.auth.models import AbstractBaseUser
#from PIL import Image


class RoomUser(AbstractBaseUser):
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	ghana_card_number = models.CharField(max_length=50)
	telephone = PhoneNumberField()
	gender = models.CharField(max_length=10)
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

