from django.urls import path
from .import views


urlpatterns = [
	path('library/', views.index, name='library-home'),
]
