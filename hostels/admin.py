from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.utils.safestring import mark_safe
from .models import (
    School, Amenity, Hostel, RoomType, RoomTypeImage, 
    Room, ContactInquiry
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'hostel_count', 'is_active', 'created_at')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'region')
    list_editable = ('is_active',)
    ordering = ('name',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            hostel_count=models.Count('hostels')
        )
    
    def hostel_count(self, obj):
        return obj.hostel_count
    hostel_count.admin_order_field = 'hostel_count'
    hostel_count.short_description = 'Number of Hostels'


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon_preview', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('category', 'is_active')
    ordering = ('category', 'name')
    
    def icon_preview(self, obj):
        return format_html('<i class="{}"></i>', obj.icon_class)
    icon_preview.short_description = 'Icon'


class RoomTypeImageInline(admin.TabularInline):
    model = RoomTypeImage
    extra = 3
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ('room_number', 'floor_number', 'capacity', 'current_occupants', 'is_available', 'is_active')
    readonly_fields = ('current_occupants',)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'hostel', 'get_room_type_display', 'beds_per_room', 
        'total_rooms', 'price_per_person', 'available_rooms_count', 'total_capacity'
    )
    list_filter = ('room_type', 'beds_per_room', 'has_private_bathroom', 'has_ac', 'created_at')
    search_fields = ('name', 'hostel__name', 'hostel__school__name')
    raw_id_fields = ('hostel',)
    inlines = [RoomTypeImageInline, RoomInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('hostel', 'name', 'room_type', 'beds_per_room', 'total_rooms')
        }),
        ('Pricing', {
            'fields': ('price_per_person',)
        }),
        ('Features', {
            'fields': ('has_private_bathroom', 'has_balcony', 'has_ac')
        }),
        ('Media & Description', {
            'fields': ('main_image', 'description')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hostel').annotate(
            available_rooms=models.Count('rooms', filter=models.Q(rooms__is_available=True))
        )
    
    def available_rooms_count(self, obj):
        return obj.available_rooms
    available_rooms_count.admin_order_field = 'available_rooms'
    available_rooms_count.short_description = 'Available Rooms'
    
    def total_capacity(self, obj):
        return obj.total_capacity
    total_capacity.short_description = 'Total Capacity'


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'school', 'campus', 'total_rooms', 
        'price_range', 'rating', 'available_rooms', 'is_featured', 'is_active'
    )
    list_filter = (
        'school', 'school__region', 'is_featured', 'is_active', 
        'has_wifi', 'created_at'
    )
    search_fields = ('name', 'owner__username', 'school__name', 'address')
    raw_id_fields = ('owner', 'school')
    list_editable = ('is_featured', 'is_active')
    filter_horizontal = ('amenities',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'owner_name', 'school', 'campus', 'name', 'slug')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('account_number', 'account_name', 'bank_name'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('description', 'main_image')
        }),
        ('Features & Amenities', {
            'fields': ('amenities', 'has_wifi')
        }),
        ('Metadata', {
            'fields': ('total_rooms', 'min_price', 'max_price', 'rating', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    readonly_fields = ('slug', 'min_price', 'max_price', 'rating_count')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'school').annotate(
            available_rooms_count=models.Count(
                'room_types__rooms', 
                filter=models.Q(room_types__rooms__is_available=True)
            )
        )
    
    def price_range(self, obj):
        if obj.min_price == obj.max_price:
            return f"GH₵{obj.min_price}"
        return f"GH₵{obj.min_price} - GH₵{obj.max_price}"
    price_range.short_description = 'Price Range'
    
    def available_rooms(self, obj):
        return obj.available_rooms_count
    available_rooms.admin_order_field = 'available_rooms_count'
    available_rooms.short_description = 'Available Rooms'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number', 'hostel_name', 'room_type', 'floor_number', 
        'capacity', 'current_occupants', 'occupancy_status', 'is_available', 'is_active'
    )
    list_filter = (
        'room_type__hostel', 'room_type__room_type', 'floor_number', 
        'is_available', 'is_active', 'created_at'
    )
    search_fields = ('room_number', 'room_type__hostel__name', 'room_type__name')
    raw_id_fields = ('room_type',)
    list_editable = ('is_available', 'is_active')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room_type__hostel')
    
    def hostel_name(self, obj):
        return obj.room_type.hostel.name
    hostel_name.short_description = 'Hostel'
    hostel_name.admin_order_field = 'room_type__hostel__name'
    
    def occupancy_status(self, obj):
        if obj.current_occupants == 0:
            color = 'green'
            status = 'Empty'
        elif obj.is_full:
            color = 'red'
            status = 'Full'
        else:
            color = 'orange'
            status = f'{obj.current_occupants}/{obj.capacity}'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color, status
        )
    occupancy_status.short_description = 'Occupancy'


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'hostel', 'room_type_interest', 
        'number_of_occupants', 'is_contacted', 'created_at'
    )
    list_filter = (
        'is_contacted', 'hostel', 'room_type_interest__room_type', 
        'school', 'created_at'
    )
    search_fields = ('name', 'email', 'phone_number', 'student_id', 'hostel__name')
    raw_id_fields = ('hostel', 'user', 'school', 'room_type_interest')
    list_editable = ('is_contacted',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone_number')
        }),
        ('Student Information', {
            'fields': ('student_id', 'school', 'user')
        }),
        ('Inquiry Details', {
            'fields': (
                'hostel', 'room_type_interest', 'number_of_occupants', 
                'preferred_move_in_date', 'message'
            )
        }),
        ('Status', {
            'fields': ('is_contacted', 'contacted_at', 'contacted_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('contacted_at',)
    
    actions = ['mark_as_contacted', 'mark_as_not_contacted']
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(is_contacted=True, contacted_by=request.user)
        self.message_user(request, f'{updated} inquiries marked as contacted.')
    mark_as_contacted.short_description = "Mark selected inquiries as contacted"
    
    def mark_as_not_contacted(self, request, queryset):
        updated = queryset.update(is_contacted=False, contacted_by=None, contacted_at=None)
        self.message_user(request, f'{updated} inquiries marked as not contacted.')
    mark_as_not_contacted.short_description = "Mark selected inquiries as not contacted"


@admin.register(RoomTypeImage)
class RoomTypeImageAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'caption', 'order', 'image_preview', 'created_at')
    list_filter = ('room_type__hostel', 'created_at')
    search_fields = ('room_type__name', 'room_type__hostel__name', 'caption')
    raw_id_fields = ('room_type',)
    list_editable = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


# Customize admin site header
admin.site.site_header = "Hostel Booking Administration"
admin.site.site_title = "Hostel Admin"
admin.site.index_title = "Welcome to Hostel Booking Admin"