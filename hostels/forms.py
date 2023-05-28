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

	class Meta:
		model = Hostel
		fields = '__all__'