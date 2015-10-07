from django.conf.urls import url


urlpatterns = [
    # /accounts/...
    url(r'^accounts/login/$', 'coco.web.views.auth.coco_login', {
        'template_name': 'web/user/login.html',
        'extra_context': {
            'title': "Login"
        }
    }, name='accounts_login'),
    url(r'^accounts/flag/$', 'coco.web.views.accounts.create_cookie', name='accounts_flag'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='accounts_logout'),
    url(r'^accounts/unflag/$', 'coco.web.views.accounts.remove_cookie', name='accounts_unflag'),

    # /group(s)/...
    url(r'^groups/$', 'coco.web.views.collaborationgroups.index', name='groups'),
    url(r'^groups/create$', 'coco.web.views.collaborationgroups.create', name='group_create'),
    url(r'^groups/delete$', 'coco.web.views.collaborationgroups.delete', name='group_delete'),
    url(r'^groups/manage/(\d+)$', 'coco.web.views.collaborationgroups.manage', name='group_manage'),
    url(r'^groups/remove_member$', 'coco.web.views.collaborationgroups.remove_member', name='group_remove_member'),
    url(r'^groups/leave$', 'coco.web.views.collaborationgroups.leave', name='group_leave'),
    url(r'^groups/join$', 'coco.web.views.collaborationgroups.join', name='group_join'),
    url(r'^groups/add_admin$', 'coco.web.views.collaborationgroups.add_admin', name='group_add_admin'),
    url(r'^groups/remove_admin$', 'coco.web.views.collaborationgroups.remove_admin', name='group_remove_admin'),
    url(r'^groups/add_users$', 'coco.web.views.collaborationgroups.add_members', name='group_add_members'),

    # /container(s)/...
    url(r'^containers/$', 'coco.web.views.containers.index', name='containers'),
    url(r'^container/clone$', 'coco.web.views.containers.clone', name='container_clone'),
    url(r'^container/commit$', 'coco.web.views.containers.commit', name='container_commit'),
    url(r'^container/create_snapshot$', 'coco.web.views.containers.create_snapshot', name='container_create_snapshot'),
    url(r'^container/delete_snapshot$', 'coco.web.views.containers.delete_snapshot', name='container_delete_snapshot'),
    url(r'^container/restore_snapshot$', 'coco.web.views.containers.restore_snapshot', name='container_restore_snapshot'),
    url(r'^container/create$', 'coco.web.views.containers.create', name='container_create'),
    url(r'^container/delete$', 'coco.web.views.containers.delete', name='container_delete'),
    url(r'^container/restart$', 'coco.web.views.containers.restart', name='container_restart'),
    url(r'^container/start$', 'coco.web.views.containers.start', name='container_start'),
    url(r'^container/stop$', 'coco.web.views.containers.stop', name='container_stop'),
    url(r'^container/suspend$', 'coco.web.views.containers.suspend', name='container_suspend'),
    url(r'^container/resume$', 'coco.web.views.containers.resume', name='container_resume'),
    url(r'^container/(\d+)/snapshots$', 'coco.web.views.container_snapshots.index', name='container_snapshots'),


    # # /images(s)/...
    url(r'^images/$', 'coco.web.views.images.index', name='images'),
    url(r'^images/manage/(\d+)$', 'coco.web.views.images.manage', name='image_manage'),
    url(r'^image/delete$', 'coco.web.views.images.delete', name='image_delete'),
    url(r'^image/add_access_groups$', 'coco.web.views.images.add_access_groups', name='image_add_access_groups'),
    url(r'^image/remove_access_group$', 'coco.web.views.images.remove_access_group', name='image_remove_access_group'),

    # /share(s)/...
    url(r'^shares/$', 'coco.web.views.shares.index', name='shares'),
    url(r'^share/add_access_groups$', 'coco.web.views.shares.share_add_access_groups', name='share_add_access_groups'),
    url(r'^share/remove_access_group$', 'coco.web.views.shares.share_remove_access_group', name='share_remove_access_group'),
    url(r'^share/create$', 'coco.web.views.shares.create', name='share_create'),
    url(r'^share/delete$', 'coco.web.views.shares.delete', name='share_delete'),
    url(r'^share/leave$', 'coco.web.views.shares.leave', name='share_leave'),
    url(r'^share/manage/(\d+)$', 'coco.web.views.shares.manage', name='share_manage'),

    # /notification(s)/...
    url(r'^notifications/$', 'coco.web.views.notifications.index', name='notifications'),
    url(r'^notifications/create$', 'coco.web.views.notifications.create', name='notification_create'),
    url(r'^notifications/mark_as_read$', 'coco.web.views.notifications.mark_as_read', name='notification_mark_as_read'),
    url(r'^notifications/mark_all_as_read$', 'coco.web.views.notifications.mark_all_as_read', name='notifications_mark_all_as_read'),

    # internal
    url(r'^_workspace_auth_check$', 'coco.core.auth.checks.workspace_auth_access'),
    url(r'^error/404$', 'coco.web.views.system.error_404'),
    url(r'^error/500$', 'coco.web.views.system.error_500'),

    # /
    url(r'^$', 'coco.web.views.common.dashboard', name='dashboard')
]
