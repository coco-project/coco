from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # /accounts/...
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {
            'template_name': 'wui/user/login.html',
            'extra_context': {
                'title': 'Login'
            }
        }
    ),
    url(r'^accounts/flag/$', 'ipynbsrv.wui.views.accounts.flag', name='accounts_flag'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='accounts_logout'),
    url(r'^accounts/unflag/$', 'ipynbsrv.wui.views.accounts.unflag', name='accounts_unflag'),

    # /container(s)/...
    url(r'^containers/$', 'ipynbsrv.wui.views.containers.index', name='containers'),
    url(r'^containers/clone$', 'ipynbsrv.wui.views.containers.clone', name='containers_clone'),
    url(r'^containers/create$', 'ipynbsrv.wui.views.containers.create', name='container_create'),
    url(r'^containers/delete$', 'ipynbsrv.wui.views.containers.delCont', name='containers_delete'),
    url(r'^containers/stop$', 'ipynbsrv.wui.views.containers.stop', name='container_stop'),
    url(r'^containers/start$', 'ipynbsrv.wui.views.containers.start', name='container_start'),
    url(r'^containers/restart$', 'ipynbsrv.wui.views.containers.restart', name='container_restart'),
    url(r'^containers/share$', 'ipynbsrv.wui.views.containers.share', name='containers_share'),

    # # /images(s)/...
    url(r'^images/$', 'ipynbsrv.wui.views.images.index', name='images'),
    url(r'^images/commit$', 'ipynbsrv.wui.views.images.commit', name='image_commit'),
    url(r'^images/delete$', 'ipynbsrv.wui.views.images.delete', name='image_delete'),
    # url(r'^image/edit$', 'ipynbsrv.wui.views.images.edit', name='image::edit'),
    # url(r'^image/share$', 'ipynbsrv.wui.views.images.share', name='image::share'),

    # /share(s)/...
    url(r'^shares/$', 'ipynbsrv.wui.views.shares.index', name='shares'),
    url(r'^share/add_user$', 'ipynbsrv.wui.views.shares.add_user', name='share_add_user'),
    url(r'^share/create$', 'ipynbsrv.wui.views.shares.create', name='share_create'),
    url(r'^share/delete$', 'ipynbsrv.wui.views.shares.delete', name='share_delete'),
    url(r'^share/leave$', 'ipynbsrv.wui.views.shares.leave', name='share_leave'),
    url(r'^share/manage/(\d+)$', 'ipynbsrv.wui.views.shares.manage', name='share_manage'),
    url(r'^share/remove_user$', 'ipynbsrv.wui.views.shares.remove_user', name='share_remove_user'),

    # workspace auth check url
    # Nginx/OpenResty will query this URL for each request to /workspace/...
    # to ensure the user is allowed to access it
    # we therefor need to check the user and user = container owner in there
    url(r'^_workspace_auth_check$', 'ipynbsrv.wui.views.common.workspace_auth_check', name='workspace_auth_check'),

    # /
    url(r'^$', 'ipynbsrv.wui.views.common.dashboard', name='dashboard'),
)
