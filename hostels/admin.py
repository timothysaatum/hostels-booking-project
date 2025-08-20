from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import (
    School, Amenity, Hostel, HostelImage, RoomType, RoomTypeImage, 
    Room, ContactInquiry
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'hostel_count', 'coordinates_display', 'is_active', 'created_at')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'region')
    list_editable = ('is_active',)
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'city', 'region')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'Add coordinates for distance calculations'
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            hostel_count=models.Count('hostels')
        )
    
    def hostel_count(self, obj):
        return obj.hostel_count
    hostel_count.admin_order_field = 'hostel_count'
    hostel_count.short_description = 'Number of Hostels'
    
    def coordinates_display(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<span style="color: green;">✓ ({}, {})</span>',
                obj.latitude, obj.longitude
            )
        return format_html('<span style="color: red;">✗ Not set</span>')
    coordinates_display.short_description = 'Coordinates'


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon_preview', 'hostel_count', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name',)
    list_editable = ('category', 'is_active')
    ordering = ('category', 'name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            hostel_count=models.Count('hostel')
        )
    
    def icon_preview(self, obj):
        return format_html('<i class="{}"></i>', obj.icon_class)
    icon_preview.short_description = 'Icon'
    
    def hostel_count(self, obj):
        return obj.hostel_count
    hostel_count.admin_order_field = 'hostel_count'
    hostel_count.short_description = 'Used by Hostels'


class HostelImageInline(admin.TabularInline):
    model = HostelImage
    extra = 3
    max_num = 15
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 75px; object-fit: cover; border-radius: 4px;" />',
                obj.image_thumbnail if hasattr(obj, 'image_thumbnail') else obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


class RoomTypeImageInline(admin.TabularInline):
    model = RoomTypeImage
    extra = 2
    max_num = 10
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image_thumbnail if hasattr(obj, 'image_thumbnail') else obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    max_num = 50
    fields = (
        'room_number', 'floor_number', 'capacity', 'current_occupants', 
        'occupant_gender', 'is_available', 'is_active', 'occupancy_status'
    )
    readonly_fields = ('occupancy_status',)
    
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
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    occupancy_status.short_description = 'Occupancy'


class RoomTypeInline(admin.StackedInline):
    model = RoomType
    extra = 1
    max_num = 10
    fields = (
        ('name', 'room_type', 'beds_per_room'),
        ('total_rooms', 'price_per_person'),
        ('has_private_bathroom', 'has_balcony', 'has_ac', 'has_study_desk', 'has_wardrobe'),
        'main_image',
        'description',
        'room_generation_info'
    )
    readonly_fields = ('room_generation_info',)
    show_change_link = True
    
    def room_generation_info(self, obj):
        if obj.pk:
            room_count = obj.rooms.count()
            available_count = obj.rooms.filter(is_available=True).count()
            return format_html(
                '<div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">'
                '<strong>Auto-Generated Rooms:</strong><br>'
                'Total: {} rooms<br>'
                'Available: {} rooms<br>'
                'Occupied: {} rooms<br>'
                '<small>Rooms are automatically created when this room type is saved.</small>'
                '</div>',
                room_count, available_count, room_count - available_count
            )
        return format_html(
            '<div style="background: #fff3cd; padding: 10px; border-radius: 5px;">'
            '<strong>Note:</strong> Rooms will be automatically generated after saving this room type.'
            '</div>'
        )
    room_generation_info.short_description = 'Room Generation Status'


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'school', 'campus', 'room_summary', 
        'price_range', 'rating', 'distance_to_school_display', 'main_image_preview',
        'is_featured', 'is_active'
    )
    list_filter = (
        'school', 'school__region', 'is_featured', 'is_active', 
        'has_wifi', 'created_at'
    )
    search_fields = ('name', 'owner__username', 'school__name', 'address', 'owner_name')
    raw_id_fields = ('owner', 'school')
    list_editable = ('is_featured', 'is_active')
    filter_horizontal = ('amenities',)
    
    inlines = [HostelImageInline, RoomTypeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('owner', 'owner_name'),
                ('school', 'campus'),
                ('name', 'slug'),
            )
        }),
        ('Contact Information', {
            'fields': (
                ('phone_number', 'email'),
                'address',
            )
        }),
        ('Location', {
            'fields': (
                ('latitude', 'longitude'),
                'distance_info'
            ),
            'description': 'Add coordinates for distance calculations to school'
        }),
        ('Banking Information', {
            'fields': (
                ('account_number', 'account_name'),
                'bank_name',
            ),
            'classes': ('collapse',)
        }),
        ('Content & Media', {
            'fields': (
                'description',
                'main_image',
            )
        }),
        ('Features & Amenities', {
            'fields': (
                'amenities',
                'has_wifi',
            )
        }),
        ('Cached Statistics (Auto-calculated)', {
            'fields': (
                'statistics_display',
                ('min_price', 'max_price'),
                ('total_rooms', 'available_rooms'),
                ('rating', 'rating_count'),
            ),
            'classes': ('collapse',),
            'description': 'These fields are automatically calculated from room types and rooms'
        }),
        ('SEO & Metadata', {
            'fields': (
                'meta_title',
                'meta_description',
            ),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': (
                ('is_featured', 'is_active'),
            )
        }),
    )
    
    readonly_fields = (
        'slug', 'min_price', 'max_price', 'rating_count', 
        'total_rooms', 'available_rooms', 'distance_info', 'statistics_display'
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'owner', 'school'
        ).prefetch_related('room_types', 'room_types__rooms')
    
    def room_summary(self, obj):
        room_types_count = obj.room_types.count()
        total_rooms = obj.total_rooms
        available_rooms = obj.available_rooms
        
        return format_html(
            '<div>'
            '<strong>{}</strong> room types<br>'
            '<span style="color: blue;">{}</span> total rooms<br>'
            '<span style="color: green;">{}</span> available spots'
            '</div>',
            room_types_count, total_rooms, available_rooms
        )
    room_summary.short_description = 'Room Summary'
    
    def distance_to_school_display(self, obj):
        distance = obj.distance_to_school
        if distance is not None:
            return format_html(
                '<span style="color: green;">{} km</span>',
                float(distance)
            )

        return format_html('<span style="color: red;">Not calculated</span>')
    distance_to_school_display.short_description = 'Distance to School'
    
    def distance_info(self, obj):
        if obj.pk:
            distance = obj.distance_to_school
            if distance is not None:
                return format_html(
                    '<div style="background: #d4edda; padding: 10px; border-radius: 5px;">'
                    '<strong>Distance to {}:</strong> {:.1f} km'
                    '</div>',
                    obj.school.name, distance
                )
            elif obj.latitude and obj.longitude and obj.school.latitude and obj.school.longitude:
                return format_html(
                    '<div style="background: #fff3cd; padding: 10px; border-radius: 5px;">'
                    'Coordinates available but distance calculation failed.'
                    '</div>'
                )
            else:
                return format_html(
                    '<div style="background: #f8d7da; padding: 10px; border-radius: 5px;">'
                    'Add coordinates for both hostel and school to calculate distance.'
                    '</div>'
                )
        return "Save hostel first to see distance calculation"
    distance_info.short_description = 'Distance Calculation'
    
    def statistics_display(self, obj):
        if obj.pk:
            room_types = obj.room_types.count()
            total_capacity = sum(rt.total_capacity for rt in obj.room_types.all())
            occupied_spots = sum(
                rt.rooms.aggregate(occupied=models.Sum('current_occupants'))['occupied'] or 0
                for rt in obj.room_types.all()
            )
            occupancy_rate = (occupied_spots / total_capacity * 100) if total_capacity > 0 else 0
            
            return format_html(
                '<div style="background: #e7f3ff; padding: 10px; border-radius: 5px;">'
                '<strong>Room Types:</strong> {}<br>'
                '<strong>Total Capacity:</strong> {} spots<br>'
                '<strong>Occupied:</strong> {} spots<br>'
                '<strong>Occupancy Rate:</strong> {:.1f}%<br>'
                '</div>',
                room_types, total_capacity, occupied_spots, occupancy_rate
            )
        return "Save hostel first to see statistics"
    statistics_display.short_description = 'Current Statistics'
    
    def price_range(self, obj):
        if obj.min_price == obj.max_price:
            return f"GH₵{obj.min_price:,.0f}"
        return f"GH₵{obj.min_price:,.0f} - GH₵{obj.max_price:,.0f}"
    price_range.short_description = 'Price Range'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.main_image_thumbnail
            )
        return "No image"
    main_image_preview.short_description = 'Main Image'

    # Custom actions
    actions = [
        'mark_as_featured', 'mark_as_not_featured', 'activate_hostels', 
        'deactivate_hostels', 'update_cached_fields'
    ]
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} hostels marked as featured.')
    mark_as_featured.short_description = "Mark selected hostels as featured"

    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} hostels removed from featured.')
    mark_as_not_featured.short_description = "Remove from featured"
    
    def mark_as_converted(self, request, queryset):
        updated = queryset.update(status='converted')
        self.message_user(request, f'{updated} inquiries marked as converted.')
    mark_as_converted.short_description = "Mark as converted (booked)"


@admin.register(HostelImage)
class HostelImageAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'caption', 'order', 'image_preview', 'created_at')
    list_filter = ('hostel', 'created_at')
    search_fields = ('hostel__name', 'caption')
    raw_id_fields = ('hostel',)
    list_editable = ('order', 'caption')
    ordering = ('hostel', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 75px; object-fit: cover; border-radius: 4px;" />',
                obj.image_thumbnail
            )
        return "No image"
    image_preview.short_description = 'Preview'

    actions = ['reorder_images']
    
    def reorder_images(self, request, queryset):
        """Reorder selected images starting from 1"""
        for i, image in enumerate(queryset.order_by('hostel', 'order'), 1):
            image.order = i
            image.save(update_fields=['order'])
        self.message_user(request, f'{queryset.count()} images reordered successfully.')
    reorder_images.short_description = "Reorder selected images"


@admin.register(RoomTypeImage)
class RoomTypeImageAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'hostel_name', 'caption', 'order', 'image_preview', 'created_at')
    list_filter = ('room_type__hostel', 'created_at')
    search_fields = ('room_type__name', 'room_type__hostel__name', 'caption')
    raw_id_fields = ('room_type',)
    list_editable = ('order', 'caption')
    ordering = ('room_type__hostel', 'room_type', 'order')
    
    def hostel_name(self, obj):
        return obj.room_type.hostel.name
    hostel_name.short_description = 'Hostel'
    hostel_name.admin_order_field = 'room_type__hostel__name'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 75px; object-fit: cover; border-radius: 4px;" />',
                obj.image_thumbnail
            )
        return "No image"
    image_preview.short_description = 'Preview'


# Customize admin site
admin.site.site_header = "Hostel Booking Management System"
admin.site.site_title = "Hostel Admin"
admin.site.index_title = "Welcome to Hostel Management Dashboard"

# Add custom dashboard stats
def admin_stats_view(request):
    """Custom admin dashboard with statistics"""
    from django.template.response import TemplateResponse
    
    context = {
        'total_hostels': Hostel.objects.count(),
        'active_hostels': Hostel.objects.filter(is_active=True).count(),
        'total_schools': School.objects.count(),
        'total_room_types': RoomType.objects.count(),
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(is_available=True).count(),
        'total_inquiries': ContactInquiry.objects.count(),
        'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
        'recent_hostels': Hostel.objects.order_by('-created_at')[:5],
        'recent_inquiries': ContactInquiry.objects.order_by('-created_at')[:5],
    }
    
    return TemplateResponse(request, 'admin/dashboard_stats.html', context)

# Custom admin actions for bulk operations
class BulkOperationsMixin:
    """Mixin to add common bulk operations"""
    
    def bulk_activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} items activated.')
    bulk_activate.short_description = "Activate selected items"
    
    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} items deactivated.')
    bulk_deactivate.short_description = "Deactivate selected items"


# Add CSS for better admin interface
class CustomAdminSite(admin.AdminSite):
    """Custom admin site with enhanced interface"""
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_title'] = 'Hostel Management'
        context['site_header'] = 'Hostel Booking System'
        context['index_title'] = 'Administration Dashboard'
        return context


# Performance optimizations for admin
class OptimizedModelAdmin(admin.ModelAdmin):
    """Base admin class with performance optimizations"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add select_related and prefetch_related based on list_display
        if hasattr(self, 'list_select_related'):
            qs = qs.select_related(*self.list_select_related)
        if hasattr(self, 'list_prefetch_related'):
            qs = qs.prefetch_related(*self.list_prefetch_related)
        return qs


# Custom filters for better admin experience
class HasCoordinatesFilter(admin.SimpleListFilter):
    """Filter for items that have coordinates set"""
    title = 'has coordinates'
    parameter_name = 'has_coordinates'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                latitude__isnull=False, 
                longitude__isnull=False
            )
        if self.value() == 'no':
            return queryset.filter(
                models.Q(latitude__isnull=True) | 
                models.Q(longitude__isnull=True)
            )


class OccupancyFilter(admin.SimpleListFilter):
    """Filter rooms by occupancy status"""
    title = 'occupancy status'
    parameter_name = 'occupancy'

    def lookups(self, request, model_admin):
        return (
            ('empty', 'Empty'),
            ('partial', 'Partially Occupied'),
            ('full', 'Full'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'empty':
            return queryset.filter(current_occupants=0)
        if self.value() == 'partial':
            return queryset.filter(
                current_occupants__gt=0,
                current_occupants__lt=models.F('capacity')
            )
        if self.value() == 'full':
            return queryset.filter(current_occupants__gte=models.F('capacity'))


# Add custom filters to admin classes
HostelAdmin.list_filter += (HasCoordinatesFilter,)
SchoolAdmin.list_filter += (HasCoordinatesFilter,)

# JavaScript for enhanced admin interface
class EnhancedAdminMixin:
    """Mixin to add enhanced JavaScript functionality"""
    
    class Media:
        css = {
            'all': ('admin/css/enhanced_admin.css',)
        }
        js = (
            'admin/js/enhanced_admin.js',
            'admin/js/distance_calculator.js',
        )


# Apply enhanced admin to key classes
class EnhancedHostelAdmin(EnhancedAdminMixin, HostelAdmin):
    pass

# Re-register with enhanced versions will be done after RoomTypeAdmin is defined

class EnhancedHostelAdmin(EnhancedAdminMixin, HostelAdmin):
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} hostels marked as featured.')
    mark_as_featured.short_description = "Mark selected hostels as featured"

    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} hostels removed from featured.')
    mark_as_not_featured.short_description = "Remove from featured"

    def activate_hostels(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} hostels activated.')
    activate_hostels.short_description = "Activate selected hostels"

    def deactivate_hostels(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} hostels deactivated.')
    deactivate_hostels.short_description = "Deactivate selected hostels"

    def update_cached_fields(self, request, queryset):
        updated = 0
        for hostel in queryset:
            hostel.update_cached_fields()
            updated += 1
        self.message_user(request, f'Cached fields updated for {updated} hostels.')
    update_cached_fields.short_description = "Update cached fields (prices, room counts)"


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'hostel', 'get_room_type_display', 'beds_per_room', 
        'total_rooms', 'price_per_person', 'room_status', 'total_capacity',
        'main_image_preview'
    )
    list_filter = (
        'room_type', 'beds_per_room', 'has_private_bathroom', 'has_ac', 
        'hostel__school', 'created_at'
    )
    search_fields = ('name', 'hostel__name', 'hostel__school__name')
    raw_id_fields = ('hostel',)
    inlines = [RoomTypeImageInline, RoomInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'hostel', 'name', 'room_type', 'beds_per_room', 'total_rooms',
                'auto_room_generation_note'
            )
        }),
        ('Pricing', {
            'fields': ('price_per_person',)
        }),
        ('Room Features', {
            'fields': (
                ('has_private_bathroom', 'has_balcony'),
                ('has_ac', 'has_study_desk', 'has_wardrobe')
            )
        }),
        ('Media & Description', {
            'fields': ('main_image', 'description')
        }),
        ('Room Statistics', {
            'fields': ('room_statistics',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('auto_room_generation_note', 'room_statistics')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'hostel'
        ).prefetch_related('rooms')
    
    def auto_room_generation_note(self, obj):
        if obj.pk:
            return format_html(
                '<div style="background: #d4edda; padding: 10px; border-radius: 5px;">'
                '<strong>✓ Rooms Generated:</strong><br>'
                'This room type has {} automatically generated rooms.<br>'
                '<small>Changing total_rooms will add/remove rooms as needed.</small>'
                '</div>',
                obj.rooms.count()
            )
        return format_html(
            '<div style="background: #fff3cd; padding: 10px; border-radius: 5px;">'
            '<strong>⚠ Auto Room Generation:</strong><br>'
            'After saving, {} individual rooms will be automatically created.<br>'
            '<small>Each room will have capacity of {} (beds per room).</small>'
            '</div>',
            obj.total_rooms if hasattr(obj, 'total_rooms') else 0,
            obj.beds_per_room if hasattr(obj, 'beds_per_room') else 0
        )
    auto_room_generation_note.short_description = 'Room Generation'
    
    def room_statistics(self, obj):
        if obj.pk:
            rooms = obj.rooms.all()
            total_rooms = rooms.count()
            available_rooms = rooms.filter(is_available=True).count()
            occupied_rooms = rooms.filter(current_occupants__gt=0).count()
            total_occupants = sum(room.current_occupants for room in rooms)
            total_capacity = sum(room.capacity for room in rooms)
            occupancy_rate = (total_occupants / total_capacity * 100) if total_capacity > 0 else 0
            
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">'
                '<h4 style="margin-top: 0;">Room Statistics</h4>'
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">'
                '<div><strong>Total Rooms:</strong> {}</div>'
                '<div><strong>Available Rooms:</strong> <span style="color: green;">{}</span></div>'
                '<div><strong>Occupied Rooms:</strong> <span style="color: orange;">{}</span></div>'
                '<div><strong>Total Capacity:</strong> {} spots</div>'
                '<div><strong>Current Occupants:</strong> {} people</div>'
                '<div><strong>Occupancy Rate:</strong> <span style="color: {};">{:.1f}%</span></div>'
                '</div>'
                '</div>',
                total_rooms, available_rooms, occupied_rooms, 
                total_capacity, total_occupants,
                'red' if occupancy_rate > 80 else 'orange' if occupancy_rate > 60 else 'green',
                occupancy_rate
            )
        return "Save room type first to see statistics"
    room_statistics.short_description = 'Room Statistics'
    
    def room_status(self, obj):
        available_count = obj.rooms.filter(is_available=True).count()
        total_count = obj.rooms.count()
        
        return format_html(
            '<span style="color: green;">{}</span> / <span style="color: blue;">{}</span>',
            available_count, total_count
        )
    room_status.short_description = 'Available / Total'
    
    def total_capacity(self, obj):
        return obj.total_capacity
    total_capacity.short_description = 'Total Capacity'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.main_image_url
            )
        return "No image"
    main_image_preview.short_description = 'Image'
    
    actions = ['regenerate_rooms', 'update_availability']
    
    def regenerate_rooms(self, request, queryset):
        """Regenerate rooms for selected room types"""
        updated = 0
        for room_type in queryset:
            # Delete existing rooms (only empty ones)
            empty_rooms = room_type.rooms.filter(current_occupants=0)
            deleted_count = empty_rooms.count()
            empty_rooms.delete()
            
            # Regenerate rooms
            room_type._create_rooms()
            updated += 1
            
            self.message_user(
                request,
                f'Regenerated rooms for {room_type.name}. '
                f'Deleted {deleted_count} empty rooms and created {room_type.total_rooms} new rooms.'
            )
        
        self.message_user(request, f'Rooms regenerated for {updated} room types.')
    regenerate_rooms.short_description = "Regenerate rooms (deletes empty rooms first)"
    
    def update_availability(self, request, queryset):
        """Update availability cache for selected room types"""
        for room_type in queryset:
            room_type.available_rooms_count = room_type.rooms.filter(is_available=True).count()
            room_type.save(update_fields=['available_rooms_count'])
        
        self.message_user(request, f'Availability updated for {queryset.count()} room types.')
    update_availability.short_description = "Update availability cache"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number', 'hostel_name', 'room_type', 'floor_number', 
        'capacity', 'current_occupants', 'occupancy_display', 'occupant_gender',
        'is_available', 'is_active',
    )
    list_filter = (
        'room_type__hostel', 'room_type__room_type', 'floor_number', 
        'occupant_gender', 'is_available', 'is_active', 'created_at',
        OccupancyFilter,
    )
    search_fields = ('room_number', 'room_type__hostel__name', 'room_type__name')
    raw_id_fields = ('room_type',)
    list_editable = ('current_occupants', 'occupant_gender', 'is_available', 'is_active')
    
    fieldsets = (
        ('Room Details', {
            'fields': (
                'room_type',
                ('room_number', 'floor_number'),
                ('capacity', 'current_occupants'),
                'occupant_gender',
                'occupancy_info'
            )
        }),
        ('Status', {
            'fields': (
                ('is_available', 'is_active'),
                'notes'
            )
        }),
    )
    
    readonly_fields = ('occupancy_info',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room_type__hostel')
    
    def hostel_name(self, obj):
        return obj.room_type.hostel.name
    hostel_name.short_description = 'Hostel'
    hostel_name.admin_order_field = 'room_type__hostel__name'
    
    def occupancy_display(self, obj):
        percentage = float(obj.occupancy_percentage or 0)
        percentage_display = f"{percentage:.0f}"  # ✅ pre-format here
        
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
            '<div>'
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<small>{}% occupied</small>'
            '</div>',
            color, status, percentage_display
        )
    occupancy_display.short_description = 'Occupancy'
    
    def occupancy_info(self, obj):
        if obj.pk:
            percentage = float(obj.occupancy_percentage or 0)
            percentage_display = f"{percentage:.1f}"  # ✅ pre-format here
            
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Occupancy Details:</strong><br>'
                'Available spots: {} out of {}<br>'
                'Occupancy rate: {}%<br>'
                'Status: {}'
                '</div>',
                obj.available_spots, obj.capacity, percentage_display,
                'Full' if obj.is_full else 'Available'
            )
        return "Save room first to see occupancy info"
    occupancy_info.short_description = 'Occupancy Information'
    
    actions = ['mark_as_available', 'mark_as_unavailable', 'reset_occupancy']
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        for room in queryset:
            room._update_room_type_cache()
        self.message_user(request, f'{updated} rooms marked as available.')
    mark_as_available.short_description = "Mark selected rooms as available"
    
    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        for room in queryset:
            room._update_room_type_cache()
        self.message_user(request, f'{updated} rooms marked as unavailable.')
    mark_as_unavailable.short_description = "Mark selected rooms as unavailable"
    
    def reset_occupancy(self, request, queryset):
        updated = queryset.update(current_occupants=0, is_available=True)
        for room in queryset:
            room._update_room_type_cache()
            room.room_type.hostel.update_cached_fields()
        self.message_user(request, f'Occupancy reset for {updated} rooms.')
    reset_occupancy.short_description = "Reset occupancy (set to 0 occupants)"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'hostel', 'room_type_interest', 
        'number_of_occupants', 'status', 'is_contacted', 'created_at'
    )
    list_filter = (
        'status', 'is_contacted', 'hostel', 'room_type_interest__room_type', 
        'school', 'created_at'
    )
    search_fields = ('name', 'email', 'phone_number', 'student_id', 'hostel__name')
    raw_id_fields = ('hostel', 'user', 'school', 'room_type_interest')
    list_editable = ('status', 'is_contacted')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                ('name', 'email'),
                'phone_number'
            )
        }),
        ('Student Information', {
            'fields': (
                ('student_id', 'school'),
                'user'
            )
        }),
        ('Inquiry Details', {
            'fields': (
                'hostel',
                ('room_type_interest', 'number_of_occupants'),
                'preferred_move_in_date',
                'message'
            )
        }),
        ('Management', {
            'fields': (
                ('status', 'is_contacted'),
                ('contacted_at', 'contacted_by')
            )
        }),
    )
    
    readonly_fields = ('contacted_at',)
    
    actions = ['mark_as_contacted', 'mark_as_not_contacted', 'mark_as_converted']
    
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_contacted=True, 
            status='contacted',
            contacted_by=request.user,
            contacted_at=timezone.now()
        )
        self.message_user(request, f'{updated} inquiries marked as contacted.')
    mark_as_contacted.short_description = "Mark selected inquiries as contacted"
    
    def mark_as_not_contacted(self, request, queryset):
        updated = queryset.update(
            is_contacted=False, 
            status='new',
            contacted_by=None, 
            contacted_at=None
        )
        self.message_user(request, f'{updated} inquiries marked as not contacted.')
    mark_as_not_contacted.short_description = "Mark selected inquiries as not contacted"

    def mark_as_converted(self, request, queryset):
        updated = queryset.update(status='converted')
        self.message_user(request, f'{updated} inquiries marked as converted.')
    mark_as_converted.short_description = "Mark as converted (booked)"


HostelAdmin.list_select_related = ('owner', 'school')
HostelAdmin.list_prefetch_related = ('room_types', 'amenities')

RoomTypeAdmin.list_select_related = ('hostel', 'hostel__school')
RoomTypeAdmin.list_prefetch_related = ('rooms',)

RoomAdmin.list_select_related = ('room_type', 'room_type__hostel')

ContactInquiryAdmin.list_select_related = ('hostel', 'school', 'room_type_interest', 'user')
