from django.urls import path
from .views import (HostelDetailView, about, home, contact,
     food, HostelListView,
     category_500_1000,
     BookingDetailView, 
     category_1100_1500, category_1600_2000, make_booking)



urlpatterns = [
    #hostels views
    path('', home, name='home'),
    path('rooms/', HostelListView.as_view(), name='rooms'),
    path('hostel/<int:pk>/', HostelDetailView.as_view(), name='hostel-detail'),
    path('category_500_1000/', category_500_1000, name='category_500_1000'),
    path('category_1100_1500/', category_1100_1500, name='category_1100_1500'),
    path('category_1600_2000/', category_1600_2000, name='category_1600_2000'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('food/', food, name='food'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking-details'),
    path('rooms/pay/<int:pk>/', make_booking, name='pay'),
]
