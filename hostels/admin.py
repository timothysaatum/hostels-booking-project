from django.contrib import admin
from .models import Hostel, School, HostelImages, Room, RoomImages
#from django import forms


#class HostelAdminForm(forms.ModelForm):
#    class Meta:
#        model = Hostel
#        fields = '__all__'
#        widgets = {
#            'amenities': forms.CheckboxSelectMultiple,
#        }
#
class HostelAdmin(admin.ModelAdmin):
    list_display = ('school', 'campus', 'hostel_name', 'contact', 'no_of_rooms', 
        'rate', 'date_added', 'hostel_amenities')
    list_filter = ('school',)
    search_fields = ['hostel_name', 'date_added', 'hostel_coordinates']
    #form = HostelAdminForm

class RoomAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'room_type', 'room_type_number', 'occupants')

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'school_coordinates')



admin.site.register(Hostel, HostelAdmin)
admin.site.register(HostelImages) 
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomImages)
admin.site.register(School, SchoolAdmin)


