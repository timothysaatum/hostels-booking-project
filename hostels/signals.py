from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.cache import cache
from .models import RoomType, Room, Hostel, ContactInquiry


@receiver(post_save, sender=RoomType)
def update_hostel_cache_on_roomtype_save(sender, instance, created, **kwargs):
    """Update hostel cached fields when room type is saved"""
    if not created:  # Only for updates, not creation (creation is handled in the model)
        transaction.on_commit(lambda: instance.hostel.update_cached_fields())


@receiver(post_delete, sender=RoomType)
def update_hostel_cache_on_roomtype_delete(sender, instance, **kwargs):
    """Update hostel cached fields when room type is deleted"""
    transaction.on_commit(lambda: instance.hostel.update_cached_fields())


@receiver(post_save, sender=Room)
def update_caches_on_room_save(sender, instance, created, **kwargs):
    """Update room type and hostel caches when room is saved"""
    def update_caches():
        # Update room type availability cache
        instance.room_type.available_rooms_count = instance.room_type.rooms.filter(
            is_available=True
        ).count()
        instance.room_type.save(update_fields=['available_rooms_count'])
        
        # Update hostel cache
        instance.room_type.hostel.update_cached_fields()
        
        # Clear related cache keys
        cache_keys = [
            f'hostel_stats_{instance.room_type.hostel.id}',
            f'roomtype_stats_{instance.room_type.id}',
            'hostel_list_cache',
        ]
        cache.delete_many(cache_keys)
    
    transaction.on_commit(update_caches)

@receiver(pre_delete, sender=Room)
def update_caches_on_room_delete(sender, instance, **kwargs):
    room_type = instance.room_type
    hostel = room_type.hostel

    def update_caches():
        available_count = room_type.rooms.filter(is_available=True).count()
        RoomType.objects.filter(pk=room_type.pk).update(
            available_rooms_count=available_count
        )
        hostel.update_cached_fields()

        cache_keys = [
            f'hostel_stats_{hostel.id}',
            f'roomtype_stats_{room_type.id}',
            'hostel_list_cache',
        ]
        cache.delete_many(cache_keys)

    transaction.on_commit(update_caches)


@receiver(pre_delete, sender=RoomType)
def check_rooms_before_roomtype_delete(sender, instance, **kwargs):
    """Check if room type can be safely deleted"""
    occupied_rooms = instance.rooms.filter(current_occupants__gt=0)
    if occupied_rooms.exists():
        from django.core.exceptions import ValidationError
        raise ValidationError(
            f"Cannot delete room type '{instance.name}'. "
            f"{occupied_rooms.count()} rooms have current occupants."
        )


@receiver(post_save, sender=ContactInquiry)
def clear_inquiry_cache_on_save(sender, instance, created, **kwargs):
    """Clear inquiry-related caches when new inquiry is created"""
    if created:
        cache_keys = [
            f'hostel_inquiries_{instance.hostel.owner.id}',
            'dashboard_stats',
        ]
        cache.delete_many(cache_keys)


@receiver(post_save, sender=Hostel)
def clear_hostel_list_cache(sender, instance, **kwargs):
    """Clear hostel list cache when hostel is updated"""
    cache_keys = [
        'hostel_list_cache',
        f'school_hostels_{instance.school.id}',
        'hostel_stats',
    ]
    cache.delete_many(cache_keys)


# Management command signals for data integrity
@receiver(post_save, sender=RoomType)
def log_room_generation(sender, instance, created, **kwargs):
    """Log room generation for audit purposes"""
    if created:
        import logging
        logger = logging.getLogger('hostel_management')
        logger.info(
            f"Room type '{instance.name}' created for hostel '{instance.hostel.name}'. "
            f"{instance.total_rooms} rooms will be auto-generated."
        )


@receiver(post_save, sender=Room)
def log_room_creation(sender, instance, created, **kwargs):
    """Log individual room creation"""
    if created:
        import logging
        logger = logging.getLogger('hostel_management')
        logger.debug(
            f"Room '{instance.room_number}' created for room type '{instance.room_type.name}' "
            f"in hostel '{instance.room_type.hostel.name}'"
        )


# Signal for automatic slug generation
@receiver(post_save, sender=Hostel)
def ensure_hostel_slug(sender, instance, **kwargs):
    """Ensure hostel has a valid slug"""
    if not instance.slug:
        from django.utils.text import slugify
        base_slug = slugify(f"{instance.name}-{instance.school.name}")
        instance.slug = instance._generate_unique_slug(base_slug)
        instance.save(update_fields=['slug'])


# Performance optimization signals
@receiver(post_save, sender=Room)
def batch_update_room_availability(sender, instance, **kwargs):
    """Batch update room availability to avoid N+1 queries"""
    # This runs after the main transaction, so we can safely batch operations
    def batch_update():
        from django.db.models import Count
        
        # Update all room types for this hostel in one go
        hostel = instance.room_type.hostel
        room_types = hostel.room_types.all()
        
        for room_type in room_types:
            available_count = room_type.rooms.filter(is_available=True).count()
            room_type.available_rooms_count = available_count
        
        # Bulk update to reduce database calls
        RoomType.objects.bulk_update(room_types, ['available_rooms_count'])
        
        # Update hostel cache once
        hostel.update_cached_fields()
    
    transaction.on_commit(batch_update)


# Error handling signals
@receiver(post_save, sender=RoomType)
def handle_room_creation_errors(sender, instance, created, **kwargs):
    """Handle errors during automatic room creation"""
    if created:
        try:
            # Verify rooms were created successfully
            expected_rooms = instance.total_rooms
            actual_rooms = instance.rooms.count()
            
            if actual_rooms != expected_rooms:
                import logging
                logger = logging.getLogger('hostel_management')
                logger.warning(
                    f"Room creation mismatch for room type '{instance.name}'. "
                    f"Expected {expected_rooms}, got {actual_rooms}."
                )
                
                # Attempt to create missing rooms
                if actual_rooms < expected_rooms:
                    instance._create_rooms()
        except Exception as e:
            import logging
            logger = logging.getLogger('hostel_management')
            logger.error(
                f"Error during room creation for room type '{instance.name}': {str(e)}"
            )


# Signal to handle distance calculation cache invalidation
@receiver(post_save, sender=Hostel)
def invalidate_distance_cache(sender, instance, **kwargs):
    """Invalidate distance-related caches when hostel coordinates change"""
    if instance.latitude and instance.longitude:
        # Clear school-specific distance caches
        cache.delete(f'hostel_distances_school_{instance.school.id}')
        cache.delete('hostel_list_with_distances')


# Data consistency signals
@receiver(post_save, sender=Room)
def ensure_room_data_consistency(sender, instance, **kwargs):
    """Ensure room data consistency"""
    # Validate occupancy doesn't exceed capacity
    if instance.current_occupants > instance.capacity:
        instance.current_occupants = instance.capacity
        instance.save(update_fields=['current_occupants'])
    
    # Auto-update availability based on occupancy
    was_available = instance.is_available
    should_be_available = instance.current_occupants < instance.capacity
    
    if was_available != should_be_available:
        instance.is_available = should_be_available
        instance.save(update_fields=['is_available'])


# Cleanup signals for orphaned records
@receiver(post_delete, sender=Hostel)
def cleanup_hostel_related_data(sender, instance, **kwargs):
    """Clean up related data when hostel is deleted"""
    # Clear caches
    cache_keys = [
        'hostel_list_cache',
        f'school_hostels_{instance.school.id}',
        'hostel_stats',
        f'hostel_stats_{instance.id}',
    ]
    cache.delete_many(cache_keys)


# Audit trail signals
@receiver(post_save, sender=Room)
def create_room_audit_trail(sender, instance, created, **kwargs):
    """Create audit trail for room changes"""
    if not created and instance._state.fields_cache:
        # Log significant changes
        changes = []
        original = Room.objects.get(pk=instance.pk)
        
        if original.current_occupants != instance.current_occupants:
            changes.append(f"occupancy: {original.current_occupants} → {instance.current_occupants}")
        
        if original.is_available != instance.is_available:
            changes.append(f"availability: {original.is_available} → {instance.is_available}")
        
        if changes:
            import logging
            logger = logging.getLogger('hostel_audit')
            logger.info(
                f"Room {instance.room_number} in {instance.room_type.hostel.name} updated: "
                f"{', '.join(changes)}"
            )


# Performance monitoring signals
@receiver(post_save, sender=RoomType)
def monitor_room_creation_performance(sender, instance, created, **kwargs):
    """Monitor room creation performance"""
    if created:
        import time
        from django.core.cache import cache
        
        start_time = time.time()
        room_count = instance.rooms.count()
        end_time = time.time()
        
        creation_time = end_time - start_time
        
        # Store performance metrics
        cache.set(
            f'room_creation_perf_{instance.id}',
            {
                'room_count': room_count,
                'creation_time': creation_time,
                'timestamp': start_time
            },
            timeout=3600  # 1 hour
        )
        
        # Log slow creations
        if creation_time > 2.0:  # More than 2 seconds
            import logging
            logger = logging.getLogger('performance')
            logger.warning(
                f"Slow room creation detected: {room_count} rooms created in {creation_time:.2f}s "
                f"for room type '{instance.name}'"
            )


# Health check signals
@receiver(post_save, sender=Hostel)
def validate_hostel_health(sender, instance, **kwargs):
    """Validate hostel data health after save"""
    transaction.on_commit(lambda: _validate_hostel_health(instance))


def _validate_hostel_health(hostel):
    """Perform health checks on hostel data"""
    issues = []
    
    # Check if room counts match
    calculated_total = sum(rt.total_rooms for rt in hostel.room_types.all())
    if hostel.total_rooms != calculated_total:
        issues.append(f"Total rooms mismatch: stored={hostel.total_rooms}, calculated={calculated_total}")
    
    # Check price consistency
    room_types = hostel.room_types.all()
    if room_types:
        min_price = min(rt.price_per_person for rt in room_types)
        max_price = max(rt.price_per_person for rt in room_types)
        
        if hostel.min_price != min_price or hostel.max_price != max_price:
            issues.append(f"Price range mismatch: stored=({hostel.min_price}, {hostel.max_price}), calculated=({min_price}, {max_price})")
    
    # Check availability consistency
    actual_available = sum(
        rt.rooms.filter(is_available=True).count() 
        for rt in room_types
    )
    if hostel.available_rooms != actual_available:
        issues.append(f"Available rooms mismatch: stored={hostel.available_rooms}, calculated={actual_available}")
    
    if issues:
        import logging
        logger = logging.getLogger('data_integrity')
        logger.warning(f"Data integrity issues found for hostel '{hostel.name}': {'; '.join(issues)}")
        
        # Auto-fix if configured
        from django.conf import settings
        if getattr(settings, 'AUTO_FIX_DATA_INTEGRITY', False):
            hostel.update_cached_fields()
            logger.info(f"Auto-fixed data integrity issues for hostel '{hostel.name}'")


# Search index update signals (if using search backends like Elasticsearch)
@receiver(post_save, sender=Hostel)
def update_search_index(sender, instance, **kwargs):
    """Update search index when hostel is updated"""
    try:
        # Only update if search backend is configured
        from django.conf import settings
        if hasattr(settings, 'SEARCH_BACKEND') and settings.SEARCH_BACKEND:
            # This would integrate with your search backend
            # For example, with Elasticsearch:
            # from .search import update_hostel_index
            # update_hostel_index(instance)
            pass
    except ImportError:
        # Search backend not configured, skip
        pass


# Notification signals for hostel owners
@receiver(post_save, sender=ContactInquiry)
def notify_hostel_owner_new_inquiry(sender, instance, created, **kwargs):
    """Notify hostel owner of new inquiry"""
    if created:
        # This could send email, SMS, or push notifications
        # For now, we'll just log it
        import logging
        logger = logging.getLogger('notifications')
        logger.info(
            f"New inquiry received for hostel '{instance.hostel.name}' "
            f"from {instance.name} ({instance.email})"
        )


# Rate limiting signals for API protection
@receiver(post_save, sender=ContactInquiry)
def rate_limit_inquiries(sender, instance, created, **kwargs):
    """Implement rate limiting for inquiries"""
    if created:
        from django.core.cache import cache
        
        # Rate limit by email
        email_key = f'inquiry_rate_limit_{instance.email}'
        email_count = cache.get(email_key, 0)
        cache.set(email_key, email_count + 1, timeout=3600)  # 1 hour
        
        # Rate limit by IP (would need to be passed from view)
        # ip_key = f'inquiry_rate_limit_ip_{ip_address}'
        # ip_count = cache.get(ip_key, 0)
        # cache.set(ip_key, ip_count + 1, timeout=3600)
        
        # Log potential abuse
        if email_count > 5:  # More than 5 inquiries per hour
            import logging
            logger = logging.getLogger('security')
            logger.warning(
                f"High inquiry rate detected from email {instance.email}: "
                f"{email_count + 1} inquiries in the last hour"
            )


# Backup trigger signals
# Example placeholder for backup trigger signal
# @receiver(post_save, sender=Hostel)
# def trigger_backup_on_hostel_save(sender, instance, **kwargs):
#     """Trigger backup process when hostel is saved"""
#     # In a real implementation, this might:
#     # 1. Queue a backup job
#     # 2. Call a backup API
#     # 3. Create a database dump
#     pass