from coco.api import views
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns('',
    url(r'^$', views.api_root),

    # /api/users(/)...
    url(r'^users/?$', views.UserList.as_view(), name="users"),
    url(r'^users/?(?P<pk>[0-9]+)$', views.UserDetail.as_view(), name="user_details"),

    # /api/configurationvariables(/)...
    url(r'^configurationvariables/?$', views.ConfigurationVariableList.as_view(), name="configurationvariables"),
    url(r'^configurationvariables/(?P<pk>[0-9]+)$', views.ConfigurationVariableDetail.as_view(), name="configurationvariables_detail"),

    # /api/collaborationgroups(/)...
    url(r'^collaborationgroups/?$', views.CollaborationGroupList.as_view(), name="collaborationgroups"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)$', views.CollaborationGroupDetail.as_view(), name="collaborationgroup_detail"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/add_members$', views.collaborationgroup_add_members, name="collaborationgroup_add_members"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/remove_members$', views.collaborationgroup_remove_members, name="collaborationgroup_remove_members"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/join$', views.collaborationgroup_join, name="collaborationgroup_join"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/leave$', views.collaborationgroup_leave, name="collaborationgroup_leave"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/add_admins$', views.collaborationgroup_add_admins, name="collaborationgroup_add_admins"),
    url(r'^collaborationgroups/(?P<pk>[0-9]+)/remove_admins$', views.collaborationgroup_remove_admins, name="collaborationgroup_remove_admins"),

    # /api/backends(/)...
    url(r'^backends/?$', views.BackendList.as_view(), name="backends"),
    url(r'^backends/(?P<pk>[0-9]+)$', views.BackendDetail.as_view(), name="backend_detail"),

    # /api/containers(/)...
    url(r'^containers/?$', views.ContainerList.as_view(), name="containers"),
    url(r'^containers/(?P<pk>[0-9]+)$', views.ContainerDetail.as_view(), name="container_detail"),

    url(r'^containers/(?P<pk>[0-9]+)/clone$', views.container_clone, name="container_clone"),
    url(r'^containers/(?P<pk>[0-9]+)/clones$', views.container_clones, name="container_clones"),
    url(r'^containers/(?P<pk>[0-9]+)/snapshots/?$', views.ContainerSnapshotsList.as_view(), name="container_snapshots"),
    url(r'^containers/(?P<pk>[0-9]+)/commit$', views.container_commit, name="container_commit"),
    url(r'^containers/(?P<pk>[0-9]+)/create_snapshot$', views.container_create_snapshot, name="container_create_snapshot"),
    url(r'^containers/(?P<pk>[0-9]+)/restart$', views.container_restart, name="container_restart"),
    url(r'^containers/(?P<pk>[0-9]+)/resume$', views.container_resume, name="container_resume"),
    url(r'^containers/(?P<pk>[0-9]+)/start$', views.container_start, name="container_start"),
    url(r'^containers/(?P<pk>[0-9]+)/stop$', views.container_stop, name="container_stop"),
    url(r'^containers/(?P<pk>[0-9]+)/suspend$', views.container_suspend, name="container_suspend"),

    # /api/container/images(/)...
    url(r'^containers/images/?$', views.ContainerImageList.as_view(), name="images"),
    url(r'^containers/images/(?P<pk>[0-9]+)$', views.ContainerImageDetail.as_view(), name="image_detail"),
    url(r'^containers/images/(?P<pk>[0-9]+)/add_access_groups$', views.image_add_access_groups, name="image_add_access_groups"),
    url(r'^containers/images/(?P<pk>[0-9]+)/remove_access_groups$', views.image_remove_access_groups, name="image_remove_access_groups"),

    # /api/container/snapshots(/)...
    url(r'^containers/snapshots/?$', views.ContainerSnapshotList.as_view(), name="snapshot"),
    url(r'^containers/snapshots/(?P<pk>[0-9]+)$', views.ContainerSnapshotDetail.as_view(), name="snapshot_detail"),
    url(r'^containers/snapshots/(?P<pk>[0-9]+)/restore$', views.container_snapshot_restore, name="container_snapshot_restore"),

    # /api/servers(/)...
    url(r'^servers/?$', views.ServerList.as_view(), name="servers"),
    url(r'^servers/(?P<pk>[0-9]+)$', views.ServerDetail.as_view(), name="server_detail"),

    # /api/shares(/)...
    url(r'^shares/?$', views.ShareList.as_view(), name="shares"),
    url(r'^shares/(?P<pk>[0-9]+)$', views.ShareDetail.as_view(), name="share_detail"),
    url(r'^shares/(?P<pk>[0-9]+)/add_access_groups$', views.share_add_access_groups, name="share_add_access_groups"),
    url(r'^shares/(?P<pk>[0-9]+)/remove_access_groups$', views.share_remove_access_groups, name="share_remove_access_groups"),

    # /api/tags(/)...
    url(r'^tags/?$', views.TagList.as_view(), name="tags"),
    url(r'^tags/(?P<pk>[0-9]+)$', views.TagDetail.as_view(), name="tag_detail"),
    url(r'^tags/by_name/(?P<label_text>.+)/$', views.TagList.as_view(), name="tag_by_name"),

    # /api/notifications(/)...
    url(r'^notifications/?$', views.NotificationList.as_view(), name="notifications"),
    url(r'^notifications/(?P<pk>[0-9]+)$', views.NotificationDetail.as_view(), name="notification_detail"),

    # /api/notificationtypes(/)..
    url(r'^notificationtypes/?$', views.notification_types, name="notification_types"),

    # /api/notificationlogs(/)...
    url(r'^notificationlogs/?$', views.NotificationLogList.as_view(), name="notificationlogs"),
    url(r'^notificationlogs/unread$', views.NotificationLogUnreadList.as_view(), name="notificationlogs_unread"),
    url(r'^notificationlogs/mark_all_as_read$', views.notificationlogs_mark_all_as_read, name="notificationlogs_mark_all_as_read"),
    url(r'^notificationlogs/(?P<pk>[0-9]+)$', views.NotificationLogDetail.as_view(), name="notificationlog_detail"),

)
urlpatterns = format_suffix_patterns(urlpatterns)
