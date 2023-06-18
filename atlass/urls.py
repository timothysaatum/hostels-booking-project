from django.urls import path
from .views import DeleteBooking

urlpatterns = [
	path('delete/<int:pk>/', DeleteBooking.as_view(), name='delete-booking'),
]