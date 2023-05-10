from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import RoomUser, Complain, Contact
from .adminforms import UserCreationForm, UserChangeForm



class UserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 
					'ghana_card_number', 'gender', 'telephone', 'date_joined')
    list_filter = ('email', 'telephone')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('telephone',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': ('email', 'telephone', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'last_name', 'ghana_card_number')
    ordering = ('email',)
    filter_horizontal = ()


class ComplainAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'address', 'date_added')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'address', 'date_added')




# Now register the new UserAdmin...
admin.site.register(RoomUser, UserAdmin)
admin.site.register(Complain, ComplainAdmin)
admin.site.register(Contact, ContactAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)