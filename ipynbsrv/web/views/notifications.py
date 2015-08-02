from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Notification, NotificationLog
from ipynbsrv.web.api_client_proxy import get_httpclient_instance


@user_passes_test(login_allowed)
def index(request):
    """
    Shares listing/index.
    """
    client = get_httpclient_instance(request)
    notificationlogs = client.notificationlogs.get()
    notificationtypes = client.notificationtypes.get()
    groups = client.collaborationgroups.get()

    return render(request, 'web/notifications/index.html', {
        'title': "Notifications",
        'notifications': notificationlogs,
        'notification_types': notificationtypes,
        'groups': groups
    })


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('notifications')
    # Todo: validate POST params: receiver_group, msg, type, rel objs
    if 'recipient' not in request.POST or 'message' not in request.POST or 'event_type' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('notifications')

    # Todo: call API to create Notification
    group_id = request.POST.get('recipient')
    group = Group.objects.get(id=group_id)
    message = request.POST.get('message', '')
    event_type = request.POST.get('event_type', '')
    sender = request.user
    date = datetime.now()

    notification = Notification(sender=sender, message=message, event_type=event_type, date=date)
    notification.save()

    messages.success(request, "Notification sucessfully sent.")

    return redirect('notifications')
