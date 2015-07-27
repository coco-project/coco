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
    #url(r'^groups/(?P<pk>[0-9]+)/django_group$', views.CollaborationGroupDjangoGroup.as_view(), name="group_detail_django_group"),

    # /api/backend(s)/...
    url(r'^backends/$', views.BackendList.as_view(), name="backends"),
    url(r'^backends/(?P<pk>[0-9]+)$', views.BackendDetail.as_view(), name="backend_detail"),

    # /api/container(s)/...
    url(r'^containers/$', views.ContainerList.as_view(), name="containers"),
    url(r'^containers/(?P<pk>[0-9]+)$', views.ContainerDetail.as_view(), name="container_detail"),

    url(r'^containers/(?P<pk>[0-9]+)/clone$', views.container_clone, name="container_clone"),
    url(r'^containers/(?P<pk>[0-9]+)/clones$', views.container_clones, name="container_clones"),
    url(r'^containers/(?P<pk>[0-9]+)/create_snapshot$', views.container_create_snapshot, name="container_create_snapshot"),
    url(r'^containers/(?P<pk>[0-9]+)/restart$', views.container_restart, name="container_restart"),
    url(r'^containers/(?P<pk>[0-9]+)/resume$', views.container_resume, name="container_resume"),
    url(r'^containers/(?P<pk>[0-9]+)/start$', views.container_start, name="container_start"),
    url(r'^containers/(?P<pk>[0-9]+)/stop$', views.container_stop, name="container_stop"),
    url(r'^containers/(?P<pk>[0-9]+)/suspend$', views.container_suspend, name="container_suspend"),

    # /api/image(s)/...
    url(r'^images/$', views.ContainerImageList.as_view(), name="images"),
    url(r'^images/(?P<pk>[0-9]+)$', views.ContainerImageDetail.as_view(), name="image_detail"),

    # /api/snapshot(s)/...
    url(r'^snapshots/$', views.ContainerSnapshotList.as_view(), name="snapshot"),
    url(r'^snapshots/(?P<pk>[0-9]+)$', views.ContainerSnapshotDetail.as_view(), name="snapshot_detail"),

    # /api/server(s)/...
    url(r'^servers/$', views.ServerList.as_view(), name="servers"),
    url(r'^servers/(?P<pk>[0-9]+)$', views.ServerDetail.as_view(), name="server_detail"),

    # /api/share(s)/...
    url(r'^shares/$', views.ShareList.as_view(), name="shares"),
    url(r'^shares/(?P<pk>[0-9]+)$', views.ShareDetail.as_view(), name="share_detail"),

    # /api/tag(s)/...
    url(r'^tags/$', views.TagList.as_view(), name="tags"),
    url(r'^tags/(?P<pk>[0-9]+)$', views.TagDetail.as_view(), name="tag_detail"),

    # /api/notification(s)/...
    url(r'^notifications/$', views.NotificationList.as_view(), name="notifications"),
    url(r'^notifications/(?P<pk>[0-9]+)$', views.NotificationDetail.as_view(), name="notification_detail"),

    # /api/notificationlog(s)/...
    url(r'^notificationlogs/$', views.NotificationLogList.as_view(), name="notificationlogs"),
    url(r'^notificationlogs/(?P<pk>[0-9]+)$', views.NotificationLogDetail.as_view(), name="notificationlog_detail"),

)
urlpatterns = format_suffix_patterns(urlpatterns)