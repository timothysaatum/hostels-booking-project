from django.urls import reverse
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models import Count, Q, Sum, F
from django.utils.text import slugify
import random
import string
from math import radians, cos, sin, asin, sqrt
from cloudinary_storage.storage import MediaCloudinaryStorage

User = get_user_model()


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    try:
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return round(c * r, 2)
    except (ValueError, TypeError):
        return None


class BaseTimestampModel(models.Model):
    """Base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """Manager for active objects only"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class School(BaseTimestampModel):
    """Model for educational institutions"""
    name = models.CharField(max_length=200, unique=True, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=100, db_index=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    # Managers
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'city']),
            models.Index(fields=['region', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"

    @property
    def coordinates(self):
        if self.latitude and self.longitude:
            return f"{self.latitude},{self.longitude}"
        return None


class Amenity(BaseTimestampModel):
    """Model for hostel amenities"""
    CATEGORY_CHOICES = [
        ('basic', 'Basic'),
        ('comfort', 'Comfort'),
        ('luxury', 'Luxury'),
        ('security', 'Security'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=100, default='fa fa-check')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='basic')
    is_active = models.BooleanField(default=True, db_index=True)

    # Managers
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        verbose_name_plural = 'Amenities'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class HostelQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def featured(self):
        return self.filter(is_featured=True, is_active=True)

    def by_school(self, school_id):
        return self.filter(school_id=school_id, is_active=True)

    def with_available_rooms(self):
        return self.filter(room_types__rooms__is_available=True, is_active=True).distinct()

    def with_stats(self):
        return self.annotate(
            total_room_count=Count('room_types__rooms'),
            available_room_count=Count(
                'room_types__rooms',
                filter=Q(room_types__rooms__is_available=True)
            ),
            available_spots_count=Sum(
                F('room_types__rooms__capacity') - F('room_types__rooms__current_occupants'),
                filter=Q(room_types__rooms__is_available=True)
            ),
            inquiry_count=Count('inquiries'),
        )

    def with_distance_to_school(self):
        """Annotate hostels with distance to their school"""
        return self.select_related('school').extra(
            select={
                'distance_to_school': """
                    CASE 
                        WHEN hostels_hostel.latitude IS NOT NULL 
                        AND hostels_hostel.longitude IS NOT NULL 
                        AND hostels_school.latitude IS NOT NULL 
                        AND hostels_school.longitude IS NOT NULL 
                        THEN 
                            6371 * acos(
                                cos(radians(hostels_school.latitude)) 
                                * cos(radians(hostels_hostel.latitude)) 
                                * cos(radians(hostels_hostel.longitude) - radians(hostels_school.longitude)) 
                                + sin(radians(hostels_school.latitude)) 
                                * sin(radians(hostels_hostel.latitude))
                            )
                        ELSE NULL
                    END
                """
            }
        )

    def search(self, query):
        if not query:
            return self
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(school__name__icontains=query) |
            Q(address__icontains=query) |
            Q(campus__icontains=query)
        )


class HostelManager(models.Manager):
    def get_queryset(self):
        return HostelQuerySet(self.model, using=self._db) \
            .select_related('school', 'owner') \
            .prefetch_related('amenities', 'images')

    def active(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def with_available_rooms(self):
        return self.get_queryset().with_available_rooms()

    def with_stats(self):
        return self.get_queryset().with_stats()

    def with_distance_to_school(self):
        return self.get_queryset().with_distance_to_school()


class Hostel(BaseTimestampModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_hostels')
    owner_name = models.CharField(max_length=200)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='hostels')
    campus = models.CharField(max_length=200, default='Main Campus')
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = CKEditor5Field(config_name='advanced')

    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    latitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)

    address = models.TextField()

    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=100, blank=True)

    main_image = models.ImageField(upload_to='hostels/', storage=MediaCloudinaryStorage(), blank=True, null=True)

    total_rooms = models.PositiveIntegerField(default=0, db_index=True)
    available_rooms = models.PositiveIntegerField(default=0, db_index=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    rating_count = models.PositiveIntegerField(default=0)

    amenities = models.ManyToManyField('Amenity', blank=True)
    has_wifi = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    objects = HostelManager()
    active = HostelManager()

    def __str__(self):
        return f'{self.name} - {self.school}'

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['school', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['min_price', 'max_price']),
            models.Index(fields=['has_wifi', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.school.name}")
            self.slug = self._generate_unique_slug(base_slug)

        if not self.meta_title:
            self.meta_title = f"{self.name} - Student Hostel in {self.school.city}"

        if not self.meta_description:
            self.meta_description = f"Book affordable student accommodation at {self.name} near {self.school.name}."

        super().save(*args, **kwargs)

        if self.main_image:
            self._resize_cloudinary_image()

    def _resize_cloudinary_image(self):
        """Resize image using Cloudinary transformations instead of PIL"""
        try:
            if self.main_image:
                pass
        except Exception as e:
            print(f"Error processing image: {e}")

    def _generate_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        while Hostel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug


    def update_cached_fields(self):
        total_rooms = Room.objects.filter(room_type__hostel=self).count()
        available_rooms = Room.objects.filter(room_type__hostel=self, is_available=True).count()
        prices = RoomType.objects.filter(hostel=self).values_list('price_per_person', flat=True)

        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # Update directly in DB to avoid stale .save() issues
        Hostel.objects.filter(pk=self.pk).update(
            total_rooms=total_rooms,
            available_rooms=available_rooms,
            min_price=min_price,
            max_price=max_price,
        )

        # Optionally refresh the current instance so it's in sync
        self.refresh_from_db(fields=['total_rooms', 'available_rooms', 'min_price', 'max_price'])

    @property
    def price_range_display(self):
        if self.min_price == self.max_price:
            return f"GH₵{self.min_price:,.0f}"
        return f"GH₵{self.min_price:,.0f} - GH₵{self.max_price:,.0f}"

    @property
    def distance_to_school(self):
        """Calculate distance to school if coordinates are available"""
        if (self.latitude and self.longitude and 
            self.school.latitude and self.school.longitude):
            distance = calculate_distance(
                self.school.latitude, self.school.longitude,
                self.latitude, self.longitude
            )

            minutes_walk = round((distance * 1000) / 100)  # Assume walking is 80% of driving distance
            return minutes_walk
        return None

    @property
    def main_image_thumbnail(self):
        """Get resized image URL using Cloudinary transformations"""
        if self.main_image:
            base_url = self.main_image.url
            if 'cloudinary.com' in base_url:
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    return f"{parts[0]}/upload/w_1200,h_800,c_fill,q_85/{parts[1]}"
            return self.main_image.url
        return '/static/images/placeholder-hostel.jpg'


class RoomType(BaseTimestampModel):
    """Room type model with auto room creation"""
    
    ROOM_TYPE_CHOICES = [
        ('single', '1 Bed per Room'),
        ('double', '2 Beds per Room'),
        ('triple', '3 Beds per Room'),
        ('quad', '4 Beds per Room'),
        ('custom', 'Custom'),
    ]
    
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, db_index=True)
    beds_per_room = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        db_index=True
    )
    total_rooms = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    description = CKEditor5Field(config_name='advanced', blank=True)
    main_image = models.ImageField(upload_to='room_types/main/', storage=MediaCloudinaryStorage(), blank=True, null=True)
    
    # Cached availability (updated via signals)
    available_rooms_count = models.PositiveIntegerField(default=0, db_index=True)
    
    # Features
    has_private_bathroom = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_study_desk = models.BooleanField(default=False)
    has_wardrobe = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['beds_per_room', 'price_per_person']
        unique_together = ['hostel', 'room_type', 'beds_per_room']
        indexes = [
            models.Index(fields=['hostel', 'room_type']),
            models.Index(fields=['price_per_person']),
            models.Index(fields=['available_rooms_count']),
        ]

    def __str__(self):
        return f"{self.hostel.name} - {self.get_room_type_display()}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            self._create_rooms()

        self.hostel.update_cached_fields()


    def _create_rooms(self):
        """Create individual rooms for this room type"""

        existing_rooms = self.rooms.count()
        if existing_rooms >= self.total_rooms:
            print(f"Skipping room creation: already {existing_rooms} rooms exist for {self}")
            return

        rooms_to_create = []
        existing_room_numbers = set(
            Room.objects.filter(room_type__hostel=self.hostel)
            .values_list('room_number', flat=True)
        )

        for i in range(self.total_rooms - existing_rooms):
            print(f'Room {i+1} of {self.total_rooms - existing_rooms} for {self.hostel.name}')
            room_number = self._generate_room_number(existing_room_numbers)
            existing_room_numbers.add(room_number)
            floor_number = self._get_floor_from_room_number(room_number)

            rooms_to_create.append(
                Room(
                    room_type=self,
                    room_number=room_number,
                    floor_number=floor_number,
                    capacity=self.beds_per_room,
                    current_occupants=0,
                    occupant_gender='mixed',
                    is_available=True,
                    is_active=True
                )
            )

        Room.objects.bulk_create(rooms_to_create, batch_size=100)

        # Update availability count directly
        self.available_rooms_count = self.rooms.filter(is_available=True).count()
        RoomType.objects.filter(pk=self.pk).update(
            available_rooms_count=self.available_rooms_count
        )


    def _generate_room_number(self, existing_numbers):
        """Generate a unique room number"""
        # Try different patterns for room numbering
        patterns = [
            lambda i: f"{self.room_type[0].upper()}{i+1:03d}",  # A001, D001, etc.
            lambda i: f"{i+1:03d}",  # 001, 002, etc.
            lambda i: f"{random.choice(string.ascii_uppercase)}{i+1:02d}",  # A01, B01, etc.
        ]
        
        for pattern in patterns:
            for i in range(1000):  # Try up to 1000 combinations
                room_number = pattern(i)
                if room_number not in existing_numbers:
                    return room_number
        
        # Fallback to timestamp-based unique number
        import time
        return f"R{int(time.time() * 1000) % 100000:05d}"

    def _get_floor_from_room_number(self, room_number):
        """Extract floor number from room number or generate one"""
        # Extract digits from room number
        digits = ''.join(filter(str.isdigit, room_number))
        if digits:
            # Use first digit as floor, default to 1
            return max(1, int(digits[0]) if digits[0] != '0' else 1)
        return 1

    @property
    def total_capacity(self):
        """Total capacity for this room type"""
        return self.total_rooms * self.beds_per_room

    @property
    def main_image_url(self):
        """Get main image URL with Cloudinary transformations"""
        if self.main_image:
            base_url = self.main_image.url
            if 'cloudinary.com' in base_url:
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    return f"{parts[0]}/upload/w_800,h_600,c_fill,q_85/{parts[1]}"
            return self.main_image.url
        return '/static/images/placeholder-room.jpg'

    @property
    def feature_list(self):
        """Get list of features for this room type"""
        features = []
        if self.has_private_bathroom:
            features.append(('Private Bathroom', 'fa-bath'))
        if self.has_balcony:
            features.append(('Balcony', 'fa-building'))
        if self.has_ac:
            features.append(('Air Conditioning', 'fa-snowflake'))
        if self.has_study_desk:
            features.append(('Study Desk', 'fa-desk'))
        if self.has_wardrobe:
            features.append(('Wardrobe', 'fa-closet'))
        return features

    def get_available_rooms(self):
        """Get available rooms for this room type"""
        return self.rooms.filter(is_available=True)

    def get_absolute_url(self):
        return reverse('hostels:roomtype-detail', kwargs={'pk': self.pk})


class HostelImage(BaseTimestampModel):
    """Images for hostels"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hostels/gallery/', storage=MediaCloudinaryStorage())
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['hostel', 'order']),
        ]

    def __str__(self):
        return f"{self.hostel.name} - Image {self.id}"

    @property
    def image_thumbnail(self):
        """Get thumbnail URL using Cloudinary transformations"""
        if self.image:
            base_url = self.image.url
            if 'cloudinary.com' in base_url:
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    return f"{parts[0]}/upload/w_400,h_300,c_fill,q_85/{parts[1]}"
            return self.image.url
        return '/static/images/placeholder.jpg'


class RoomTypeImage(BaseTimestampModel):
    """Images for room types"""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_types/gallery/', storage=MediaCloudinaryStorage())
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['room_type', 'order']),
        ]

    def __str__(self):
        return f"{self.room_type} - Image {self.id}"

    @property
    def image_thumbnail(self):
        """Get thumbnail URL using Cloudinary transformations"""
        if self.image:
            base_url = self.image.url
            if 'cloudinary.com' in base_url:
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    return f"{parts[0]}/upload/w_400,h_300,c_fill,q_85/{parts[1]}"
            return self.image.url
        return '/static/images/placeholder.jpg'


class RoomQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True, is_active=True)

    def filter_by_gender(self, gender):
        return self.filter(occupant_gender=gender)

    def by_floor(self, floor_number):
        return self.filter(floor_number=floor_number)


class Room(BaseTimestampModel):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('mixed', 'Mixed'),
    ]
    
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor_number = models.PositiveIntegerField(default=1, db_index=True)
    capacity = models.PositiveIntegerField()
    current_occupants = models.PositiveIntegerField(default=0)
    occupant_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='mixed', db_index=True)
    is_available = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    objects = RoomQuerySet.as_manager()

    class Meta:
        ordering = ['floor_number', 'room_number']
        unique_together = ['room_type', 'room_number']
        indexes = [
            models.Index(fields=['room_type', 'is_available']),
            models.Index(fields=['is_available', 'is_active']),
            models.Index(fields=['floor_number']),
            models.Index(fields=['occupant_gender']),
        ]

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.hostel.name}"

    def save(self, *args, **kwargs):
        # Validate occupancy before saving
        self.clean()
        super().save(*args, **kwargs)
        
        # Update room type availability cache
        self._update_room_type_cache()
        
        # Update hostel cache
        self.room_type.hostel.update_cached_fields()

    def _update_room_type_cache(self):
        """Update room type availability cache"""
        available_count = self.room_type.rooms.filter(is_available=True).count()
        self.room_type.available_rooms_count = available_count
        self.room_type.save(update_fields=['available_rooms_count'])

    def clean(self):
        if self.current_occupants > self.capacity:
            raise ValidationError("Current occupants cannot exceed room capacity")
        
        # Update availability based on occupancy
        self.is_available = self.current_occupants < self.capacity

    @property
    def is_full(self):
        """Check if room is at full capacity"""
        return self.current_occupants >= self.capacity

    @property
    def available_spots(self):
        """Number of available spots in the room"""
        return max(0, self.capacity - self.current_occupants)

    @property
    def occupancy_percentage(self):
        """Occupancy percentage"""
        if self.capacity == 0:
            return 0
        return (self.current_occupants / self.capacity) * 100

    def get_absolute_url(self):
        return reverse('hostels:room-detail', kwargs={'pk': self.pk})


class ContactInquiry(BaseTimestampModel):
    """Model to track user inquiries for hostels"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]
    
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    
    # Contact Information
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=15)
    
    # Student Information
    student_id = models.CharField(max_length=50, blank=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Inquiry Details
    room_type_interest = models.ForeignKey(
        RoomType, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='inquiries'
    )
    number_of_occupants = models.PositiveIntegerField(default=1)
    preferred_move_in_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    is_contacted = models.BooleanField(default=False, db_index=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    contacted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='contacted_inquiries'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Inquiries'
        indexes = [
            models.Index(fields=['hostel', 'status']),
            models.Index(fields=['is_contacted', 'created_at']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"Inquiry from {self.name} for {self.hostel.name}"

    def mark_as_contacted(self, user=None):
        """Mark inquiry as contacted"""
        self.is_contacted = True
        self.status = 'contacted'
        self.contacted_at = timezone.now()
        if user:
            self.contacted_by = user
        self.save(update_fields=['is_contacted', 'status', 'contacted_at', 'contacted_by'])