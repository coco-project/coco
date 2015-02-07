from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # /accounts/...
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {
        'template_name': 'wui/user/login.html',
        'extra_context': {
            'title': "Login"
        }
    }),
    url(r'^accounts/flag/$', 'ipynbsrv.wui.views.accounts.create_cookie', name='accounts_flag'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='accounts_logout'),
    url(r'^accounts/unflag/$', 'ipynbsrv.wui.views.accounts.remove_cookie', name='accounts_unflag'),

    # /container(s)/...
    url(r'^containers/$', 'ipynbsrv.wui.views.containers.index', name='containers'),
    url(r'^container/clone$', 'ipynbsrv.wui.views.containers.clone', name='container_clone'),
    url(r'^container/commit$', 'ipynbsrv.wui.views.containers.commit', name='container_commit'),
    url(r'^container/create$', 'ipynbsrv.wui.views.containers.create', name='container_create'),
    url(r'^container/delete$', 'ipynbsrv.wui.views.containers.delete', name='container_delete'),
    url(r'^container/restart$', 'ipynbsrv.wui.views.containers.restart', name='container_restart'),
    url(r'^container/share$', 'ipynbsrv.wui.views.containers.share', name='container_share'),
    url(r'^container/start$', 'ipynbsrv.wui.views.containers.start', name='container_start'),
    url(r'^container/stop$', 'ipynbsrv.wui.views.containers.stop', name='container_stop'),

    # # /images(s)/...
    url(r'^images/$', 'ipynbsrv.wui.views.images.index', name='images'),
    url(r'^image/delete$', 'ipynbsrv.wui.views.images.delete', name='image_delete'),

    # /share(s)/...
    url(r'^shares/$', 'ipynbsrv.wui.views.shares.index', name='shares'),
    url(r'^share/add_user$', 'ipynbsrv.wui.views.shares.add_user', name='share_add_user'),
    url(r'^share/create$', 'ipynbsrv.wui.views.shares.create', name='share_create'),
    url(r'^share/delete$', 'ipynbsrv.wui.views.shares.delete', name='share_delete'),
    url(r'^share/leave$', 'ipynbsrv.wui.views.shares.leave', name='share_leave'),
    url(r'^share/manage/(\d+)$', 'ipynbsrv.wui.views.shares.manage', name='share_manage'),
    url(r'^share/remove_user$', 'ipynbsrv.wui.views.shares.remove_user', name='share_remove_user'),

    # internal
    url(r'^_workspace_auth_check$', 'ipynbsrv.wui.auth.checks.workspace_auth_access'),
    url(r'^error/404$', 'ipynbsrv.wui.views.system.error_404'),
    url(r'^error/500$', 'ipynbsrv.wui.views.system.error_500'),

    # /
    url(r'^$', 'ipynbsrv.wui.views.common.dashboard', name='dashboard'),
)
