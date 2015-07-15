from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect
from ipynbsrv.core.auth.checks import login_allowed
from ipynbsrv.core.models import Container, Image


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
        img = img.first()
        if img.owner == request.user:
            img.delete()
            messages.success(request, "Image deleted successfully.")
        else:
            messages.error(request, "You don't have enough permissions for the requested operation.")
    else:
        messages.error(request, "Image does not exist.")

    return redirect('images')


@user_passes_test(login_allowed)
def index(request):
    return render(request, 'web/images/index.html', {
        'title': "Images",
        'containers': Container.objects.filter(owner=request.user),
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True))),
        # meta information for the create modal
        'selected': Container.objects.filter(pk=int(request.GET.get('ct', -1))).first(),
        'share': 'share' in request.GET
    })
