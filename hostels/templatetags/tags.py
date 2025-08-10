from django import template
#from django.template.defaultfilters import stringfilter
register = template.Library()
from hostels.models import Hostel


@register.simple_tag
def split_list(value, param):
	param = 'hello'
	return (value + param)