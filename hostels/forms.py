from django import forms
from .models import Booking


class PayForm(forms.Form):
	momo_no = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'E.g 0506916500'}))
	account_no = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'E.g 7001100800101'}))
	message = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'E.G type your message here'}))
	