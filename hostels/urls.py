from django.urls import path
from . import views

app_name = 'hostels'

urlpatterns = [
    # Public hostel browsing
    path('', views.HostelListView.as_view(), name='hostel_list'),
    path('hostel/<slug:slug>/', views.HostelDetailView.as_view(), name='hostel-detail'),
    
    # Owner dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Hostel CRUD
    path('create/', views.HostelCreateView.as_view(), name='hostel-create'),
    path('hostel/<slug:slug>/edit/', views.HostelUpdateView.as_view(), name='hostel-update'),
    path('hostel/<slug:slug>/delete/', views.HostelDeleteView.as_view(), name='hostel-delete'),
    
    # Hostel setup completion
    path('hostel/<slug:hostel_slug>/finish-setup/', 
         views.finish_hostel_setup, name='finish-hostel-setup'),
    
    # Room Type CRUD
    path('hostel/<slug:hostel_slug>/room-type/create/', 
         views.RoomTypeCreateView.as_view(), name='roomtype-create'),
    path('room-type/<int:pk>/edit/', 
         views.RoomTypeUpdateView.as_view(), name='roomtype-update'),
    path('room-type/<int:pk>/delete/', 
         views.RoomTypeDeleteView.as_view(), name='roomtype-delete'),
    
    # Contact inquiries
    path('hostel/<slug:hostel_slug>/contact/', 
         views.ContactInquiryCreateView.as_view(), name='contact-inquiry'),
    path('inquiries/', views.InquiryListView.as_view(), name='inquiry-list'),
    path('inquiry/<int:pk>/', views.InquiryDetailView.as_view(), name='inquiry-detail'),
    path('inquiry/<int:inquiry_id>/mark-contacted/', 
         views.mark_inquiry_contacted, name='mark-inquiry-contacted'),
]