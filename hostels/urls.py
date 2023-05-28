from django.urls import path
from .views import (HostelDetailView, about, home,
                    services,
                    dashboard, howitworks,
                    mission, RoomsListView,
                    make_booking, CreateHostel)


urlpatterns = [
    path('', home, name='home'),
    path('rooms/', RoomsListView.as_view(), name='rooms'),
    path('hostel/create/', CreateHostel.as_view(), name='create'),
    path('hostel/<int:pk>/', HostelDetailView.as_view(), name='hostel-detail'),
    path('services/', services, name='services'),
    path('how-it-works/', howitworks, name="howitworks"),
    path('mission/', mission, name='mission'),
    path('about/', about, name='about'),
    path('booking/summary', dashboard, name='booking-details'),
    path('rooms/request-to-book/<int:pk>/', make_booking, name='pay'),
]
