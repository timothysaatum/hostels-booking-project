from django.urls import path
from .views import (RoomDetailView, AboutView, HomeView, Services, 
                    user_dashboard, HowItWorks,
                    Mission, HostelsListView, make_booking, 
                    CreateHostel, Management, verify_booking, HostelDelete, 
                    HostelUpdate, RoomsListView, RoomTypeCreateView, make_payment, GeneratePdf)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
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
    path('about/', AboutView.as_view(), name='about'),
    path('user/dashboard/', user_dashboard, name='booking-details'),
    path('rooms/request-to-book/<int:pk>/<int:room_pk>', make_booking, name='pay'),
    path('room/pay/<int:pk>/', make_payment, name="book"),
    path('admin/dashboard/', Management.as_view(), name='management'),
    path('verify-payment/<str:ref>/', verify_booking, name='verify'),
    path('booking/receipts/download/', GeneratePdf.as_view(), name='receipt')
]
