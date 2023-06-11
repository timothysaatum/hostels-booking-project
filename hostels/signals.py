from .models import Room, RoomType
from django.db.models.signals import post_save
from django.dispatch import receiver




@receiver(post_save, sender=RoomType)
def create_room(sender, instance, **kwargs):

	room_nos = instance.room_numbers

	for val in room_nos.values():
		Room.objects.create(room_type=instance, room_number=val)
