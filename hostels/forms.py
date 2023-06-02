from django import forms
from .models import Booking, Hostel, HostelImages


class PayForm(forms.Form):

	phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'0806916500'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Sheldon'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Cooper'}))
	email_address = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Tam@gmail.com'}))
	city_or_town = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Las Vegas'}))
	university_identification_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'UIN'}))
	region_of_residence = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Texas'}))
	digital_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'BL-0587-3675'}))


class CreateHostelForm(forms.ModelForm):

	allow_multiple_selected = True

	amenities = forms.CharField(widget=forms.TextInput(
		attrs={'placeholder':'Enter utilities in this format e.g: Power=there a standby generator, toilet=private toilet'})
	)
	files = forms.ImageField(label='Upload hostel images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
	
	class Meta:

		model = Hostel
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 'files', 'contact', 'display_image', 'no_of_rooms',
			'hostel_coordinates', 'cost_per_room', 'duration_of_rent', 'wifi', 'amenities', 'details',
		]

	def _save_m2m(self):
		super()._save_m2m()
		images = [HostelImages(hostel=self.instance, images=file) for file in self.files.getlist('files')]
		HostelImages.objects.bulk_create(images)