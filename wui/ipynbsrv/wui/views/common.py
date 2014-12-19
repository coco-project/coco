from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from djproxy.views import HttpProxy
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container


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
        splits = request.path.split('/')
        if len(splits) >= 3:
            container = Container.objects.filter(ports=splits[2]).first()
            if container:
                if container.owner == request.user:
                    return super(WorkspaceProxy, self).dispatch(request, *args, **kwargs)
                else:
                    messages.error(request, "You have no permissions to access this container.")
            else:
                messages.error(request, "Container does not exist.")
        else:
            messages.error(request, "Invalid URL.")

        return redirect('containers')
