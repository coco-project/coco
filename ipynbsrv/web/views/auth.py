from django.contrib.auth.views import login
from ipynbsrv.web.api_client_proxy import set_session_password


def ipynbsrv_login(request, *args, **kwargs):
    # execute default login
    response = login(request, *args, **kwargs)

    # if sucessful, store user & password in session for use in API HttpClient
    if response:
        set_session_password(request)
    return response
