from django import forms
from .models import RoomUser
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'e.g example@gmail.com'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Zoppie'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Zigi'}))
	gender = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'male'}))
	telephone = PhoneNumberField(
        widget=forms.TextInput(attrs={'placeholder': 'E.g +233 246 743 489'}),
        required=True)
	ghana_card_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'GHA-xxxxxxxxx-x'}))

	class Meta:
		model = RoomUser
		fields = ['email','first_name', 'last_name', 'telephone', 'ghana_card_number', 'gender', 'password1', 'password2']

