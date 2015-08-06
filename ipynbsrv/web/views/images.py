from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from ipynbsrv.web.views._messages import api_error_message
from slumber.exceptions import HttpNotFoundError


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    img_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        image = client.images(img_id).get()
    except HttpNotFoundError:
        messages.error(request, "Image does not exist or you don't have the permissions to delete it.")

    if image:
        try:
            client.images(img_id).delete()
            messages.success(request, "Image deleted successfully.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Image does not exist or you don't have the permissions to delete it.")

    return redirect('images')


@user_passes_test(login_allowed)
def index(request):
    client = get_httpclient_instance(request)

    containers = client.containers.get()
    images = client.images.get()
    if request.GET.get('ct'):
        selected = client.containers(int(request.GET.get('ct'))).get()
    else:
        selected = None
    new_notifications_count = len(client.notificationlogs.unread.get())

    return render(request, 'web/images/index.html', {
        'title': "Images",
        'containers': containers,
        'images': images,
        # meta information for the create modal
        'selected': selected,
        'share': 'share' in request.GET,
        'new_notifications_count': new_notifications_count
    })
