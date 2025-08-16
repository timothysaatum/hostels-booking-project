from django.urls import path
from . import views

app_name = 'hostels'

urlpatterns = [
    # Public views
    path('', views.HostelListView.as_view(), name='hostel_list'),
    path('hostel/<slug:slug>/', views.HostelDetailView.as_view(), name='hostel-detail'),
    path('hostel/<slug:hostel_slug>/contact/', views.ContactInquiryCreateView.as_view(), name='contact-inquiry'),
    
    # Owner management views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('create/', views.HostelCreateView.as_view(), name='hostel-create'),
    path('hostel/<slug:slug>/edit/', views.HostelUpdateView.as_view(), name='hostel-update'),
    path('hostel/<slug:slug>/delete/', views.HostelDeleteView.as_view(), name='hostel-delete'),
    
    # Room type management
    path('hostel/<slug:hostel_slug>/room-types/', views.HostelRoomTypesView.as_view(), name='hostel-room-types'),
    path('hostel/<slug:hostel_slug>/room-types/add/', views.RoomTypeCreateView.as_view(), name='roomtype-create'),
    path('room-type/<int:pk>/edit/', views.RoomTypeUpdateView.as_view(), name='roomtype-update'),
    path('room-type/<int:pk>/delete/', views.RoomTypeDeleteView.as_view(), name='roomtype-delete'),
    
    # Inquiry management
    path('inquiries/', views.InquiryListView.as_view(), name='inquiry-list'),
    path('inquiry/<int:pk>/', views.InquiryDetailView.as_view(), name='inquiry-detail'),
    path('inquiry/<int:inquiry_id>/contacted/', views.mark_inquiry_contacted, name='mark-inquiry-contacted'),
    
    # Utility endpoints
    path('finish-setup/<slug:hostel_slug>/', views.finish_hostel_setup, name='finish-hostel-setup'),
    path('get-location/', views.get_current_location, name='get-current-location'),
]