
# Signals to update cached fields
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Room, RoomType


@receiver([post_save, post_delete], sender=Room)
def update_room_type_cache(sender, instance, **kwargs):
    """Update room type cached fields when rooms change"""
    if hasattr(instance, 'room_type') and instance.room_type:
        room_type = instance.room_type
        room_type.available_rooms_count = room_type.rooms.filter(is_available=True).count()
        room_type.save(update_fields=['available_rooms_count'])
        
        # Update hostel cache
        room_type.hostel.update_cached_fields()

@receiver([post_save, post_delete], sender=RoomType)
def update_hostel_cache(sender, instance, **kwargs):
    """Update hostel cached fields when room types change"""
    if hasattr(instance, 'hostel') and instance.hostel:
        instance.hostel.update_cached_fields()