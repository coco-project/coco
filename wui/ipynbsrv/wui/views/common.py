from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponse
from django.shortcuts import render
from ipynbsrv.wui.auth.checks import login_allowed


""
@user_passes_test(login_allowed)
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }

    return render(request, 'wui/dashboard.html', context)


"""
"""
def workspace_auth_check(request):
    # TODO
    print request.user
    print request.path
    print request

    return HttpResponse(status=200)
