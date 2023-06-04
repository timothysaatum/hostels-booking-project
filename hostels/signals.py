from atlass.models import Booking
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Booking)
def reduce_hostel_number(sender, instance, **kwargs):
	'''
	get the specific hostel instance the User is interacting with
	'''
	hostel = instance.hostel
	'''
	reducing the number of rooms by one whenever a booking is made
	'''
	'''
	check to see if the number of hostels is less than or equal to 1
	'''
	if hostel.no_of_rooms >= 1:
		'''
		if the number is more than 1 reduce by 1
		'''
		hostel.no_of_rooms -= 1
	'''
	saving the changes to the database
	'''
	hostel.save()

