from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest
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
    if request.method != "POST":
        uri = request.META.get('X_Original_URI', None)
        if uri:
            print uri
            print request.user
            return HttpResponse(status=200)
        else:
            print request.META

    return HttpResponse(status=403)
