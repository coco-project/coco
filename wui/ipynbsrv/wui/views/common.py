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


@user_passes_test(login_allowed)
class WorkspaceProxy(HttpProxy):
    """
    """
    base_url = settings.WORKSPACE_PROXY_URL


    """
    """
    def dispatch(self, request, *args, **kwargs):
        # TODO: check if user is allowed here
        return super(WorkspaceProxy, self).dispatch(request, *args, **kwargs)
