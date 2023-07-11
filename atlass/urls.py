from django.urls import path
from .views import DeleteBooking, RequestToLeave

urlpatterns = [
	path('<int:pk>/delete', DeleteBooking.as_view(), name='delete-booking'),
	path('request-to-leave/', RequestToLeave.as_view(), name='request-to-leave')
]