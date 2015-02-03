from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from ipynbsrv.wui.auth.checks import login_allowed


COOKIE_NAME = 'username'


"""
The flag view is called after a successful user login.

Since we use Nginx, which does a subrequest, to check authorization of workspace access,
we need a way to identify the user there. So we bypass here to create a signed cookie
for that purpose.
"""
@user_passes_test(login_allowed)
def flag(request):
    response = HttpResponseRedirect('/')
    response.set_signed_cookie(COOKIE_NAME, request.user.username, httponly=True)
    return response


"""
The unflag view is called before a user is actually logged out.

We use that chance to remove the cookie we created after his login
which authorizes him to access his workspaces.
"""
@user_passes_test(login_allowed)
def unflag(request):
    response = HttpResponseRedirect('/accounts/logout')
    response.delete_cookie(COOKIE_NAME)
    return response
