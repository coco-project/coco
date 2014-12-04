from django.conf.urls import patterns, url


""
urlpatterns = patterns('',
    # /accounts/...
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {
            'template_name': 'wui/user/login.html',
            'extra_context': {
                'title': 'Login'
            }
        }
    ),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    # /container(s)/...
    url(r'^containers/$', 'ipynbsrv.wui.views.containers.index', name='containers'),
    # url(r'^container/backup$', 'ipynbsrv.wui.views.containers.backup', name='container::backup'),
    # url(r'^container/clone$', 'ipynbsrv.wui.views.containers.clone', name='containers'),
    url(r'^containers/create$', 'ipynbsrv.wui.views.containers.create', name='container_create'),
    # url(r'^container/delete$', 'ipynbsrv.wui.views.containers.delete', name='containers'),
    # url(r'^container/edit$', 'ipynbsrv.wui.views.containers.edit', name='containers'),
    # url(r'^container/restore$', 'ipynbsrv.wui.views.containers.restore', name='containers'),
    # url(r'^container/share$', 'ipynbsrv.wui.views.containers.share', name='containers'),
    url(r'^containers/stop$', 'ipynbsrv.wui.views.containers.stop', name='container_stop'),
    url(r'^containers/start$', 'ipynbsrv.wui.views.containers.start', name='container_start'),

    # # /images(s)/...
    url(r'^images/$', 'ipynbsrv.wui.views.images.index', name='images'),
    # # url(r'^image/create$', 'ipynbsrv.wui.views.images.create', name='image::create'),
    # # url(r'^image/delete$', 'ipynbsrv.wui.views.images.delete', name='image::delete'),
    # # url(r'^image/edit$', 'ipynbsrv.wui.views.images.edit', name='image::edit'),
    # url(r'^image/share$', 'ipynbsrv.wui.views.images.share', name='image::share'),

    # /share(s)/...
    url(r'^shares/$', 'ipynbsrv.wui.views.shares.index', name='shares'),
    # url(r'^share/accept$', 'ipynbsrv.wui.views.shares.index', name='share_accept'),
    url(r'^share/adduser$', 'ipynbsrv.wui.views.shares.adduser', name='share_adduser'),
    url(r'^share/create$', 'ipynbsrv.wui.views.shares.create', name='share_create'),
    # url(r'^share/decline$', 'ipynbsrv.wui.views.shares.index', name='share_decline'),
    url(r'^share/delete$', 'ipynbsrv.wui.views.shares.delete', name='share_delete'),
    # url(r'^share/invite$', 'ipynbsrv.wui.views.shares.index', name='share_invite'),
    url(r'^share/leave$', 'ipynbsrv.wui.views.shares.index', name='share_leave'),
    url(r'^share/manage/(\d+)$', 'ipynbsrv.wui.views.shares.index', name='share_manage'),

    # /
    url(r'^$', 'ipynbsrv.wui.views.common.dashboard', name='dashboard'),
)
