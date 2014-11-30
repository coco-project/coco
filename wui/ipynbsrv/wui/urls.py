from django.conf.urls import patterns, url
from ipynbsrv.wui import views


urlpatterns = patterns('',
    # /
    url(r'^$',                      views.login,      name='login'),
    url(r'^dashboard/$',            views.dashboard,  name='dashboard'),
    url(r'^containers/$',           views.containers, name='containers'),
    url(r'^images/$',               views.images,     name='images'),
    url(r'^shares/$',               views.shares,     name='shares'),
    url(r'^profile/notifications$', views.profile_notifications, name='profile/notifications'),
    url(r'^profile/preferences$',   views.profile_preferences,   name='profile/preferences'),
)
