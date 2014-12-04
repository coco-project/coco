from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.models import Container, Host, Image
from ipynbsrv.wui.signals.container_handlers import *
from django.contrib import messages
from django.shortcuts import redirect

""
@login_required
def index(request):
    c = Container.objects.all()
    i = Image.objects.all()
    context = {
        'title': 'Containers',
    	'containers' : c,
	'images' : i
    }
    
    return render(request, 'wui/containers.html', context)

@login_required
def stop(request):
    c = Container.objects.all().filter(ct_id=request.POST.get('id')).get()
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
    print(request.POST.get('id'))
    c = Container.objects.all().filter(ct_id=request.POST.get('id')).get()
    container_started.send(sender='', container=c)
    c.status = True
    c.save()
    messages.success(request, 'Container ' + c.name + ' successfully started')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})

@login_required
def restart(request):
    c = Container.objects.all().filter(ct_id=request.POST.get('id')).get()
    container_stopped.send(sender='', container=c)
    container_started.send(sender='', container=c)
    messages.success(request, 'Container ' + c.name + ' successfully restarted')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})

@login_required
def get(request):
    return render(request, 'wui/containers.html',{})

@login_required
def delCont(request):
    c = Container.objects.all()
    c = Container.objects.all().filter(ct_id=request.POST.get('id')).get()
    container_deleted.send(sender='',container=c)
    c.delete()
    messages.success(request, 'Container ' + c.name + ' successfully deleted')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})

@login_required
def create(request):
    #i = Image.objects.all().filter(name=request.POST.get('image')).get()
    name = request.POST.get('name')
    print(request.POST.get('image'))
    c = Container(name=name, description=request.POST.get('description'))
    container_created.send(sender='', container=c, image=request.POST.get('image'))
    c.save()
    messages.success(request, 'Container ' + c.name + ' successfully created')
    return redirect('containers')
    return render(request, 'wui/containers.html',{})

@login_required
def commitContainer(request):
    #container_backuped.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})

