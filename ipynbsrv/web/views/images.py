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
    if 'id' not in request.POST or not request.POST.get('id').isdigit():
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    img_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        image = client.containers.images(img_id).get()
    except HttpNotFoundError:
        messages.error(request, "Image does not exist or you don't have the permissions to delete it.")

    if image:
        try:
            client.containers.images(img_id).delete()
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
    images = client.containers.images.get()
    new_notifications_count = len(client.notificationlogs.unread.get())

    return render(request, 'web/images/index.html', {
        'title': "Images",
        'containers': containers,
        'images': images,
        'new_notifications_count': new_notifications_count,
        'request': request.GET
    })


@user_passes_test(login_allowed)
def manage(request, image_id):
    client = get_httpclient_instance(request)
    image = client.containers.images(image_id).get()
    new_notifications_count = len(client.notificationlogs.unread.get())
    image['access_group_ids'] = [g.id for g in image.access_groups]
    users = client.users.get()
    groups = client.collaborationgroups.get()

    return render(request, 'web/images/manage.html', {
        'title': "Image",
        'image': image,
        'users': users,
        'groups': groups,
        'new_notifications_count': new_notifications_count
    })


@user_passes_test(login_allowed)
def add_access_groups(request):

    """
    Add access groups to the image.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'id' not in request.POST or not request.POST.get('id').isdigit() or 'access_groups' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    access_groups = request.POST.getlist('access_groups')
    img_id = request.POST.get('id')
    client = get_httpclient_instance(request)

    params = {}
    params['access_groups'] = access_groups

    try:
        response = client.containers.images(img_id).add_access_groups.post(params)
        count = response.get('count')
        if count == 0:
            messages.info(request, "{} groups successfully added to the image.".format(count))
        elif count == 1:
            messages.success(request, "{} group successfully added to the image.".format(count))
        else:
            messages.success(request, "{} groups successfully added to the image.".format(count))
    except Exception as e:
        messages.error(request, api_error_message(e, params))

    return redirect('image_manage', img_id)


@user_passes_test(login_allowed)
def remove_access_group(request):

    """
    Add access groups to the image.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'id' not in request.POST or not request.POST.get('id').isdigit() or 'access_group' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    group_id = request.POST.get('access_group')
    img_id = request.POST.get('id')
    client = get_httpclient_instance(request)

    params = {"access_groups": [group_id]}

    try:
        client.containers.images(img_id).remove_access_groups.post(params)
        messages.success(request, "Group successfully removed from image.")
    except Exception as e:
        messages.error(request, api_error_message(e, params))
        return(redirect('image_manage', img_id))

    return redirect('image_manage', img_id)
