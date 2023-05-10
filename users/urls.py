from django.urls import path
from .import views
from django.contrib.auth import views as auth_views



urlpatterns = [
	path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('complain/', views.ComplainView.as_view(), name='complain'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy-policy/', views.PrivacyPolicy.as_view(), name='privacy'),
    path('faqs/', views.FAQs.as_view(), name='faqs'),
    path('data-handling', views.DataHandlingView.as_view(), name='data'),
    path('terms-and-conditions', views.TermsAndConditions.as_view(), name='terms_and_conditions'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', views.profile, name='profile'),
]

