from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from ipynbsrv.conf.helpers import *
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Container, ContainerImage, Server
from random import randint


@user_passes_test(login_allowed)
def clone(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user:
            container.clone()
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def commit(request):
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

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user:
            if ContainerImage.objects.filter(name=img_name).filter(owner=request.user).exists():
                messages.error(request, "An image with that name already exists.")
            else:
                container.commit(img_name=img_name, description=description, public=(public == "on"))
                messages.success(request, "Sucessfully created the image.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Selected base container does not exist.")

    return redirect('images')


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'name' not in request.POST or 'description' not in request.POST or 'image_id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    name = request.POST.get('name')
    description = request.POST.get('description')
    image_id = int(request.POST.get('image_id'))

    if Container.objects.filter(name=name).filter(owner=request.user.backend_user).exists():
        messages.error(request, "A container with that name already exists.")
    else:
        image = ContainerImage.objects.filter(pk=image_id)
        if image.exists():
            image = image.first()
            if image.owner == request.user or image.is_public:
                # pick a host server via the selection algorithm
                server = get_server_selection_algorithm().choose_server(
                    Server.objects.all().iterator()
                )
                container = Container(backend_pk=randint(0, 1000), name=name, description=description, server=server, owner=request.user.backend_user, image=image)
                container.save()
                # container.start()
                messages.success(request, "Container created successfully.")
            else:
                messages.error(request, "You don't have enough permissions for the requested operation.")
        else:
            messages.error(request, "Container bootstrap image does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user.backend_user:
            container.delete()
            messages.success(request, "Container deleted successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def index(request):
    containers = Container.objects.filter(owner=request.user.backend_user)
    return render(request, 'web/containers/index.html', {
        'title': "Containers",
        'containers': containers,
        'images': ContainerImage.objects.filter((Q(owner=request.user) | Q(is_public=True)))
    })


@user_passes_test(login_allowed)
def restart(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user.backend_user:
            container.restart()
            messages.success(request, "Container restarted successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def start(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user.backend_user:
            container.start()
            messages.success(request, "Container started successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def stop(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = int(request.POST.get('id'))

    container = Container.objects.filter(pk=ct_id)
    if container.exists():
        container = container.first()
        if container.owner == request.user.backend_user:
            container.stop()
            messages.success(request, "Container stopped successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')
