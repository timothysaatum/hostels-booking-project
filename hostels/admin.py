from django.contrib import admin
from .models import Hostel, School, RoomType, RoomTypeImages, Room, Amenities
#from django import forms



class HostelAdmin(admin.ModelAdmin):

    list_display = ('school', 'campus', 'hostel_name', 'account_number', 'contact', 'no_of_rooms', 
        'cost_range', 'date_added')

    list_filter = ('school',)

    search_fields = ['hostel_name', 'date_added', 'hostel_coordinates']
    

class RoomTypeAdmin(admin.ModelAdmin):

    list_display = ('hostel', 'room_type', 'room_type_number', 'room_numbers', 'room_capacity', 'cost_per_head')


class SchoolAdmin(admin.ModelAdmin):

    list_display = ('name', 'city', 'region', 'school_coordinates')
    

class AmenitiesAdmin(admin.ModelAdmin):

    list_display = ('amenity', 'fontawesome_icon')

class RoomAdmin(admin.ModelAdmin):
    
    list_display = ('hostel', 'room_type', 'room_number', 'capacity', 'cost_per_head')

class RoomTypeImageAdmin(admin.ModelAdmin):
    list_display = ('room', 'room_type_images')


admin.site.register(Hostel, HostelAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(RoomTypeImages, RoomTypeImageAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Amenities, AmenitiesAdmin)