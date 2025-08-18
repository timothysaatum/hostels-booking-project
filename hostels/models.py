# from django.urls import reverse
# from django.db import models
# from django.utils import timezone
# from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.core.exceptions import ValidationError
# from django_ckeditor_5.fields import CKEditor5Field
# from PIL import Image
# from django.db.models import Avg, Count, Q, Sum, F
# from django.utils.text import slugify
# from io import BytesIO
# import os
# from cloudinary_storage.storage import MediaCloudinaryStorage
# User = get_user_model()


# class BaseTimestampModel(models.Model):
#     """Base model with timestamp fields"""
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True


# class ActiveManager(models.Manager):
#     """Manager for active objects only"""
#     def get_queryset(self):
#         return super().get_queryset().filter(is_active=True)


# class School(BaseTimestampModel):
#     """Model for educational institutions"""
#     name = models.CharField(max_length=200, unique=True, db_index=True)
#     city = models.CharField(max_length=100, db_index=True)
#     region = models.CharField(max_length=100, db_index=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     is_active = models.BooleanField(default=True)

#     # Managers
#     objects = models.Manager()
#     active = ActiveManager()

#     class Meta:
#         ordering = ['name']
#         indexes = [
#             models.Index(fields=['name', 'city']),
#             models.Index(fields=['region', 'is_active']),
#         ]

#     def __str__(self):
#         return f"{self.name} - {self.city}"

#     @property
#     def coordinates(self):
#         if self.latitude and self.longitude:
#             return f"{self.latitude},{self.longitude}"
#         return None


# class Amenity(BaseTimestampModel):
#     """Model for hostel amenities"""
#     CATEGORY_CHOICES = [
#         ('basic', 'Basic'),
#         ('comfort', 'Comfort'),
#         ('luxury', 'Luxury'),
#         ('security', 'Security'),
#     ]
    
#     name = models.CharField(max_length=100, unique=True)
#     icon_class = models.CharField(max_length=100, default='fa fa-check')
#     category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='basic')
#     is_active = models.BooleanField(default=True, db_index=True)

#     # Managers
#     objects = models.Manager()
#     active = ActiveManager()

#     class Meta:
#         verbose_name_plural = 'Amenities'
#         ordering = ['category', 'name']

#     def __str__(self):
#         return self.name

# class HostelQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_active=True)

#     def featured(self):
#         return self.filter(is_featured=True, is_active=True)

#     def by_school(self, school_id):
#         return self.filter(school_id=school_id, is_active=True)

#     def with_available_rooms(self):
#         return self.filter(room_types__rooms__is_available=True, is_active=True).distinct()

#     def with_stats(self):
#         return self.annotate(
#             total_room_count=Count('room_types__rooms'),
#             available_room_count=Sum(
#                 F('room_types__rooms__capacity') - F('room_types__rooms__current_occupants'),
#                 filter=Q(room_types__rooms__is_available=True)
#             ),
#             inquiry_count=Count('inquiries'),
#             # avg_rating=Avg('reviews__rating')
#         )

#     def search(self, query):
#         if not query:
#             return self
#         return self.filter(
#             Q(name__icontains=query) |
#             Q(description__icontains=query) |
#             Q(school__name__icontains=query) |
#             Q(address__icontains=query) |
#             Q(campus__icontains=query)
#         )


# class HostelManager(models.Manager):
#     def get_queryset(self):
#         return HostelQuerySet(self.model, using=self._db) \
#             .select_related('school', 'owner') \
#             .prefetch_related('amenities', 'images')

#     def active(self):
#         return self.get_queryset().active()

#     def featured(self):
#         return self.get_queryset().featured()

#     def with_available_rooms(self):
#         return self.get_queryset().with_available_rooms()

#     def with_stats(self):
#         return self.get_queryset().with_stats()


# class Hostel(BaseTimestampModel):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_hostels')
#     owner_name = models.CharField(max_length=200)
#     school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='hostels')
#     campus = models.CharField(max_length=200, default='Main Campus')
#     name = models.CharField(max_length=200, db_index=True)
#     slug = models.SlugField(max_length=220, unique=True, blank=True)
#     description = CKEditor5Field(config_name='advanced')

#     phone_number = models.CharField(max_length=15)
#     email = models.EmailField(blank=True)

#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     address = models.TextField()

#     account_number = models.CharField(max_length=20, blank=True)
#     account_name = models.CharField(max_length=200)
#     bank_name = models.CharField(max_length=100, blank=True)

#     main_image = models.ImageField(upload_to='hostels/', storage=MediaCloudinaryStorage(), blank=True, null=True)

#     total_rooms = models.PositiveIntegerField(default=0, db_index=True)
#     available_rooms = models.PositiveIntegerField(default=0, db_index=True)
#     min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)
#     max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_index=True)

#     rating = models.DecimalField(max_digits=3, decimal_places=2, default=0,
#                                  validators=[MinValueValidator(0), MaxValueValidator(5)])
#     rating_count = models.PositiveIntegerField(default=0)

#     amenities = models.ManyToManyField('Amenity', blank=True)
#     has_wifi = models.BooleanField(default=False, db_index=True)
#     is_featured = models.BooleanField(default=False, db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)

#     meta_title = models.CharField(max_length=60, blank=True)
#     meta_description = models.CharField(max_length=160, blank=True)

#     objects = HostelManager()
#     active = HostelManager()

#     class Meta:
#         ordering = ['-is_featured', '-created_at']
#         indexes = [
#             models.Index(fields=['school', 'is_active']),
#             models.Index(fields=['is_featured', 'is_active']),
#             models.Index(fields=['min_price', 'max_price']),
#             models.Index(fields=['has_wifi', 'is_active']),
#             models.Index(fields=['created_at']),
#             models.Index(fields=['slug']),
#         ]

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base_slug = slugify(f"{self.name}-{self.school.name}")
#             self.slug = self._generate_unique_slug(base_slug)
#         if not self.meta_title:
#             self.meta_title = f"{self.name} - Student Hostel in {self.school.city}"
#         if not self.meta_description:
#             self.meta_description = f"Book affordable student accommodation at {self.name} near {self.school.name}."
#         super().save(*args, **kwargs)
#         if self.main_image and self.main_image.storage.exists(self.main_image.name):
#             self._resize_image(self.main_image, (1200, 800))

#     def _generate_unique_slug(self, base_slug):
#         slug = base_slug
#         counter = 1
#         while Hostel.objects.filter(slug=slug).exists():
#             slug = f"{base_slug}-{counter}"
#             counter += 1
#         return slug

#     def _resize_image(self, image_field, size):
#         try:
#             img = Image.open(image_field)
#             img.thumbnail(size, Image.Resampling.LANCZOS)
#             buffer = BytesIO()
#             img.save(buffer, format='JPEG', optimize=True, quality=85)
#             image_field.file = buffer
#         except Exception:
#             pass

#     def update_cached_fields(self):
#         room_stats = self.room_types.aggregate(
#             total=Sum('total_rooms'),
#             available=Sum(
#                 F('rooms__capacity') - F('rooms__current_occupants'),
#                 filter=Q(rooms__is_available=True)
#             )
#         )
#         price_stats = self.room_types.aggregate(
#             min_price=models.Min('price_per_person'),
#             max_price=models.Max('price_per_person')
#         )
#         self.total_rooms = room_stats['total'] or 0
#         self.available_rooms = room_stats['available'] or 0
#         self.min_price = price_stats['min_price'] or 0
#         self.max_price = price_stats['max_price'] or 0
#         self.save(update_fields=['total_rooms', 'available_rooms', 'min_price', 'max_price'])

#     @property
#     def price_range_display(self):
#         if self.min_price == self.max_price:
#             return f"GH₵{self.min_price:,.0f}"
#         return f"GH₵{self.min_price:,.0f} - GH₵{self.max_price:,.0f}"


# class RoomType(BaseTimestampModel):
#     """Room type model with better structure"""
    
#     ROOM_TYPE_CHOICES = [
#         ('single', '1 Bed per Room'),
#         ('double', '2 Beds per Room'),
#         ('triple', '3 Beds per Room'),
#         ('quad', '4 Beds per Room'),
#         ('custom', 'Custom'),
#     ]
    
#     hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='room_types')
#     name = models.CharField(max_length=100)
#     room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, db_index=True)
#     beds_per_room = models.PositiveIntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(8)],
#         db_index=True
#     )
#     total_rooms = models.PositiveIntegerField(validators=[MinValueValidator(1)])
#     price_per_person = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
#     description = CKEditor5Field(config_name='advanced', blank=True)
#     main_image = models.ImageField(upload_to='room_types/main/', storage=MediaCloudinaryStorage(), blank=True, null=True)
    
#     # Cached availability (updated via signals)
#     available_rooms_count = models.PositiveIntegerField(default=0, db_index=True)
    
#     # Features
#     has_private_bathroom = models.BooleanField(default=False)
#     has_balcony = models.BooleanField(default=False)
#     has_ac = models.BooleanField(default=False)
#     has_study_desk = models.BooleanField(default=False)
#     has_wardrobe = models.BooleanField(default=False)
    
#     class Meta:
#         ordering = ['beds_per_room', 'price_per_person']
#         unique_together = ['hostel', 'room_type', 'beds_per_room']
#         indexes = [
#             models.Index(fields=['hostel', 'room_type']),
#             models.Index(fields=['price_per_person']),
#             models.Index(fields=['available_rooms_count']),
#         ]

#     def __str__(self):
#         return f"{self.hostel.name} - {self.get_room_type_display()}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
        
#         # Update hostel cached fields
#         self.hostel.update_cached_fields()
        
#         # Resize image if it exists
#         if self.main_image and os.path.exists(self.main_image.url):
#             self._resize_image(self.main_image.url, (800, 600))

#     def _resize_image(self, image_path, size):
#         """Resize image to specified size"""
#         try:
#             with Image.open(image_path) as img:
#                 img.thumbnail(size, Image.Resampling.LANCZOS)
#                 img.save(image_path, optimize=True, quality=85)
#         except Exception:
#             pass

#     @property
#     def total_capacity(self):
#         """Total capacity for this room type"""
#         return self.total_rooms * self.beds_per_room

#     @property
#     def main_image_url(self):
#         """Get main image URL or placeholder"""
#         if self.main_image:
#             return self.main_image.url
#         return '/static/images/placeholder-room.jpg'

#     @property
#     def feature_list(self):
#         """Get list of features for this room type"""
#         features = []
#         if self.has_private_bathroom:
#             features.append(('Private Bathroom', 'fa-bath'))
#         if self.has_balcony:
#             features.append(('Balcony', 'fa-building'))
#         if self.has_ac:
#             features.append(('Air Conditioning', 'fa-snowflake'))
#         if self.has_study_desk:
#             features.append(('Study Desk', 'fa-desk'))
#         if self.has_wardrobe:
#             features.append(('Wardrobe', 'fa-closet'))
#         return features

#     def get_available_rooms(self):
#         """Get available rooms for this room type"""
#         return self.rooms.filter(is_available=True)

#     def get_absolute_url(self):
#         return reverse('hostels:roomtype-detail', kwargs={'pk': self.pk})

# class HostelImage(BaseTimestampModel):
#     """Images for hostels"""
#     hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='hostels/gallery/', storage=MediaCloudinaryStorage())
#     caption = models.CharField(max_length=200, blank=True)
#     order = models.PositiveIntegerField(default=0, db_index=True)

#     class Meta:
#         ordering = ['order', 'created_at']
#         indexes = [
#             models.Index(fields=['hostel', 'order']),
#         ]

#     def __str__(self):
#         return f"{self.hostel.name} - Image {self.id}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if self.image and self.image.storage.exists(self.image.name):  # S3-safe
#             self._resize_image(self.image, (1200, 800))

#     def _resize_image(self, image_field, size):
#         """Resize image to specified size (S3-safe)"""
#         try:
#             img = Image.open(image_field)
#             img.thumbnail(size, Image.Resampling.LANCZOS)
#             buffer = BytesIO()
#             img.save(buffer, format='JPEG', optimize=True, quality=85)
#             image_field.file = buffer
#         except Exception:
#             pass


# class RoomTypeImage(BaseTimestampModel):
#     """Images for room types"""
#     room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
#     image = models.ImageField(upload_to='room_types/gallery/', storage=MediaCloudinaryStorage())
#     caption = models.CharField(max_length=200, blank=True)
#     order = models.PositiveIntegerField(default=0, db_index=True)

#     class Meta:
#         ordering = ['order', 'created_at']
#         indexes = [
#             models.Index(fields=['room_type', 'order']),
#         ]

#     def __str__(self):
#         return f"{self.room_type} - Image {self.id}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if self.image and self.image.storage.exists(self.image.name):  # S3-safe
#             self._resize_image(self.image, (1200, 800))

#     def _resize_image(self, image_field, size):
#         """Resize image to specified size (S3-safe)"""
#         try:
#             img = Image.open(image_field)
#             img.thumbnail(size, Image.Resampling.LANCZOS)
#             buffer = BytesIO()
#             img.save(buffer, format='JPEG', optimize=True, quality=85)
#             image_field.file = buffer
#         except Exception:
#             pass


# class RoomQuerySet(models.QuerySet):
#     def filter_by_gender(self, gender):
#         return self.filter(occupant_gender=gender)


# class Room(BaseTimestampModel):
#     GENDER_CHOICES = [
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('mixed', 'Mixed'),
#     ]
#     room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE, related_name='rooms')
#     room_number = models.CharField(max_length=20)
#     floor_number = models.PositiveIntegerField(default=1, db_index=True)
#     capacity = models.PositiveIntegerField()
#     current_occupants = models.PositiveIntegerField(default=0)
#     occupant_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='mixed', db_index=True)
#     is_available = models.BooleanField(default=True, db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#     notes = models.TextField(blank=True)

#     objects = RoomQuerySet.as_manager()

#     class Meta:
#         ordering = ['floor_number', 'room_number']
#         unique_together = ['room_type', 'room_number']
#         indexes = [
#             models.Index(fields=['room_type', 'is_available']),
#             models.Index(fields=['is_available', 'is_active']),
#             models.Index(fields=['floor_number']),
#             models.Index(fields=['occupant_gender']),
#         ]

#     def __str__(self):
#         return f"Room {self.room_number} - {self.room_type.hostel.name}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # Update room type availability cache
#         self.room_type.available_rooms_count = self.room_type.rooms.filter(
#             is_available=True
#         ).count()
#         self.room_type.save(update_fields=['available_rooms_count'])

#     def clean(self):
#         if self.current_occupants > self.capacity:
#             raise ValidationError("Current occupants cannot exceed room capacity")

#     @property
#     def is_full(self):
#         """Check if room is at full capacity"""
#         return self.current_occupants >= self.capacity

#     @property
#     def available_spots(self):
#         """Number of available spots in the room"""
#         return max(0, self.capacity - self.current_occupants)

#     def get_absolute_url(self):
#         return reverse('hostels:room-detail', kwargs={'pk': self.pk})


# class ContactInquiry(BaseTimestampModel):
#     """Model to track user inquiries for hostels"""
#     STATUS_CHOICES = [
#         ('new', 'New'),
#         ('contacted', 'Contacted'),
#         ('converted', 'Converted'),
#         ('closed', 'Closed'),
#     ]
    
#     hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='inquiries')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    
#     # Contact Information
#     name = models.CharField(max_length=200, db_index=True)
#     email = models.EmailField(db_index=True)
#     phone_number = models.CharField(max_length=15)
    
#     # Student Information
#     student_id = models.CharField(max_length=50, blank=True)
#     school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    
#     # Inquiry Details
#     room_type_interest = models.ForeignKey(
#         RoomType, on_delete=models.SET_NULL, 
#         null=True, blank=True,
#         related_name='inquiries'
#     )
#     number_of_occupants = models.PositiveIntegerField(default=1)
#     preferred_move_in_date = models.DateField(null=True, blank=True)
#     message = models.TextField(blank=True)
    
#     # Status
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
#     is_contacted = models.BooleanField(default=False, db_index=True)
#     contacted_at = models.DateTimeField(null=True, blank=True)
#     contacted_by = models.ForeignKey(
#         User, on_delete=models.SET_NULL, 
#         null=True, blank=True,
#         related_name='contacted_inquiries'
#     )

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name_plural = 'Contact Inquiries'
#         indexes = [
#             models.Index(fields=['hostel', 'status']),
#             models.Index(fields=['is_contacted', 'created_at']),
#             models.Index(fields=['email']),
#         ]

#     def __str__(self):
#         return f"Inquiry from {self.name} for {self.hostel.name}"

#     def mark_as_contacted(self, user=None):
#         """Mark inquiry as contacted"""
#         self.is_contacted = True
#         self.status = 'contacted'
#         self.contacted_at = timezone.now()
#         if user:
#             self.contacted_by = user
#         self.save(update_fields=['is_contacted', 'status', 'contacted_at', 'contacted_by'])

from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from PIL import Image
from django.db.models import Avg, Count, Q, Sum, F
from django.utils.text import slugify
from io import BytesIO
import os
import requests
from cloudinary_storage.storage import MediaCloudinaryStorage
from cloudinary import uploader

User = get_user_model()


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
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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
            available_room_count=Sum(
                F('room_types__rooms__capacity') - F('room_types__rooms__current_occupants'),
                filter=Q(room_types__rooms__is_available=True)
            ),
            inquiry_count=Count('inquiries'),
            # avg_rating=Avg('reviews__rating')
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

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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
        
        # Save first, then handle image processing
        super().save(*args, **kwargs)
        
        # Handle Cloudinary image resizing AFTER save
        if self.main_image:
            self._resize_cloudinary_image()

    def _resize_cloudinary_image(self):
        """Resize image using Cloudinary transformations instead of PIL"""
        try:
            if self.main_image:
                # Cloudinary handles resizing via URL transformations
                # No need to physically resize - Cloudinary does this on-the-fly
                # You can add transformation parameters when displaying the image
                pass
        except Exception as e:
            # Log the error in production
            print(f"Error processing image: {e}")

    def _generate_unique_slug(self, base_slug):
        slug = base_slug
        counter = 1
        while Hostel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def update_cached_fields(self):
        room_stats = self.room_types.aggregate(
            total=Sum('total_rooms'),
            available=Sum(
                F('rooms__capacity') - F('rooms__current_occupants'),
                filter=Q(rooms__is_available=True)
            )
        )
        price_stats = self.room_types.aggregate(
            min_price=models.Min('price_per_person'),
            max_price=models.Max('price_per_person')
        )
        self.total_rooms = room_stats['total'] or 0
        self.available_rooms = room_stats['available'] or 0
        self.min_price = price_stats['min_price'] or 0
        self.max_price = price_stats['max_price'] or 0
        self.save(update_fields=['total_rooms', 'available_rooms', 'min_price', 'max_price'])

    @property
    def price_range_display(self):
        if self.min_price == self.max_price:
            return f"GH₵{self.min_price:,.0f}"
        return f"GH₵{self.min_price:,.0f} - GH₵{self.max_price:,.0f}"

    @property
    def main_image_thumbnail(self):
        """Get resized image URL using Cloudinary transformations"""
        if self.main_image:
            # Use Cloudinary URL transformations for resizing
            base_url = self.main_image.url
            if 'cloudinary.com' in base_url:
                # Insert transformation parameters
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    return f"{parts[0]}/upload/w_1200,h_800,c_fill,q_85/{parts[1]}"
            return self.main_image.url
        return '/static/images/placeholder-hostel.jpg'


class RoomType(BaseTimestampModel):
    """Room type model with better structure"""
    
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
        validators=[MinValueValidator(1), MaxValueValidator(8)],
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
        super().save(*args, **kwargs)
        # Update hostel cached fields
        self.hostel.update_cached_fields()
        # Remove the problematic image resizing - Cloudinary handles this

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
                # Add Cloudinary transformations for optimization
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Remove image resizing - Cloudinary handles this automatically

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Remove image resizing - Cloudinary handles this automatically

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
    def filter_by_gender(self, gender):
        return self.filter(occupant_gender=gender)


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
        super().save(*args, **kwargs)
        # Update room type availability cache
        self.room_type.available_rooms_count = self.room_type.rooms.filter(
            is_available=True
        ).count()
        self.room_type.save(update_fields=['available_rooms_count'])

    def clean(self):
        if self.current_occupants > self.capacity:
            raise ValidationError("Current occupants cannot exceed room capacity")

    @property
    def is_full(self):
        """Check if room is at full capacity"""
        return self.current_occupants >= self.capacity

    @property
    def available_spots(self):
        """Number of available spots in the room"""
        return max(0, self.capacity - self.current_occupants)

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