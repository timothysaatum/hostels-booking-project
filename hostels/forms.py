from django import forms
from .models import Hostel, RoomType, RoomTypeImages
from atlass.models import Booking



class BookingCreationForm(forms.Form):
	phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'0806916500'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Sheldon'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Cooper'}))
	email_address = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Tam@gmail.com'}))
	city_or_town = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Las Vegas'}))
	gender = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'M or F'}))
	university_identification_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'UIN'}))
	region_of_residence = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Texas'}))
	digital_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'BL-0587-3675'}))


class BookingForm(forms.ModelForm):
	#room_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
	#			attrs={'placeholder':'Select the room type'}), 
	#			choices=ROOM_TYPE
	#		)

	class Meta: 
		model = Booking
		exclude = ('tenant', 'cost', 'is_verified', 'date_created', 'check_in', 'ref')




class HostelCreationForm(forms.ModelForm):


	amenities = forms.CharField(widget=forms.TextInput(
		attrs={'placeholder':'Enter utilities in this format e.g: Power=there a standby generator, toilet=private toilet'})
	)
	
	
	class Meta:

		model = Hostel
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 'contact', 'display_image', 'no_of_rooms',
			'hostel_coordinates', 'cost_range', 'duration_of_rent', 'wifi', 'amenities']




class RoomTypeCreationForm(forms.ModelForm):
	allow_multiple_selected = True
	files = forms.ImageField(label='Upload room images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
	room_numbers = forms.CharField(label='Enter the room numbers', widget=forms.TextInput(attrs={'placeholder':'Please enter the room numbers'}))
	class Meta:
		model = RoomType
		fields = ['hostel', 'room_type', 'room_type_number','room_numbers', 'room_capacity', 'cost_per_head',
		 'room_display_image', 'details', 'files']

	def _save_m2m(self):
		super()._save_m2m()
		room_images = [RoomTypeImages(room=self.instance, room_type_images=file) for file in self.files.getlist('files')]
		RoomTypeImages.objects.bulk_create(room_images)