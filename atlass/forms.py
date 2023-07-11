from .models import LeaveRequests
from django import forms


class RequestToLeaveForm(forms.ModelForm):

	class Meta:

		model = LeaveRequests
		fields = ['your_course', 'level', 'phone_number', 'purpose', 'i_affirm_everything_in_my_room_is_intact']