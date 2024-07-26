from django import forms
from .models import Hostel, RoomType, RoomTypeImages, Amenities
from atlass.models import Booking
from PIL import Image
from django.contrib.auth import get_user_model

user = get_user_model()



class BookingCreationForm(forms.ModelForm):

	phone_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'0246474321'}))

	first_name = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'Saatum'}))

	last_name = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'Timothy'}))

	email_address = forms.EmailField(
		widget=forms.EmailInput(attrs={'placeholder':'example@gmail.com'}))

	city_or_town = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'Lawra'}))

	number_of_guests = forms.IntegerField(
		widget=forms.TextInput(attrs={'min':1,'max': 4,'type': 'number'}))

	university_identification_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'University Identification Number'}))

	region_of_residence = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'Upper West'}))

	digital_address = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'BL-0587-3675'}))

	class Meta: 
		model = Booking

		#Exclude these fields as they being dynamically added in the booking view
		exclude = ('tenant', 'cost', 'is_verified', 'date_created', 'ref', 
			'room', 'receipt_number', 'room_type', 'room_no')
		widgets = {
            'check_in': forms.widgets.DateInput(attrs={'type': 'date'})
        }




class HostelCreationForm(forms.ModelForm):

	amenities = forms.ModelMultipleChoiceField(queryset=Amenities.objects.all(), 
		widget=forms.CheckboxSelectMultiple, required=True)

	class Meta:
		#Create a hostel using the Hostel Model
		model = Hostel

		#fields to be shown in the form
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 
					'description', 'account_number', 'account_name', 
					'rating', 'contact', 'display_image', 'no_of_rooms',
					'hostel_coordinates', 'cost_range', 'duration_of_rent',
					 'wifi', 'amenities']



class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class RoomTypeCreationForm(forms.ModelForm):


	files = MultipleFileField()
	
	room_numbers = forms.CharField(label='Enter the room numbers', 
		widget=forms.TextInput(attrs={'placeholder':'Please enter the room numbers'}))
	
	class Meta:
		
		#create a room type using the roomtype model
		model = RoomType
		
		#fields to be shown in the roomtype model to be shown in the form
		fields = ['room_type', 'hostel', 'room_type_number',
					'room_numbers', 'room_capacity', 'cost_per_head',
		 			'room_display_image', 'details', 'files']

	#def __init__(self, user=user, *args, **kwargs):

		#super(RoomTypeCreationForm, self).__init__(*args, **kwargs)

		#Filter foreignkey field according to the logged in user
		#To remove hostels belonging to other users to remove a long list of dropdown options

		#self.fields['hostel'].queryset = Hostel.objects.filter(created_by=user.pk)

	def _save_m2m(self):

		super()._save_m2m()

		#Creating room images
		room_images = [
		RoomTypeImages(room=self.instance, room_type_images=file) for file in self.files.getlist('files')
		]

		RoomTypeImages.objects.bulk_create(room_images)
