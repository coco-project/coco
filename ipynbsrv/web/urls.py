from django.conf.urls import url


urlpatterns = [
    # /accounts/...
    url(r'^accounts/login/$', 'ipynbsrv.web.views.auth.ipynbsrv_login', {
        'template_name': 'web/user/login.html',
        'extra_context': {
            'title': "Login"
        }
    }, name='accounts_login'),
    url(r'^accounts/flag/$', 'ipynbsrv.web.views.accounts.create_cookie', name='accounts_flag'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='accounts_logout'),
    url(r'^accounts/unflag/$', 'ipynbsrv.web.views.accounts.remove_cookie', name='accounts_unflag'),

    # /group(s)/...
    url(r'^groups/$', 'ipynbsrv.web.views.collaborationgroups.index', name='groups'),
    url(r'^groups/create$', 'ipynbsrv.web.views.collaborationgroups.create', name='group_create'),
    url(r'^groups/delete$', 'ipynbsrv.web.views.collaborationgroups.delete', name='group_delete'),
    url(r'^groups/manage/(\d+)$', 'ipynbsrv.web.views.collaborationgroups.manage', name='group_manage'),
    url(r'^groups/remove_user$', 'ipynbsrv.web.views.collaborationgroups.remove_member', name='group_remove_member'),
    url(r'^groups/add_admin$', 'ipynbsrv.web.views.collaborationgroups.add_admin', name='group_add_admin'),
    url(r'^groups/add_users$', 'ipynbsrv.web.views.collaborationgroups.add_members', name='group_add_members'),

    # /container(s)/...
    url(r'^containers/$', 'ipynbsrv.web.views.containers.index', name='containers'),
    url(r'^container/clone$', 'ipynbsrv.web.views.containers.clone', name='container_clone'),
    url(r'^container/commit$', 'ipynbsrv.web.views.containers.commit', name='container_commit'),
    url(r'^container/create$', 'ipynbsrv.web.views.containers.create', name='container_create'),
    url(r'^container/delete$', 'ipynbsrv.web.views.containers.delete', name='container_delete'),
    url(r'^container/restart$', 'ipynbsrv.web.views.containers.restart', name='container_restart'),
    url(r'^container/start$', 'ipynbsrv.web.views.containers.start', name='container_start'),
    url(r'^container/stop$', 'ipynbsrv.web.views.containers.stop', name='container_stop'),

    # # /images(s)/...
    url(r'^images/$', 'ipynbsrv.web.views.images.index', name='images'),
    url(r'^image/delete$', 'ipynbsrv.web.views.images.delete', name='image_delete'),

    # /share(s)/...
    url(r'^shares/$', 'ipynbsrv.web.views.shares.index', name='shares'),
    url(r'^share/add_user$', 'ipynbsrv.web.views.shares.add_user', name='share_add_user'),
    url(r'^share/create$', 'ipynbsrv.web.views.shares.create', name='share_create'),
    url(r'^share/delete$', 'ipynbsrv.web.views.shares.delete', name='share_delete'),
    url(r'^share/leave$', 'ipynbsrv.web.views.shares.leave', name='share_leave'),
    url(r'^share/manage/(\d+)$', 'ipynbsrv.web.views.shares.manage', name='share_manage'),
    url(r'^share/remove_user$', 'ipynbsrv.web.views.shares.remove_user', name='share_remove_user'),

    # /notification(s)/...
    url(r'^notifications/$', 'ipynbsrv.web.views.notifications.index', name='notifications'),
    url(r'^notifications/create$', 'ipynbsrv.web.views.notifications.create', name='notification_create'),

    # internal
    url(r'^_workspace_auth_check$', 'ipynbsrv.web.views.common.workspace_auth_access'),
    url(r'^error/404$', 'ipynbsrv.web.views.system.error_404'),
    url(r'^error/500$', 'ipynbsrv.web.views.system.error_500'),

    # /
    url(r'^$', 'ipynbsrv.web.views.common.dashboard', name='dashboard')
]
