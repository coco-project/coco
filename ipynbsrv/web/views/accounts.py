from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.web import settings


@user_passes_test(login_allowed)
def create_cookie(request):
    '''
    The flag view is called after a successful user login.

    Since we use Nginx, which does a subrequest to check authorization of workspace access,
    we need a way to identify the user there. So we bypass here to create a signed cookie
    for that purpose.
    '''
    response = HttpResponseRedirect(reverse('dashboard'))
    response.set_signed_cookie(settings.AUTH_COOKIE_NAME, request.user.username, httponly=True)
    return response


@user_passes_test(login_allowed)
def remove_cookie(request):
    '''
    The unflag view is called before a user is actually logged out.

    We use that chance to remove the cookie we created after his login
    which authorizes him to access his workspaces.
    '''
    response = HttpResponseRedirect(reverse('accounts_logout'))
    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    return response
