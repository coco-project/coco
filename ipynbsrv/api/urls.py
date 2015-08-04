from django.conf.urls import patterns, url
from ipynbsrv.api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns('',
    url(r'^$', views.api_root),

    # /api/user(s)/...
    url(r'^users/$', views.UserList.as_view(), name="users"),
    url(r'^users/(?P<pk>[0-9]+)$', views.UserDetails.as_view(), name="user_details"),

    # /api/configurationvariable(s)/...
    url(r'^configurationvariables/$', views.ConfigurationVariableList.as_view(), name="configurationvariables"),
    url(r'^configurationvariables/(?P<pk>[0-9]+)$', views.ConfigurationVariableDetail.as_view(), name="configurationvariables_detail"),

    # /api/collaborationgroup(s)/...
    url(r'^collaborationgroups/$', views.CollaborationGroupList.as_view(), name="collaborationgroups"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)$', views.CollaborationGroupDetail.as_view(), name="collaborationgroup_detail"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/add_members$', views.collaborationgroup_add_members, name="collaborationgroup_add_members"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/add_admins$', views.collaborationgroup_add_admins, name="collaborationgroup_add_admins"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/remove_members$', views.collaborationgroup_remove_members, name="collaborationgroup_remove_members"),

    # /api/backend(s)/...
    url(r'^backends/$', views.BackendList.as_view(), name="backends"),
    url(r'^backends/(?P<pk>[0-9]+)$', views.BackendDetail.as_view(), name="backend_detail"),

    # /api/container(s)/...
    url(r'^containers/$', views.ContainerList.as_view(), name="containers"),
    url(r'^containers/(?P<pk>[0-9]+)$', views.ContainerDetail.as_view(), name="container_detail"),

    url(r'^containers/(?P<pk>[0-9]+)/clone$', views.container_clone, name="container_clone"),
    url(r'^containers/(?P<pk>[0-9]+)/clones$', views.container_clones, name="container_clones"),
    url(r'^containers/(?P<pk>[0-9]+)/commit$', views.container_commit, name="container_commit"),
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
    url(r'^shares/(?P<pk>[0-9]+)/add_access_groups$', views.share_add_access_groups, name="share_add_access_groups"),
    url(r'^shares/(?P<pk>[0-9]+)remove_access_groups$', views.share_remove_access_groups, name="share_remove_access_groups"),

    # /api/tag(s)/...
    url(r'^tags/$', views.TagList.as_view(), name="tags"),
    url(r'^tags/(?P<pk>[0-9]+)$', views.TagDetail.as_view(), name="tag_detail"),
    url(r'^tags/(?P<label_text>.+)/$', views.TagList.as_view(), name="tag_by_name"),

    # /api/notification(s)/...
    url(r'^notifications/$', views.NotificationList.as_view(), name="notifications"),
    url(r'^notifications/(?P<pk>[0-9]+)$', views.NotificationDetail.as_view(), name="notification_detail"),
    url(r'^notificationtypes/$', views.notification_types, name="notification_types"),

    # /api/notificationlog(s)/...
    url(r'^notificationlogs/$', views.NotificationLogList.as_view(), name="notificationlogs"),
    url(r'^notificationlogs/(?P<pk>[0-9]+)$', views.NotificationLogDetail.as_view(), name="notificationlog_detail"),

)
urlpatterns = format_suffix_patterns(urlpatterns)
