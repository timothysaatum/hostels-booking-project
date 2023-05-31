from django import forms
from .models import Booking, Hostel


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

	AMENITIES = [
		('Water', 'Water'),
		('Power Supply', 'Power Supply'),
		('Toilet', 'Toilet'),
		('Kitchen', 'Kitchen'),
		('Individual Bath Room', 'Individual Bath Room'),
		('Shared bath Room', 'Shared bath Room'),
		('Individual Meters', 'Individual meters'),
		('Wifi', 'Wifi'),
		('AC/fan', 'AC/fan'),
		('Study Area', 'Study Area'),
		('Bed Available', 'Bed Available'),
		('Wardrope', 'Wardrope'),
		('Tiled floor', 'Tiled floor')
	]

	amenities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'placeholder':'Check all that apply'}), choices=AMENITIES)

	class Meta:
		model = Hostel
		fields = ['owner_name', 'school', 'campus', 'hostel_name', 'contact', 'image', 'no_of_rooms',
			'hostel_coordinates', 'cost_per_room', 'duration_of_rent', 'wifi', 'amenities', 'details',
		]
