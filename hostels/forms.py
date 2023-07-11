from django import forms
from .models import Hostel, RoomType, RoomTypeImages
from atlass.models import Booking
from PIL import Image



class BookingCreationForm(forms.ModelForm):
	phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'0246474321'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Saatum'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Timothy'}))
	email_address = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'example@gmail.com'}))
	city_or_town = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Tamale'}))
	university_identification_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'UIN'}))
	region_of_residence = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Lawra'}))
	digital_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'BL-0587-3675'}))

	class Meta: 
		model = Booking
		exclude = ('tenant', 'cost', 'is_verified', 'date_created', 'ref', 'number_of_guests')




class HostelCreationForm(forms.ModelForm):


	amenities = forms.CharField(widget=forms.TextInput(
		attrs={'placeholder':'Enter utilities in this format e.g: Power=there a standby generator, toilet=private toilet'})
	)
	
	
	class Meta:

		model = Hostel
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 'rating', 'contact', 'display_image', 'no_of_rooms',
			'hostel_coordinates', 'cost_range', 'duration_of_rent', 'wifi', 'amenities']




class RoomTypeCreationForm(forms.ModelForm):
	allow_multiple_selected = True
	files = forms.ImageField(label='Upload room images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
	room_numbers = forms.CharField(label='Enter the room numbers', widget=forms.TextInput(attrs={'placeholder':'Please enter the room numbers'}))
	class Meta:
		model = RoomType
		fields = ['room_type', 'room_type_number','room_numbers', 'room_capacity', 'cost_per_head',
		 'room_display_image', 'details', 'files']

	def _save_m2m(self):
		super()._save_m2m()
		room_images = [RoomTypeImages(room=self.instance, room_type_images=file) for file in self.files.getlist('files')]
		RoomTypeImages.objects.bulk_create(room_images)