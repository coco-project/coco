from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from django.shortcuts import render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Container
from ipynbsrv.web import settings
from ipynbsrv.web.api_client_proxy import get_httpclient_instance


@user_passes_test(login_allowed)
def dashboard(request):
    '''
    Dashboard view listing the running containers.
    '''

    client = get_httpclient_instance(request)
    containers = client.containers.get()

    return render(request, 'web/dashboard.html', {
        'title': "Dashboard",
        'containers': containers
    })


def workspace_auth_access(request):
    '''
    This view is called by Nginx to check either a user is authorized to
    access a given workspace or not.

    The username can be obtained from the signed cookie 'username',
    while the port/container needs to be extracted from the 'X-Original-URI' header.

    Response codes of 20x will allow the user to access the requested resource.
    '''

    """
    Todo: rewrite
    """
#    if request.method == "GET":
#        username = request.get_signed_cookie(settings.AUTH_COOKIE_NAME, default=None)
#        if username:  # ensure the signed cookie set at login is there
#            try:
#                user = User.objects.get(username=username)
#                uri = request.META.get(settings.PROXY_URI_HEADER)
#                if uri:  # ensure the X- header is present. its set by Nginx
#                    splits = uri.split('/')
#                    if len(splits) >= 3:
#                        port = splits[2]
#                        mapping = PortMapping.objects.filter(external=port)
#                        if mapping.exists() and mapping.first().container.owner == user:
#                            return HttpResponse(status=200)
#            except ObjectDoesNotExist:
#                pass
#
    return HttpResponse(status=403)
