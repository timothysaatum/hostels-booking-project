from .models import Booking
from hostels.models import RoomType
from django.db.models.signals import post_save
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
			room_instance.room_type_number -= 1

		if room_instance.room_type == '2 in a room':
			if room_instance.room_capacity > 1:
				room_instance.room_capacity -= 1

			else:
				room_instance.room_capacity += 1
				room_instance.room_type_number -= 1


		if room_instance.room_type == '3 in a room':
			if room_instance.room_capacity > 1:
				room_instance.room_capacity -= 1

			else:
				room_instance.room_capacity += 2
				room_instance.room_type_number -= 1
			
		if room_instance.room_type == '4 in a room':
			if room_instance.room_capacity > 1:
				room_instance.room_capacity -= 1

			else:
				room_instance.room_capacity += 3
				room_instance.room_type_number -= 1

		if room_instance.room_type_number == 0:
			hostel.no_of_rooms -= db_use_only
			
	room.is_booked = True
	room.room_occupant_gender = instance.gender
	room.save()
	room_instance.save()
	hostel.save()
