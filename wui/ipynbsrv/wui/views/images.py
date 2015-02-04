from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Image, Container
from django.contrib import messages
from django.db.models import Q


@user_passes_test(login_allowed)
def index(request):
    return render(request, 'wui/images/index.html', {
        'title': 'Images',
        'containers': Container.objects.filter(owner=request.user),
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True)) & Q(is_clone=False))
    })


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
