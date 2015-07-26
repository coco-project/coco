from django.conf.urls import patterns, url
from ipynbsrv.api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns('',
    url(r'^$', views.api_root),

    # /api/user(s)/...
    url(r'^users/$', views.UserList.as_view(), name="users"),

    # /api/group(s)/...
    url(r'^groups/$', views.CollaborationGroupList.as_view(), name="groups"),
    url(r'^groups/(?P<pk>[0-9]+)$', views.CollaborationGroupDetail.as_view(), name="group_detail"),

    # /api/backend(s)/...
    url(r'^backends/$', views.BackendList.as_view(), name="backends"),

    # /api/container(s)/...
    url(r'^containers/$', views.ContainerList.as_view(), name="containers"),

    # /api/image(s)/...
    url(r'^images/$', views.ContainerImageList.as_view(), name="images"),

    # /api/snapshot(s)/...
    url(r'^snapshot/$', views.ContainerSnapshotList.as_view(), name="snapshot"),

    # /api/server(s)/...
    url(r'^servers/$', views.ServerList.as_view(), name="servers"),

    # /api/share(s)/...
    url(r'^shares/$', views.ShareList.as_view(), name="shares"),

    # /api/tag(s)/...
    url(r'^tags/$', views.TagList.as_view(), name="tags"),

    # /api/notification(s)/...
    url(r'^notifications/$', views.NotificationList.as_view(), name="notifications"),

    # /api/notificationlog(s)/...
    url(r'^notificationlogs/$', views.NotificationLogList.as_view(), name="notificationlogs"),

)
urlpatterns = format_suffix_patterns(urlpatterns)