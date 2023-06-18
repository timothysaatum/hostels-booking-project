from .models import Booking
from hostels.models import RoomType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F

@receiver(post_save, sender=Booking)
def update_room(sender, instance, created, **kwargs):
	'''
	get the specific hostel instance the User is interacting with
	'''
	#room_type = instance.room
	if created:
		room = instance.room
		room_instance = instance.room_type
		hostel = instance.room_type.hostel

		if room_instance.room_type == '1 in a room':
			room.capacity -= 1
			room_instance.room_type_number -= 1

		if room_instance.room_type == '2 in a room':
			if room.capacity <= 2 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1


		if room_instance.room_type == '3 in a room':

			if room.capacity <= 3 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1

		if room_instance.room_type == '4 in a room':

			if room.capacity <= 4 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1



		if room_instance.room_type_number == 0:
			hostel.no_of_rooms -= db_use_only


		room.is_booked = True

		if instance.gender == 'Female' or instance.gender == 'female' or instance.gender == 'F' or instance.gender == 'f':
			room.room_occupant_gender = 'F'


		if instance.gender == 'Male' or instance.gender == 'male' or instance.gender == 'M' or instance.gender == 'm':
			room.room_occupant_gender = 'M'

		room.save()
		room_instance.save()
		hostel.save()

	else:
		room = Room.objects.filter(id=instance).first()
		room_type_instance = RoomType.objects.filter(room_type=instance).first()
		print(room, room_type)
			


@receiver(post_delete, sender=Booking)
def update_room_numbers(sender, instance, **kwargs):
	room = instance.room
	room_type = instance.room_type


	if room_type.room_type == '1 in a room':
		room.capacity += 1
		room_type.room_type_number += 1
		room.is_booked = False
		

	if room_type.room_type == '2 in a room':

		if room.capacity >= 0 and room.capacity <= 1:
			room.capacity += 1
			print('Here 2')
			if room.capacity == 2:
				room.is_booked = False
				room_type.room_type_number += 1

	if room_type.room_type == '3 in a room':
		print('Here 3')
		if room.capacity >= 0 and room.capacity <= 2:
			room.capacity += 1

			if room.capacity == 2:
				room.is_booked = False
				room_type.room_type_number += 1

	if room_type.room_type == '4 in a room':
		print('Here 4')
		if room.capacity >= 0 and room.capacity <= 3:
			room.capacity += 1

			if room.capacity == 4:
				room.is_booked = False
				room_type.room_type_number += 1

	room.save()
	room_type.save()