from django.contrib import admin
from .models import Hostel, Booking, School
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
    list_display = ('school', 'campus', 'hostel_name', 'amenities', 'contact', 'no_of_rooms', 'cost_per_room', 'date_added')
    list_filter = ('school',)
    search_fields = ['hostel_name', 'date_added', 'hostel_coordinates']
    #form = HostelAdminForm


class BookingAdmin(admin.ModelAdmin):
    list_display = ('get_hostel', 'tenant', 'check_in', 'price', 'room_no', 'is_verified', 'expiration_date', 'days_remaining')


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'region', 'school_coordinates')

admin.site.register(Hostel, HostelAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(School, SchoolAdmin)