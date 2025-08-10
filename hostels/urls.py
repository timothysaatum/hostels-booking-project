from django.urls import path
from .views import (AboutView, HomeView, Services, user_dashboard, HowItWorks, Mission, HostelsListView, make_booking, 
                    CreateHostel, Management, verify_booking, HostelDelete, HostelUpdate, RoomsListView, RoomTypeCreateView, 
                    make_payment, GeneratePdf, HostelDetailView, VacantRooms, BookingsView, PendingView, ApprovalsView, 
                    SalesStatistics)




urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('hostel/list/', HostelsListView.as_view(), name='rooms'),
    path('hostel/details/<int:pk>/<str:hostel>/', HostelDetailView.as_view(), name='hostel-details'),
    path('rooms/list/<int:pk>/<str:hostel>/', RoomsListView.as_view(), name='room-list'),
    #path('hostel/<int:pk>/<str:room_type>/', RoomDetailView.as_view(), name='room-detail'),
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
    path('admin/dashboard/vacancies/', VacantRooms.as_view(), name='vacancies'),
    path('admin/dashboard/bookings/', BookingsView.as_view(), name='bookings'),
    path('admin/dashboard/pending-leave-request/', PendingView.as_view(), name='pending'),
    path('admin/dashboard/approved-leaves/', ApprovalsView.as_view(), name='approved'),
    path('admin/dashboard/sales/statistics/', SalesStatistics.as_view(), name='statistics'),
    path('booking/receipts/download/', GeneratePdf.as_view(), name='receipt')
]
