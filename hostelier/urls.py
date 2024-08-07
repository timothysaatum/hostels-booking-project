"""hostelier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
#from hostels.distance import IPAddressFinder



urlpatterns = [
    path('admin/t-23/unarcom/engines/admin/portal/Management/', admin.site.urls),
    path('', include('pwa.urls')),
    path('', include('hostels.urls')),
    path('users/', include('users.urls')),
    path('booking/', include('atlass.urls')),
    path('properties/', include('properties.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    #path('__debug__/', include('debug_toolbar.urls')),
]
#user = IPAddressFinder()

#ip = user.find_user_ip()

#location_data = user.get_user_location(ip)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

admin.site.site_header  =  "Unarcom Management"  
admin.site.site_title  =  "Unarcom Administration"
admin.site.index_title  =  "Unarcom Administration"

