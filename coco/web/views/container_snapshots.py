from coco.core.auth.checks import login_allowed
from coco.web.api_client_proxy import get_httpclient_instance
from coco.web.views._messages import api_error_message
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


@user_passes_test(login_allowed)
def index(request, ct_id):
    """
    Get a list of all snapshots for this container.
    """
    client = get_httpclient_instance(request)
    container = client.containers(ct_id).get()
    container_snapshots = client.containers(ct_id).snapshots.get()
    new_notifications_count = len(client.notificationlogs.unread.get())

    return render(request, 'web/container_snapshots/index.html', {
        'title': "Container Snapshots",
        'container_snapshots': container_snapshots,
        'container': container,
        'new_notifications_count': new_notifications_count
    })
