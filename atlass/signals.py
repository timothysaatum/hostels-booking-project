from .models import Booking
from hostels.models import Room
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Booking)
def reduce_hostel_number(sender, instance, **kwargs):
	'''
	get the specific hostel instance the User is interacting with
	'''
	room = instance.room
	hostel = instance.room.hostel
	'''
	reducing the number of room-type number by one whenever a booking is made
	'''
	#room_num = 0
	#room_types = ['1 in a room', '2 in a room', '3 in a room', '4 in a room']

	if instance.room_type == '1 in a room':
		room.room_type_number -= 1

	if instance.room_type == '2 in a room':
		if room.room_capacity > 1:
			room.room_capacity -= 1
		else:
			room.room_capacity += 1
			room.room_type_number -= 1 


	if instance.room_type == '3 in a room':
		if room.room_capacity > 1:
			room.room_capacity -= 1

		if room.room_capacity == 1:
			room.room_capacity += 2
			room.room_type_number -= 1

	if instance.room_type == '4 in a room':
		if room.room_capacity > 1:
			room.room_capacity -= 1
		if room.room_capacity == 1:
			room.room_capacity += 3
			room.room_type_number -= 1

	if room.room_type_number == 0:
		hostel.no_of_rooms -= room.db_use_only

	hostel.save()
	room.save()

