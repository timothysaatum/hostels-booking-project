from django.contrib import admin
from .models import Booking, Account, LeaveRequests


class BookingAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'first_name', 'last_name', 'gender', 'room_no', 'phone_number', 'is_verified', 'email_address', 'city_or_town', 
        'university_identification_number', 'region_of_residence', 'digital_address', 'check_in', 'number_of_guests',
        'cost', 'room_type', 'expiration_date', 'days_remaining')
    search_fields = ['university_identification_number', 'digital_address', 'last_name']

class AccountAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'user', 'currency', 'balance', 'created_at')

class LeaveRequestsAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'room', 'your_course', 'level', 'phone_number', 'purpose',
        'date_created', 'is_approved', 
        'appoval_id', 'i_affirm_everything_in_my_room_is_intact')

admin.site.register(Booking, BookingAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(LeaveRequests, LeaveRequestsAdmin)