from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container

"""
Dashboard view
URI: /
"""
@user_passes_test(login_allowed)
def dashboard(request):
    c = Container.objects.filter(owner=request.user).filter(status=True)
    return render(request, 'wui/dashboard.html', {
        'title':  "Dashboard",
	'containers' : c
    })
