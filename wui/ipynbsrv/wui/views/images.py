from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.signals.images import *
from ipynbsrv.wui.models import Image, Container
from django.contrib import messages
from django.db.models import Q


""
@user_passes_test(login_allowed)
def index(request):
    c = Container.objects.filter(owner=request.user)
    i = Image.objects.filter((Q(owner=request.user)|Q(is_public=True))&Q(is_clone=False))
    context = {
        'title': 'Images',
	'images': i,
	'conts' : c,
	'owner' : request.user
    }
    return render(request, 'wui/images/index.html', context)


@user_passes_test(login_allowed)
def delete(request):
    id = request.POST.get('id')
    i = Image.objects.filter(owner=request.user).filter(img_id=id).first()
    i.delete()
    messages.success(request, 'Image ' + i.name + ' successfully deleted')
    return redirect('images')


@user_passes_test(login_allowed)
def commit(request):
    ct_name = request.POST.get('ct_name')
    name = request.POST.get('name')
    description = request.POST.get('description')
    public = request.POST.get('public')
    if public=="True":
	is_public=True
    else:
	is_public=False

    c = Container.objects.filter(owner=request.user).filter(name=ct_name).get()
    i = Image(cmd=c.image.cmd, ports=c.image.ports, name=name, description=description, owner=request.user, is_public=is_public)
    imgname = str(c.owner) + "_" + name
    container_commited.send(sender='', image=i, ct_id=c.ct_id, name=imgname)
    i.save()
    return redirect('images')

