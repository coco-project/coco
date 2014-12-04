from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.models import Container, Host
from ipynbsrv.wui.signals.container_handlers import *
from django.contrib import messages
from django.shortcuts import redirect

""
@login_required
def index(request):
    c = Container.objects.all()
    context = {
        'title': 'Containers',
    	'containers' : c
    }

    return render(request, 'wui/containers.html', context)

@login_required
def stop(request):
    c = Container.objects.all().filter(ct_id='28a5242a4a69').get(pk=1)
    container_stopped.send(sender='', container=c)
    c.status = False
    c.save()
    print("stopped")
    print(c.ct_id)
    messages.success(request, 'Container ' + c.name + ' successfully stopped')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})


@login_required
def start(request):
    c = Container.objects.all().filter(ct_id='28a5242a4a69').get(pk=1)
    container_started.send(sender='', container=c)
    c.status = True
    c.save()
    messages.success(request, 'Container ' + c.name + ' successfully started')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})

@login_required
def restartContainer(request):
    #container_stopped.send(sender=self.__class__,)
    #container_started.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})

@login_required
def get(request):
    return render(request, 'wui/containers.html',{})

@login_required
def delContainer(request):
    #container_deleted.send(sender=self.__class__,)
    #c = Container.objects.all.filter(ct_id=id).get(pk=1)
    #c.delete()
    return render(request, 'wui/containers.html',{})

@login_required
def create(request):
    name = request.POST.get('name')
    c = Container(name=name, description=request.POST.get('description'))
    container_created.send(sender='', container=c)
    c.save()
    return render(request, 'wui/containers.html',{})

@login_required
def commitContainer(request):
    #container_backuped.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})
