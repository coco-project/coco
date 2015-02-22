from django.conf.urls import include, patterns, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^',       include('ipynbsrv.wui.urls'))
)


handler404 = 'ipynbsrv.wui.views.system.error_404'
handler500 = 'ipynbsrv.wui.views.system.error_500'
