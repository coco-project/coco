from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container


@user_passes_test(login_allowed)
def dashboard(request):
    """
    Dashboard view listing the running containers.
    """
    return render(request, 'wui/dashboard.html', {
        'title':  "Dashboard",
        'containers': Container.objects.filter(owner=request.user).filter(running=True)
    })
