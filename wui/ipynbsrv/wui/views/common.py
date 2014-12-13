from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from djproxy.views import HttpProxy
from ipynbsrv.wui.auth.checks import login_allowed


""
@user_passes_test(login_allowed)
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }

    return render(request, 'wui/dashboard.html', context)


class WorkspaceProxy(HttpProxy):
    """
    """
    base_url = settings.WORKSPACE_PROXY_URL


    """
    """
    def dispatch(self, request, *args, **kwargs):
        # TODO: we need the container ID via param, get the port from it and check if user
        # is allowed to use this container.
        # the reverse proxy expects URLs in the form of /<port>/<uri>
        return super(WorkspaceProxy, self).dispatch(request, *args, **kwargs)
