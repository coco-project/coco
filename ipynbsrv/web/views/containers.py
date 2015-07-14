from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from ipynbsrv.conf import conf
from ipynbsrv.core.auth.auth import login_allowed
from ipynbsrv.core.models import Container, Image, PortMapping, Server
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
            if Image.objects.filter(name=img_name).filter(owner=request.user).exists():
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

    if Container.objects.filter(name=name).filter(owner=request.user).exists():
        messages.error(request, "A container with that name already exists.")
    else:
        image = Image.objects.filter(pk=image_id)
        if image.exists():
            image = image.first()
            if image.owner == request.user or image.is_public:

                # choose container host
                # TODO: make generic (let user decide which algorithm to choose)
                s = PrimitiveContainerHostSelectionService.get_server(len.Server.objects.all())
                srv = Server.objects.all()[s]

                # TODO: distinct docker_id
                container = Container(docker_id=randint(0, 1000), host=srv.id, name=name, description=description, image=image,
                                      owner=request.user, running=False, clone_of=None)
                container.save()
                container.start()
                messages.success(request, "Container created successfully.")
            else:
                messages.error(request, "You don't have enough permissions for the requested operation.")
        else:
            messages.error(request, "Container base image does not exist.")

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
        if container.owner == request.user:
            container.delete()
            messages.success(request, "Container deleted successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def index(request):
    containers = Container.objects.filter(owner=request.user)
    for container in containers:
            port_mappings = PortMapping.objects.filter(container=container)
            container.port_mappings = port_mappings.filter(~Q(internal=container.image.proxied_port))
            container.workspace_port = port_mappings.filter(internal=container.image.proxied_port).first().external

    return render(request, 'web/containers/index.html', {
        'title': "Containers",
        'containers': containers,
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True)))
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
        if container.owner == request.user:
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
        if container.owner == request.user:
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
        if container.owner == request.user:
            container.stop()
            messages.success(request, "Container stopped successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')
