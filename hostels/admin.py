from django.contrib import admin
from .models import Hostel, Booking, School


class HostelAdmin(admin.ModelAdmin):
    list_display = ('school', 'campus', 'hostel_name', 'category', 'contact', 'no_of_rooms', 'cost_per_room', 'date_added')
    list_filter = ('category', 'school')
    search_fields = ['title', 'hostel_name', 'date_added', 'hostel_coordinates']


class BookingAdmin(admin.ModelAdmin):
    list_display = ('get_hostel', 'tenant', 'check_in', 'price', 'is_verified', 'expiration_date', 'days_remaining', 'message')


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'school_coordinates')


admin.site.register(Hostel, HostelAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(School, SchoolAdmin)