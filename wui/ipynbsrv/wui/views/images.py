from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.signals.images import *
from ipynbsrv.wui.models import Image, Container


""
@user_passes_test(login_allowed)
def index(request):
    c = Container.objects.all()
    i = Image.objects.all()
    context = {
        'title': 'Images',
	'imgs': i,
	'conts' : c
    }
    return render(request, 'wui/images.html', context)


@user_passes_test(login_allowed)
def delete(request):
    id = request.POST.get('id')
    print(id)
    i = Image.objects.all().filter(img_id=id)
    image_deleted.send(sender='', id=id)
    i.delete()
    return redirect('images')
    return render(request, 'wui/images.html', {})


@user_passes_test(login_allowed)
def commit(request):
    ct_name = request.POST.get('ct_name')
    name = request.POST.get('name')
    description = request.POST.get('description')
    c = Container.objects.all().filter(name=ct_name).get()
    i = Image(cmd='/bin/bash', ports=[80], name=name, description=description)
    container_commited.send(sender='', image=i, ct_id=c.ct_id, name=name)
    i.save()
    return redirect('containers')
    return render(request, 'wui/images.html', {})

