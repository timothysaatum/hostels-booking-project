from django.urls import path
from .views import (RoomDetailView, about, home, Services, 
                    dashboard, HowItWorks,
                    Mission, HostelsListView, make_booking, 
                    CreateHostel, hostel_manager, 
                    tenants, verify_booking, HostelDelete, 
                    HostelUpdate, RoomsListView, RoomTypeCreateView)


urlpatterns = [
    path('', home, name='home'),
    path('hostel/list/', HostelsListView.as_view(), name='rooms'),
    path('rooms/list/<int:pk>/<str:hostel>/', RoomsListView.as_view(), name='room-list'),
    path('hostel/<int:pk>/<str:room_type>/', RoomDetailView.as_view(), name='room-detail'),
    path('hostel/room-type/create/', RoomTypeCreateView.as_view(), name='room-create'),
    path('hostel/create/', CreateHostel.as_view(), name='create'),
    path('hostel/rooms/<int:pk>/delete/', HostelDelete.as_view(), name='hostel-delete'),
    path('hostel/<int:pk>/update/', HostelUpdate.as_view(), name='hostel-update'),
    path('services/', Services.as_view(), name='services'),
    path('how-it-works/', HowItWorks.as_view(), name="howitworks"),
    path('mission/', Mission.as_view(), name='mission'),
    path('about/', about, name='about'),
    path('booking/summary/', dashboard, name='booking-details'),
    path('rooms/request-to-book/<int:pk>/<int:room_pk>', make_booking, name='pay'),
    path('property/management/', hostel_manager, name='management'),
    path('property/tenants/', tenants, name='tenants'),
    path('verify-payment/<str:ref>/', verify_booking, name='verify')
]
