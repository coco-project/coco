from coco.core.auth.checks import login_allowed
from coco.web.api_client_proxy import get_httpclient_instance
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


@user_passes_test(login_allowed)
def dashboard(request):
    '''
    Dashboard view listing the running containers.
    '''

    client = get_httpclient_instance(request)
    containers = client.containers.get()
    new_notifications_count = len(client.notificationlogs.unread.get())

    return render(request, 'web/dashboard.html', {
        'title': "Dashboard",
        'containers': filter(lambda ct: ct.is_running is True, containers),
        'new_notifications_count': new_notifications_count
    })
