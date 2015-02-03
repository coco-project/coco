from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, render
from ipynbsrv.wui.auth.checks import login_allowed
from ipynbsrv.wui.models import Container, Image
from ipynbsrv.wui.signals.containers import *


""
@user_passes_test(login_allowed)
def index(request):
    return render(request, 'wui/containers/index.html', {
        'title': "Containers",
        'containers': Container.objects.filter(owner=request.user),
        'images': Image.objects.filter((Q(owner=request.user) | Q(is_public=True)) & Q(is_clone=False))
    })


@user_passes_test(login_allowed)
def stop(request):
    c = Container.objects.filter(owner=request.user).filter(ct_id=request.POST.get('id')).first()
    try:
        c.status = False
        c.save()
        messages.success(request, 'Container ' + c.name + ' successfully stopped')
    except:
    messages.error(request, "Cant Stop non-existing Container")
    c.delete()
    pass
    return redirect('containers')


@user_passes_test(login_allowed)
def start(request):
    c = Container.objects.filter(owner=request.user).filter(ct_id=request.POST.get('id')).get()
    try:
    c.status = True
        c.save()
        messages.success(request, 'Container ' + c.name + ' successfully stopped')
    except:
    messages.error(request, "Cant Start non-existing Container")
    c.delete()
    pass
    return redirect('containers')


@user_passes_test(login_allowed)
def restart(request):
    c = Container.objects.filter(owner=request.user).filter(ct_id=request.POST.get('id')).get()
    try:
        container_restarted.send(sender='', container=c)
        messages.success(request, 'Container ' + c.name + ' successfully restarted')
    except:
    messages.error(request, "Cant Restart non-existing Container")
    c.delete()
    pass
    return redirect('containers')



@user_passes_test(login_allowed)
def delCont(request):
    c = Container.objects.filter(ct_id=request.POST.get('id')).get()
    c.delete()
    if c.is_clone:
    c.image.delete()
    messages.success(request, 'Container ' + c.name + ' successfully deleted')
    return redirect('containers')


@user_passes_test(login_allowed)
def create(request):
    i = Image.objects.filter(name=request.POST.get('image')).get()
    container = Container.objects.order_by('exposeport')
    if container.count() == 0:
    portid = 49152
    else:
        cont = container.last()
        portid = int(cont.exposeport)+1
    name = request.POST.get('name')
    c = Container(name=name, description=request.POST.get('description'), owner=request.user, image=i, status=True, exposeport=portid)
    container_created.send(sender='', container=c, image=i)
    c.save()
    messages.success(request, 'Container ' + c.name + ' successfully created')
    return redirect('containers')


@user_passes_test(login_allowed)
def clone(request):
    ct_id = request.POST.get('id')
    name = str(request.POST.get('name'))
    cont = Container.objects.filter(owner=request.user).filter(ct_id=ct_id).first()
    i = Image(cmd=cont.image.cmd, ports=cont.image.ports, name=name+"_clone", description='Clone', is_clone=True, owner=request.user)
    container_commited.send(sender='', image=i, ct_id=ct_id, name=str(request.user)+"_"+name+"_clone")
    i.save()
    container = Container.objects.order_by('exposeport')
    if container.count() == 0:
    portid = 49152
    else:
        conta = container.last()
        portid = int(conta.exposeport)+len(cont.image.ports.split(','))+1
    c = Container(name=name+"_clone", description='Clone', is_clone=True, owner=request.user, status=True, image=i, exposeport=portid)
    container_created.send(sender='',container=c, image=i)
    c.save()
    return redirect('containers')

@user_passes_test(login_allowed)
def share(request):
    return redirect('images')
