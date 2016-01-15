from coco.core.models import PortMapping
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse


COOKIE_NAME = 'username'
URI_HEADER = 'HTTP_X_ORIGINAL_URI'


def login_allowed(user):
    """
    @user_passes_test decorator to check whether the user is allowed to access the application or not.

    We do not want to allow non-UserBackend users to access the application
    (because we need the LDAP entry for the shares etc.) so we check that here.
    """
    if user is None or user.get_username() is None:  # AnonymousUser
        return False
    return hasattr(user, 'backend_user')  # not super = internal only user


def workspace_auth_access(request):
    """
    This view is called by Nginx to check either a user is authorized to
    access a given workspace or not.

    The username can be obtained from the signed cookie 'username',
    while the port/container needs to be extracted from the 'X-Original-URI' header.

    Response codes of 20x will allow the user to access the requested resource.
    """
    if request.method == "GET":
        username = request.get_signed_cookie(COOKIE_NAME, default=None)
        if username:  # ensure the signed cookie set at login is there
            try:
                user = User.objects.get(username=username)
                uri = request.META.get(URI_HEADER)
                if uri:  # ensure the X- header is present. its set by Nginx
                    subdirectory_parts = 0
                    if settings.SUBDIRECTORY != "":
                        subdirectory_parts = settings.SUBDIRECTORY.split('/')
                    splits = uri.split('/')
                    if len(splits) >= (3 + subdirectory_parts):
                        base_url = splits[2 + subdirectory_parts]
                        parts = base_url.decode('hex').split(':')
                        internal_ip = parts[0]
                        port = parts[1]
                        mapping = PortMapping.objects.filter(external_port=port).filter(server__internal_ip=internal_ip)
                        if mapping.exists() and mapping.first().container.owner == user.backend_user:
                            return HttpResponse(status=200)
            except ObjectDoesNotExist:
                pass

    return HttpResponse(status=403)
