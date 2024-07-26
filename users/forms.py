from django import forms
from .models import RoomUser
from django.contrib.auth.forms import UserCreationForm




class UserRegisterForm(UserCreationForm):

	email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'e.g example@gmail.com'}))

	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Zoppie'}))

	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Zigi'}))

	gender = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Male'}))

	telephone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'E.g 0245867859'}),
        required=True)

	ghana_card_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'GHA-XXXXXXXXX-X'}))

	your_emmergency_contact = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Emmergency Contact'}))

	class Meta:

		model = RoomUser

		fields = [
			'email','first_name', 'last_name', 'telephone', 'ghana_card_number',
			 'gender', 'your_emmergency_contact', 'name_of_emmergency_contact', 
			 'password1', 'password2', 'has_a_hostel'
			]
