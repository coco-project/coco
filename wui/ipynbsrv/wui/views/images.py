from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container, Image
from django.contrib import messages
from django.db.models import Q
from ipynbsrv.wui.signals.signals import container_commited
from ipynbsrv.wui.tools import Docker


docker = Docker()


@user_passes_test(login_allowed)
def index(request):
    return render(request, 'wui/images/index.html', {
        'title': 'Images',
        'containers': Container.objects.filter(owner=request.user),
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True)) & Q(is_clone=False))
    })


@user_passes_test(login_allowed)
def commit(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'ct_name' not in request.POST or 'name' not in request.POST or 'description' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    ct_name = request.POST.get('ct_name')
    name = request.user.get_username() + '/' + request.POST.get('name')
    description = request.POST.get('description')
    public = request.POST.get('public')

    container = Container.objects.filter(name=ct_name)
    if container.exists():
        if container.owner == request.user:
            if Image.objects.filter(name=name).exists():
                messages.error(request, "An image with that name already exists.")
            else:
                img_id = docker.commit(container.id, name)['Id']
                image = Image(id=img_id, name=name, description=description, cmd=container.image.cmd,
                              exposed_ports=container.image.exposed_ports, proxied_port=container.image.proxied_port,
                              owner=container.owner, is_public=public == "True", is_clone=False)
                image.save()
                container_commited.send(sender=None, container=container, image=image)

                messages.success(request, "Sucessfully created the image.")
        else:
            messages.error(request, "You don't have permissions to commit that container.")
    else:
        messages.error(request, "Selected base container does not exist.")

    return redirect('images')


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    img_id = int(request.POST.get('id'))

    img = Image.objects.filter(pk=img_id)
    if img.exists():
        if img.owner == request.user:
            img.first().delete()
            messages.success(request, "Image deleted successfully.")
        else:
            messages.error(request, "You don't have permissions to delete that image.")
    else:
        messages.error(request, "Image does not exist.")

    return redirect('images')
