from django.contrib import admin
from .models import Booking, Account


class BookingAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'first_name', 'last_name', 'gender', 'room_no', 'phone_number', 'email_address', 'city_or_town', 
        'university_identification_number', 'region_of_residence', 'digital_address', 'check_in', 
        'cost', 'is_verified', 'room_type', 
        'expiration_date', 'days_remaining')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance', 'created_at')
admin.site.register(Booking, BookingAdmin)
admin.site.register(Account, AccountAdmin)