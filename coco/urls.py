'''
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
'''

from coco.admin.admin import admin_site
from django.conf.urls import include, url


urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin_site.urls)),
    url(r'^api/', include('coco.api.urls')),
    url(r'^', include('coco.web.urls'))
]


'''
Registering custom error handlers.
'''
handler404 = 'coco.web.views.system.error_404'
handler500 = 'coco.web.views.system.error_500'