from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container, Image


@user_passes_test(login_allowed)
def clone(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = request.POST.get('id')

    container = Container.objects.filter(id=ct_id)
    if container.exists():
        if container.owner == request.user:
            container.clone()
        else:
            messages.error(request, "You don't have permissions to clone that container.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def commit(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'ct_name' not in request.POST or 'name' not in request.POST or 'description' not in request.POST or 'public' not in request.POST:
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
                container.commit(img_name=name, description=description, public=public == "True", clone=False)
                messages.success(request, "Sucessfully created the image.")
        else:
            messages.error(request, "You don't have permissions to commit that container.")
    else:
        messages.error(request, "Selected base container does not exist.")

    return redirect('images')


@user_passes_test(login_allowed)
def create(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('images')
    if 'name' not in request.POST or 'description' not in request.POST or 'image' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('images')

    name = request.user.get_username() + '_' + request.POST.get('name')
    description = request.POST.get('description')
    image = request.POST.get('image')

    if Container.objects.filter(name=name).exists():
        image = Image.objects.filter(name=image)
        if image.exists():
            container = Container(id=randint(0, 1000), name=name, description=description, image=image.first(),
                                  owner=request.user, running=False, clone_of=None)
            container.save()
            container.start()
            messages.success(request, "Container created successfully.")
        else:
            messages.error(request, "Container base image does not exist.")
    else:
        messages.error(request, "A container with that name already exists.")

    return redirect('containers')


@user_passes_test(login_allowed)
def delete(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = request.POST.get('id')

    container = Container.objects.filter(id=ct_id)
    if container.exists():
        if container.owner == request.user:
            container.delete()
            messages.success(request, "Container stopped successfully.")
        else:
            messages.error(request, "You don't have permissions to stop that container.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def index(request):
    return render(request, 'wui/containers/index.html', {
        'title': "Containers",
        'containers': Container.objects.filter(owner=request.user),
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True)) & Q(is_clone=False))
    })


@user_passes_test(login_allowed)
def restart(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = request.POST.get('id')

    container = Container.objects.filter(id=ct_id)
    if container.exists():
        if container.owner == request.user:
            container.restart()
            messages.success(request, "Container restarted successfully.")
        else:
            messages.error(request, "You don't have permissions to stop that container.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')


@user_passes_test(login_allowed)
def share(request):
    return redirect('images')


@user_passes_test(login_allowed)
def start(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('containers')
    if 'id' not in request.POST:
        messages.error(request, "Invalid POST request.")
        return redirect('containers')

    ct_id = request.POST.get('id')

    container = Container.objects.filter(id=ct_id)
    if container.exists():
        if container.owner == request.user:
            container.start()
            messages.success(request, "Container started successfully.")
        else:
            messages.error(request, "You don't have permissions to start that container.")
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

    ct_id = request.POST.get('id')

    container = Container.objects.filter(id=ct_id)
    if container.exists():
        if container.owner == request.user:
            container.stop()
            messages.success(request, "Container stopped successfully.")
        else:
            messages.error(request, "You don't have permissions to stop that container.")
    else:
        messages.error(request, "Container does not exist.")

    return redirect('containers')
