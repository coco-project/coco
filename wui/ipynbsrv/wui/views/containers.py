from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ipynbsrv.wui.models import Container


""
@login_required
def index(request):
    context = {
        'title': 'Containers'
    }

    return render(request, 'wui/containers.html', context)

@login_required
def stopContainer(request):
    container_stopped.send(sender=self.__class__,)
    c = Container.objects.all.filter(ct_id=id).get(pk=1)
    c.status = False
    c.save()
    return render(request, 'wui/containers.html',{})
    

@login_required
def startContainer(request):
    container_started.send(sender=self.__class__,)
    c = Container.objects.all.filter(ct_id=id).get(pk=1)
    c.status = True
    c.save()
    return render(request, 'wui/containers.html',{})

@login_required
def restartContainer(request):
    container_stopped.send(sender=self.__class__,)
    container_started.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})

@login_required
def getContainer(request):
    return render(request, 'wui/containers.html',{})

@login_required
def delContainer(request):
    container_deleted.send(sender=self.__class__,)
    c = Container.objects.all.filter(ct_id=id).get(pk=1)
    c.delete()
    return render(request, 'wui/containers.html',{})

@login_required
def createContainer(request):
    container_created.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})

@login_required
def commitContainer(request):
    container_backuped.send(sender=self.__class__,)
    return render(request, 'wui/containers.html',{})
