from coco.web.api_client_proxy import set_session_password
from django.contrib.auth.views import login


def coco_login(request, *args, **kwargs):
    # execute default login
    response = login(request, *args, **kwargs)

    # if sucessful, store user & password in session for use in API HttpClient
    if response:
        set_session_password(request)
    return response
