from django import forms
from .models import Hostel, HostelImages, Room, RoomImages
from atlass.models import Booking


ROOM_TYPE = [
    	('1 in a room', '1 in a room'),
    	('2 in a room', '2 in a room'),
    	('3 in a room', '3 in a room'),
    	('4 in a room', '4 in a room')
    ]

#defining the parameters a user is requiredto input to reserver a room
class PayForm(forms.Form):
	phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'0806916500'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Sheldon'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Cooper'}))
	room_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'placeholder':'Select the room type'}), choices=ROOM_TYPE)
	email_address = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Tam@gmail.com'}))
	city_or_town = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Las Vegas'}))
	university_identification_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'UIN'}))
	region_of_residence = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Texas'}))
	digital_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'BL-0587-3675'}))

class BookingForm(forms.ModelForm):

	class Meta:
		room_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
				attrs={'placeholder':'Select the room type'}), 
				choices=ROOM_TYPE
			) 
		model = Booking
		exclude = ('tenant', 'cost', 'is_verified', 'date_created', 'check_in', 'ref')

#form for creating a hostel
class CreateHostelForm(forms.ModelForm):

	allow_multiple_selected = True

	amenities = forms.CharField(widget=forms.TextInput(
		attrs={'placeholder':'Enter utilities in this format e.g: Power=there a standby generator, toilet=private toilet'})
	)
	files = forms.ImageField(label='Upload hostel images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
	
	class Meta:

		model = Hostel
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 'files', 'contact', 'display_image', 'no_of_rooms',
			'hostel_coordinates', 'rate', 'duration_of_rent', 'wifi', 'amenities']


	#since all the related images cannot be stored in a single field
	#we need to loop through them and create each as
	#a separate object
	def _save_m2m(self):
		super()._save_m2m()
		images = [HostelImages(hostel=self.instance, images=file) for file in self.files.getlist('files')]
		HostelImages.objects.bulk_create(images)



class CreateRoomForm(forms.ModelForm):
	allow_multiple_selected = True
	files = forms.ImageField(label='Upload room images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

	class Meta:
		model = Room
		fields = ['occupants', 'hostel', 'room_type', 'room_display_image', 'room_capacity',
					'rate_per_head', 'price', 'files', 'room_type_number', 'details'
		]

	def _save_m2m(self):
		super()._save_m2m()
		room_images = [RoomImages(room=self.instance, room_type_images=file) for file in self.files.getlist('files')]
		RoomImages.objects.bulk_create(room_images)