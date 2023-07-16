from .models import Booking
from hostels.models import RoomType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .utils import send_email_with_transaction


@receiver(post_save, sender=Booking)
def update_room(sender, instance, created, **kwargs):
	'''
	get the specific hostel instance the user is interacting with
	'''
	if created:
		room = instance.room
		room_instance = instance.room_type
		hostel = instance.room_type.hostel

		if room_instance.room_type == '1 in a room':
			room.capacity -= 1
			room_instance.room_type_number -= 1
			hostel.no_of_rooms -= 1
			room.is_full = True

		if room_instance.room_type == '2 in a room':
			if room.capacity <= 2 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1
					hostel.no_of_rooms -= 1
					room.is_full = True


		if room_instance.room_type == '3 in a room':

			if room.capacity <= 3 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1
					hostel.no_of_rooms -= 1
					room.is_full = True

		if room_instance.room_type == '4 in a room':

			if room.capacity <= 4 and room.capacity != 0:
				room.capacity -= 1

				if room.capacity == 0:
					room_instance.room_type_number -= 1
					hostel.no_of_rooms -= 1
					room.is_full = True



		#if room_instance.room_type_number == 0:
		#	hostel.no_of_rooms -= room_instance.db_use_only


		room.is_booked = True

		if instance.gender == 'Female':
			room.room_occupant_gender = 'F'


		if instance.gender == 'Male':
			room.room_occupant_gender = 'M'

		room.save()
		room_instance.save()
		hostel.save()


	#send reminder email
	recipient_list = [instance.email_address]
	subject = 'Thank you for booking with us.'
	body = f'''
	\n
	In case you couldn't finish payment due to network issues, 
	Use the link below to finalize your payment and claim your room within 24 hours
	www.trustunarcom.com/room/pay/{instance.pk}/
	'''
	send_email_with_transaction(subject, body, recipient_list)


			


@receiver(post_delete, sender=Booking)
def update_room_numbers(sender, instance, **kwargs):
	room = instance.room
	room_type = instance.room_type
	hostel = instance.room_type.hostel


	if room_type.room_type == '1 in a room':
		room.capacity += 1
		room_type.room_type_number += 1
		hostel.no_of_rooms += 1
		room.is_booked = False
		room.is_full = False
		

	if room_type.room_type == '2 in a room':

		if room.capacity >= 0 and room.capacity <= 1:
			room.capacity += 1
			if room.capacity == 2:
				room.is_booked = False
				room.is_full = False
				room_type.room_type_number += 1
				hostel.no_of_rooms += 1

	if room_type.room_type == '3 in a room':
		if room.capacity >= 0 and room.capacity <= 2:
			room.capacity += 1

			if room.capacity == 3:
				room.is_booked = False
				room.is_full = False
				room_type.room_type_number += 1
				hostel.no_of_rooms += 1

	if room_type.room_type == '4 in a room':

		if room.capacity >= 0 and room.capacity <= 3:
			room.capacity += 1

			if room.capacity == 4:
				room.is_booked = False
				room.is_full = False
				room_type.room_type_number += 1
				hostel.no_of_rooms += 1

	room.save()
	room_type.save()
	hostel.save()
	print('Adding room... ok')