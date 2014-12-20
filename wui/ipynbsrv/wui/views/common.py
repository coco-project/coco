from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container


""
@user_passes_test(login_allowed)
def dashboard(request):
    context = {
        'title': 'Dashboard'
    }

    response = HttpResponse("Hi there")
    response.set_signed_cookie('username', request.user.username)

    return response


"""
"""
def workspace_auth_check(request):
    if request.method == "GET":
        username = request.get_signed_cookie('username', default=None)
        print username
        #user = User.objects.filter(username=username).first()
        if username:
            uri = request.META.get('HTTP_X_ORIGINAL_URI')
            if uri:
                splits = uri.split('/')
                if len(splits) >= 4:
                    port = splits[2]
                    # container = Container.objects.filter(port=port).first()
                    # if container:
                    #     if container.owner == user
                    return HttpResponse(status=200)

    return HttpResponse(status=403)
