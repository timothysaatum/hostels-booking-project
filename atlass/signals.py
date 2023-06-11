from .models import Booking
from hostels.models import Room
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Booking)
def reduce_hostel_number(sender, instance, **kwargs):
	'''
	get the specific hostel instance the User is interacting with
	'''
	#room_type = instance.room
	hostel = instance.room_type.hostel
	room_type = instance.room_type
	
	#reducing the number of room-type number by one whenever a booking is made
	#if the roomt-type is 1 in a room
	#reduce the room-type-number by 1 since only one person can stay in the roo
	if instance.room_type == '1 in a room':
		instance.room_type.room_type_number -= 1


	#if room-type is 2 students per room, and the room capacity is more than 1
	#reduce room capacity by 1 else add 1 to the room capacity making it two
	if instance.room_type == '2 in a room':
		if room_type.room_capacity > 1:
			room_type.room_capacity -= 1
		else:
			room_type.room_capacity += 1
			room_type.room_type_number -= 1 


	#if room type is 3 in a room, reduce room capacity by 1 if it is > 1 and increase by 2 if it is 
	#equal to 1
	if room_type == '3 in a room':
		if room_type.room_capacity > 1:
			room_type.room_capacity -= 1

		if room_type.room_capacity == 1:
			room_type.room_capacity += 2
			room_type.room_type_number -= 1

	#if room type is 4, and room capacity is > 1 reduce room capacity by 1, else increase by 3
	if room_type == '4 in a room':
		if room_type.room_capacity > 1:
			room_type.room_capacity -= 1
		if room_type.room_capacity == 1:
			room_type.room_capacity += 3
			room_type.room_type_number -= 1

	#if all the rooms in that room category are booked, reduce the number of rooms in the hoste by one
	if room_type.room_type_number == 0:
		hostel.no_of_rooms -= db_use_only

	#save the updated fields to the database
	hostel.save()
	room_type.save()