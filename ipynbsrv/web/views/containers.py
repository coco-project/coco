from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Container, ContainerImage, Server
from ipynbsrv.web.api_client_proxy import get_httpclient_instance
from slumber.exceptions import HttpNotFoundError


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

    ct_id = int(request.POST.get('id'))
    client = get_httpclient_instance(request)
    container = client.containers(ct_id).get()
    new_name = "{}_clone".format(container.name)

    # create clone
    client.containers(ct_id).clone.post({"name": new_name})

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

    ct_id = int(request.POST.get('ct_id'))
    img_name = request.POST.get('img_name')
    description = request.POST.get('description')
    public = request.POST.get('public', "")

    client = get_httpclient_instance(request)
    try:
        container = client.containers(ct_id).get()
    except HttpNotFoundError:
        messages.error(request, "Selected base container does not exist.")
    except Exception:
        messages.error(request, "Some other error.")

    print("container found")

    if container:
        client.containers(ct_id).commit.post({
            "name": img_name,
            "description": description,
            "public": (public == "on"),
            })
        messages.success(request, "Sucessfully created the image.")
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

    name = request.POST.get('name')
    description = request.POST.get('description')
    image_id = int(request.POST.get('image_id'))

    client = get_httpclient_instance(request)

    try:
        image = client.images(image_id).get()
    except HttpNotFoundError:
        messages.error(request, "Container bootstrap image does not exist or you don't have enough permissions for the requested operation.")

    if image:
        try:
            # does not make any sense, but seems like it won't work without this line
            # Todo: find the actual problem!
            client.containers.get()

            # server and owner get set by the core automatically
            client.containers.post({
                "name": name,
                "description": description,
                "image": image_id
                })
            messages.success(request, "Image created successfully.")
        except Exception as ex:
            messages.error(request, ex)
            messages.error(request, "Whuups, something went wrong :(.")

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
        except Exception:
            messages.error(request, "Whuups, something went wrong :(.")
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
    images = client.images.get()
    return render(request, 'web/containers/index.html', {
        'title': "Containers",
        'containers': containers,
        'images': images
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
            messages.success(request, "Container is restarting.")
        except Exception as e:
            print(e)
            messages.error(request, "Whuups, something went wrong :(.")
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
            messages.success(request, "Container is starting.")
        except Exception:
            messages.error(request, "Whuups, something went wrong :(.")
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
            messages.success(request, "Container stopped successfully.")
        except Exception:
            messages.error(request, "Whuups, something went wrong :(.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')
