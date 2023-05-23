from django.shortcuts import render
from django.views.generic import TemplateView




class Lands(TemplateView):
	template_name = 'properties/lands.html'


class Appartment(TemplateView):
	template_name = 'properties/appartment.html'


class Recreational(TemplateView):
	template_name = 'properties/recreational.html'
