from django.conf.urls import patterns, url
from ipynbsrv.wui import views


urlpatterns = patterns('',
    # /
    url(r'^$', views.login, name='login'),
    url(r'^dashboard/$',  views.dashboard,  name='dashboard'),
    url(r'^containers/$', views.containers, name='containers'),
    url(r'^images/$',     views.images,     name='images'),
    url(r'^shares/$',     views.shares,     name='shares'),
)
