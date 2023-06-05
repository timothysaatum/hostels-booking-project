from django.urls import path
from .views import (HostelDetailView, about, home,
                    Services,
                    dashboard, HowItWorks,
                    Mission, RoomsListView,
                    make_booking, CreateHostel, hostel_manager, tenants, verify_booking)


urlpatterns = [
    path('', home, name='home'),
    path('rooms/', RoomsListView.as_view(), name='rooms'),
    path('hostel/create/', CreateHostel.as_view(), name='create'),
    path('hostel/<int:pk>/', HostelDetailView.as_view(), name='hostel-detail'),
    path('services/', Services.as_view(), name='services'),
    path('how-it-works/', HowItWorks.as_view(), name="howitworks"),
    path('mission/', Mission.as_view(), name='mission'),
    path('about/', about, name='about'),
    path('booking/summary', dashboard, name='booking-details'),
    path('rooms/request-to-book/<int:pk>/', make_booking, name='pay'),
    path('property/management', hostel_manager, name='management'),
    path('property/tenants', tenants, name='tenants'),
    path('verify-payment/<str:ref>/', verify_booking, name='verify')
]
