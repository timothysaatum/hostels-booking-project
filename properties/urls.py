from django.urls import path
from .views import Lands, Appartment, Recreational

urlpatterns = [
	path('lands-and-businesses/', Lands.as_view(), name='lands'),
	path('travellers-and-workers/', Appartment.as_view(), name='appartment'),
	path('recreational', Recreational.as_view(), name='recreational')
]