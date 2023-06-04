from django.contrib import admin
from .models import Booking, Account


class BookingAdmin(admin.ModelAdmin):
    list_display = ('hostel_booked', 'tenant', 'first_name', 'last_name', 'phone_number', 'email_address', 'city_or_town', 
        'university_identification_number', 'region_of_residence', 'digital_address', 'check_in', 
        'price', 'room_no', 'is_verified', 
        'expiration_date', 'days_remaining', 'ref')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance', 'booking_for', 'created_at')
admin.site.register(Booking, BookingAdmin)
admin.site.register(Account, AccountAdmin)