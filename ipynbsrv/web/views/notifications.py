from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Notification, NotificationLog
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from ipynbsrv.web.views._messages import api_error_message


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    client = get_httpclient_instance(request)
    notificationlogs = client.notificationlogs.get()
    notificationtypes = client.notificationtypes.get()
    groups = client.collaborationgroups.get()
    containers = client.containers.get()
    container_images = client.images.get()
    shares = client.shares.get()

    return render(request, 'web/notifications/index.html', {
        'title': "Notifications",
        'notifications': notificationlogs,
        'notification_types': notificationtypes,
        'groups': groups,
        'containers': containers,
        'container_images': container_images,
        'shares': shares
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('notifications')
    # Todo: validate POST params: receiver_group, msg, type, rel objs
    if 'receiver_groups' not in request.POST or 'message' not in request.POST or 'notification_type' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('notifications')

    client = get_httpclient_instance(request)

    params = {}
    params["message"] = request.POST.get('message', '')
    params["notification_type"] = request.POST.get('notification_type', '')
    params["sender"] = request.user.id
    params["container"] = request.POST.get('container', None)
    params["container_image"] = request.POST.get('container_image', None)
    params["share"] = request.POST.get('share', None)
    params["group"] = request.POST.get('group', None)
    params["receiver_groups"] = [int(request.POST.get('receiver_groups', None))]

    client.notifications.get()
    try:
        client.notifications.post(params)
        messages.success(request, "Notification sucessfully created.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))

    return redirect('notifications')
