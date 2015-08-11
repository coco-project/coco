from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from ipynbsrv.web.views._messages import api_error_message
from slumber.exceptions import HttpNotFoundError


@user_passes_test(login_allowed)
def create_snapshot(request):
    """
    Todo: write doc.
    Todo: get name & description param from GUI.
    """
    print(request.POST)
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'ct_id' not in request.POST or 'name' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('ct_id'))
    params = {}
    params['name'] = request.POST.get('name', '')
    description = request.POST.get('description', '')
    if description:
        params['description'] = description

    client = get_httpclient_instance(request)

    # create snapshot
    try:
        client.containers(ct_id).create_snapshot.post(params)
        messages.success(request, "Sucessfully created snapshot `{}`.".format(params.get('name')))
    except Exception as e:
            messages.error(request, api_error_message(e, params))

    return redirect('container_snapshots', ct_id)


@user_passes_test(login_allowed)
def clone(request):
    """
    Todo: write doc.
    Todo: get name & description param from GUI.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    params = {}

    ct_id = int(request.POST.get('id'))
    client = get_httpclient_instance(request)
    container = client.containers(ct_id).get()
    params['name'] = "{}_clone".format(container.name)

    # create clone
    try:
        client.containers(ct_id).clone.post(params)
        messages.success(request, "Sucessfully created the clone `{}`.".format(params.get('name')))
    except Exception as e:
            messages.error(request, api_error_message(e, params))

    return redirect('containers')


@user_passes_test(login_allowed)
def commit(request):
    """
    Todo: write doc.
    """

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'ct_id' not in request.POST or 'img_name' not in request.POST or 'description' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    params = {}
    ct_id = int(request.POST.get('ct_id'))
    params["name"] = request.POST.get('img_name')
    params["description"] = request.POST.get('description')
    params["public"] = request.POST.get('public', "") == "on"

    client = get_httpclient_instance(request)
    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Selected base container does not exist.")
    except Exception:
        messages.error(request, "Some other error.")

    if container:
        try:
            client.containers(ct_id).commit.post(params)
            messages.success(request, "Sucessfully created the image.")
        except Exception as e:
            messages.error(request, api_error_message(e, params))
            return redirect('images')
    else:
        messages.error(request, "Selected base container does not exist.")

    return redirect('images')


@user_passes_test(login_allowed)
def create(request):
    """
    Todo: write doc.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'name' not in request.POST or 'description' not in request.POST or 'image_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    params = {}
    params["name"] = request.POST.get('name')
    params["description"] = request.POST.get('description')
    params["image"] = int(request.POST.get('image_id'))

    client = get_httpclient_instance(request)

    try:
        image = client.containers.images(params.get('image_id')).get()
    except HttpNotFoundError:
        messages.error(request, "Container bootstrap image does not exist or you don't have enough permissions for the requested operation.")
    except Exception as ex:
        messages.error(request, api_error_message(ex, params))

    if image:
        try:
            # server and owner get set by the core automatically
            client.containers.post(params)
            messages.success(request, "Container created successfully.")
        except Exception as ex:
            messages.error(request, api_error_message(ex, params))

    return redirect('containers')


@user_passes_test(login_allowed)
def delete(request):
    """
    Todo: write doc.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id)
    except HttpNotFoundError:
        messages.error(request, "Container does not exist, or you don't have permissions to delete it.")

    if container:
        try:
            client.containers(ct_id).delete()
            messages.success(request, "Container deleted successfully.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def index(request):
    """
    Get a list of all containers and render it.
    """
    client = get_httpclient_instance(request)
    # containers = Container.objects.filter(owner=request.user.backend_user)
    containers = client.containers.get()
    images = client.containers.images.get()
    new_notifications_count = len(client.notificationlogs.unread.get())

    return render(request, 'web/containers/index.html', {
        'title': "Containers",
        'containers': containers,
        'images': images,
        'new_notifications_count': new_notifications_count
    })


@user_passes_test(login_allowed)
def restart(request):
    """
    Todo: write doc.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container does not exist.")

    if container:
        try:
            client.containers(ct_id).restart.post()
            messages.success(request, "Container is now restarting.")
        except Exception as e:
            messages.error(request,  api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def start(request):
    """
    Todo: write doc.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container does not exist.")

    if container:
        try:
            client.containers(ct_id).start.post()
            messages.success(request, "Container is now starting up.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def stop(request):
    """
    Todo: write doc.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container does not exist.")

    if container:
        try:
            client.containers(ct_id).stop.post()
            messages.success(request, "Container is shutting down.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def suspend(request):
    """
    Suspend the container.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container does not exist.")

    if container:
        try:
            client.containers(ct_id).suspend.post()
            messages.success(request, "Container is going into suspended mode.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def resume(request):
    """
    Resume the container
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container does not exist.")

    if container:
        try:
            client.containers(ct_id).resume.post()
            messages.success(request, "Container is resuming.")
        except Exception as e:
            messages.error(request, api_error_message(e, ""))
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def restore_snapshot(request):
    """
    Todo: write doc.
    Todo: get name & description param from GUI.
    """
    print(request.POST)
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST or 'ct_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('ct_id'))
    params = {}
    params['id'] = int(request.POST.get('id'))

    client = get_httpclient_instance(request)

    # create snapshot
    try:
        client.containers(ct_id).restore_snapshot.post(params)
        messages.success(request, "Sucessfully restored snapshot `{}`.".format(params.get('name')))
    except Exception as e:
            messages.error(request, api_error_message(e, params))

    return redirect('container_snapshots', ct_id)


@user_passes_test(login_allowed)
def delete_snapshot(request):
    """
    Todo: write doc.
    """
    print(request.POST)
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST or 'ct_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    snapshot_id = int(request.POST.get('id'))
    params = {}
    params['id'] = snapshot_id
    ct_id = params['ct_id'] = int(request.POST.get('ct_id'))

    client = get_httpclient_instance(request)

    # create snapshot
    try:
        client.containers.snapshots(snapshot_id).delete()
        messages.success(request, "Sucessfully deleted snapshot.")
    except Exception as e:
            messages.error(request, api_error_message(e, params))

    return redirect('container_snapshots', ct_id)
