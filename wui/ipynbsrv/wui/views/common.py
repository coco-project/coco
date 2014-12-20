from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from ipynbsrv.wui.auth.checks import login_allowed


"""
Dashboard view
URI: /
"""
@user_passes_test(login_allowed)
def dashboard(request):
    return render(request, 'wui/dashboard.html', {
        'title':  "Dashboard"
    })
