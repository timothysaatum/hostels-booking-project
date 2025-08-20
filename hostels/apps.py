from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class HostelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hostels'
    verbose_name = 'Hostel Management System'

    def ready(self):
        """Initialize the app when Django starts"""
        # Import signals to register them
        try:
            import hostels.signals
        except ImportError:
            pass
        
        # Import any additional signal handlers
        try:
            from . import signal_handlers
        except ImportError:
            pass
        
        # Register post-migrate signal for initial data setup
        post_migrate.connect(self.create_initial_data, sender=self)

    def create_initial_data(self, sender, **kwargs):
        """Create initial data after migrations"""
        from django.core.management import call_command
        from django.conf import settings
        
        # Only create initial data in development or if explicitly configured
        
        try:
            self.create_default_amenities()
            self.create_sample_schools()

        except Exception as e:
            import logging
            logger = logging.getLogger('hostel_management')
            logger.error(f"Error creating initial data: {str(e)}")

    def create_default_amenities(self):
        """Create default amenities"""
        from .models import Amenity
        
        default_amenities = [
        # Basic amenities
        ('Water Supply', 'fa fa-tint', 'basic'),
        ('Electricity', 'fa fa-plug', 'basic'),
    ('Security', 'fa fa-shield-alt', 'security'),
    ('Parking', 'fa fa-parking', 'basic'),
    ('Kitchen Access', 'fa fa-utensils', 'basic'),
    ('Fan', 'fa fa-fan', 'basic'),
    ('Wi-Fi / Internet', 'fa fa-wifi', 'basic'),
    ('Waste Disposal', 'fa fa-trash', 'basic'),
    ('Private Toilet', 'fa fa-toilet', 'basic'),
    ('Shower/Bathroom', 'fa fa-bath', 'basic'),

    # Comfort amenities
    ('Air Conditioning', 'fa fa-snowflake', 'comfort'),
    ('Study Room', 'fa fa-book', 'comfort'),
    ('Common Room', 'fa fa-users', 'comfort'),
    ('Laundry Services', 'fa fa-tshirt', 'comfort'),
    ('Balcony', 'fa fa-building', 'comfort'),
    ('TV / Entertainment', 'fa fa-tv', 'comfort'),
    ('Bed & Mattress', 'fa fa-bed', 'comfort'),
    ('Wardrobe/Closet', 'fa fa-archive', 'comfort'),
    ('Refrigerator', 'fa fa-snowflake-o', 'comfort'),
    ('Microwave', 'fa fa-empire', 'comfort'),

    # Study / Academic amenities
    ('Quiet Study Area', 'fa fa-book-reader', 'study'),
    ('Library Access', 'fa fa-university', 'study'),
    ('Desk & Chair', 'fa fa-chair', 'study'),
    ('Printer/Photocopy', 'fa fa-print', 'study'),
    ('Reading Lamp', 'fa fa-lightbulb', 'study'),
    ('Computer Lab Access', 'fa fa-desktop', 'study'),
    ('High-Speed Internet', 'fa fa-ethernet', 'study'),
    ('Power Backup (Generator)', 'fa fa-battery-full', 'study'),
    ('Notice Board / Info Desk', 'fa fa-info-circle', 'study'),
    ('Group Discussion Room', 'fa fa-comments', 'study'),

    # Health & Security amenities
    ('CCTV', 'fa fa-video', 'security'),
    ('Security Guard', 'fa fa-user-shield', 'security'),
    ('Key Card Access', 'fa fa-key', 'security'),
    ('Fire Safety', 'fa fa-fire-extinguisher', 'security'),
    ('Emergency Exit', 'fa fa-door-open', 'security'),
    ('First Aid / Clinic', 'fa fa-briefcase-medical', 'health'),
    ('24/7 Security', 'fa fa-lock', 'security'),
    ('Burglar Proof Windows', 'fa fa-window-maximize', 'security'),
    ('Smoke Detectors', 'fa fa-burn', 'security'),
    ('Emergency Lighting', 'fa fa-lightbulb-o', 'security'),

    # Social & Lifestyle amenities
    ('Gym', 'fa fa-dumbbell', 'lifestyle'),
    ('Restaurant / Canteen', 'fa fa-utensil-spoon', 'lifestyle'),
    ('Conference Room', 'fa fa-chalkboard-teacher', 'lifestyle'),
    ('Game Room', 'fa fa-gamepad', 'lifestyle'),
    ('Swimming Pool', 'fa fa-swimming-pool', 'lifestyle'),
    ('Outdoor Sitting Area', 'fa fa-tree', 'lifestyle'),
    ('Sports Court (Basketball/Football)', 'fa fa-futbol', 'lifestyle'),
    ('Bicycle Rack', 'fa fa-bicycle', 'lifestyle'),
    ('Mini Mart / Shop', 'fa fa-shopping-basket', 'lifestyle'),
    ('Transport Shuttle Service', 'fa fa-bus', 'lifestyle'),
]

        
        created_count = 0
        for name, icon, category in default_amenities:
            amenity, created = Amenity.objects.get_or_create(
                name=name,
                defaults={
                    'icon_class': icon,
                    'category': category,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            import logging
            logger = logging.getLogger('hostel_management')
            logger.info(f"Created {created_count} default amenities")

    def create_sample_schools(self):
        """Create sample schools for development"""
        from .models import School
        
        sample_schools = [
            # Ghana universities with approximate coordinates
            ('University of Ghana', 'Legon', 'Greater Accra', 5.6506, -0.1887),
            ('Kwame Nkrumah University of Science and Technology', 'Kumasi', 'Ashanti', 6.6745, -1.5716),
            ('University of Cape Coast', 'Cape Coast', 'Central', 5.1053, -1.2789),
            ('Ghana Institute of Management and Public Administration', 'Accra', 'Greater Accra', 5.6037, -0.1870),
            ('Ashesi University', 'Berekuso', 'Eastern', 5.7789, -0.1709),
            ('University for Development Studies', 'Tamale', 'Northern', 9.391366511977152, -0.8867169628934316),
            ('University of Professional Studies', 'Accra', 'Greater Accra', 5.5600, -0.2057),
            ('Regent University College of Science and Technology', 'Accra', 'Greater Accra', 5.6108, -0.1821),
        ]
        
        created_count = 0
        for name, city, region, lat, lon in sample_schools:
            school, created = School.objects.get_or_create(
                name=name,
                city=city,
                defaults={
                    'region': region,
                    'latitude': lat,
                    'longitude': lon,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            import logging
            logger = logging.getLogger('hostel_management')
            logger.info(f"Created {created_count} sample schools")


# Additional signal handlers for specific business logic
@receiver(post_migrate)
def setup_logging_configuration(sender, **kwargs):
    """Setup logging configuration for the hostel app"""
    if sender.name == 'hostels':
        import logging
        from django.conf import settings
        
        # Create hostel-specific loggers
        loggers = [
            'hostel_management',
            'hostel_audit',
            'performance', 
            'data_integrity',
            'notifications',
            'security'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            
            # Set appropriate log levels
            if settings.DEBUG:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)


@receiver(post_migrate)
def setup_cache_configuration(sender, **kwargs):
    """Setup cache keys and initial cache data"""
    if sender.name == 'hostels':
        from django.core.cache import cache
        
        # Initialize cache with default values
        cache_defaults = {
            'hostel_stats': {},
            'search_filters': {
                'price_ranges': [(0, 1000), (1000, 2000), (2000, 5000), (5000, 10000)],
                'popular_amenities': [],
            },
            'system_status': 'operational'
        }
        
        for key, default_value in cache_defaults.items():
            if not cache.get(key):
                cache.set(key, default_value, timeout=3600)


@receiver(post_migrate) 
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks for maintenance"""
    if sender.name == 'hostels':
        try:
            # If using Celery, you could register periodic tasks here
            # from celery import current_app
            # current_app.conf.beat_schedule.update({
            #     'update-hostel-cache': {
            #         'task': 'hostels.tasks.update_all_hostel_caches',
            #         'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
            #     },
            #     'cleanup-stale-inquiries': {
            #         'task': 'hostels.tasks.cleanup_stale_inquiries', 
            #         'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
            #     },
            # })
            pass
        except ImportError:
            # Celery not installed, skip periodic task setup
            pass


@receiver(post_migrate)
def validate_configuration(sender, **kwargs):
    """Validate app configuration after migration"""
    if sender.name == 'hostels':
        from django.conf import settings
        import logging
        
        logger = logging.getLogger('hostel_management')
        
        # Check required settings
        required_settings = [
            'DEFAULT_FILE_STORAGE',
            'MEDIA_URL',
            'MEDIA_ROOT',
        ]
        
        missing_settings = []
        for setting_name in required_settings:
            if not hasattr(settings, setting_name):
                missing_settings.append(setting_name)
        
        if missing_settings:
            logger.warning(
                f"Missing recommended settings for hostel app: {', '.join(missing_settings)}"
            )
        
        # Check Cloudinary configuration if used
        if hasattr(settings, 'CLOUDINARY_STORAGE'):
            try:
                import cloudinary
                logger.info("Cloudinary storage configured successfully")
            except ImportError:
                logger.error("Cloudinary storage configured but cloudinary package not installed")
        
        # Validate database indexes
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_indexes 
                    WHERE tablename LIKE 'hostels_%'
                """) if connection.vendor == 'postgresql' else None
                
                if connection.vendor == 'postgresql':
                    result = cursor.fetchone()
                    if result and result[0] > 0:
                        logger.info(f"Database indexes created successfully: {result[0]} indexes")
        except Exception as e:
            logger.debug(f"Could not validate database indexes: {str(e)}")
        
        logger.info("Hostel app configuration validation completed")


# Health check utilities
def get_app_health():
    """Get health status of the hostel app"""
    from django.db import connection
    from django.core.cache import cache
    from .models import Hostel, School, RoomType
    from django.utils import timezone
    
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'components': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            health_data['components']['database'] = {
                'status': 'healthy' if result and result[0] == 1 else 'unhealthy',
                'response_time_ms': 0  # Could measure actual response time
            }
    except Exception as e:
        health_data['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    # Check cache connectivity
    try:
        test_key = 'health_check_test'
        cache.set(test_key, 'test_value', timeout=60)
        cached_value = cache.get(test_key)
        cache.delete(test_key)
        
        health_data['components']['cache'] = {
            'status': 'healthy' if cached_value == 'test_value' else 'unhealthy'
        }
    except Exception as e:
        health_data['components']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    # Check data consistency
    try:
        hostel_count = Hostel.objects.count()
        school_count = School.objects.count()
        roomtype_count = RoomType.objects.count()
        
        health_data['components']['data'] = {
            'status': 'healthy',
            'counts': {
                'hostels': hostel_count,
                'schools': school_count,
                'room_types': roomtype_count
            }
        }
    except Exception as e:
        health_data['components']['data'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    return health_data