from django.contrib.auth.models import User
from django.http.response import HttpResponse
from ipynbsrv.wui.models import Container, LdapUser


"""
@user_passes_test decorator callback that checks either the
passed in user is allowed to access the application or not.

We do not want to allow non-LDAP users to access the application
(because we need the LDAP entry for the shares etc.) so we check that here.
"""
def login_allowed(user):
    return user.is_active and LdapUser.objects.filter(pk=user.username).exists()


"""
This view is called by Nginx to check either a user is authorized to
access a given workspace or not.

The username can be obtained from the signed cookie 'username',
while the port/container needs to be extracted from the 'X-Original-URI' header.

Response codes of 20x will allow the user to access the requested resource.
"""
def workspace_auth(request):
    if request.method == "GET":
        username = request.get_signed_cookie('username', default=None)
        if username:  # ensure the signed cookie set at login is there
            user = User.objects.filter(username=username).first()
            if user:  # ensure the user really exists
                uri = request.META.get('HTTP_X_ORIGINAL_URI')
                if uri:  # ensure the X- header is present. its set by Nginx
                    splits = uri.split('/')
                    if len(splits) >= 4:
                        port = splits[2]
                        container = Container.objects.filter(exposeport=port).first()
                        if container and container.owner == user:
                            return HttpResponse(status=200)

    return HttpResponse(status=403)
