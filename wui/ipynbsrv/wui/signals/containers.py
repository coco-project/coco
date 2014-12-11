from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker

d = Docker()

""
@receiver(container_commited)
def commited(sender, image, ct_id, name, **kwargs):
    d.commitContainer(ct_id, name, 'latest')
    c_name = name + ":latest"
    cont = d.images_name(name)
    image.img_id = cont[0]['Id']

""
@receiver(container_created)
def created(sender, container, image, **kwargs):
    cont = d.createContainer(image, '/bin/bash', container.name, 'True')
    id = cont['Id']
    id = str(id)
    container.ct_id = id
    print("Received container_created signal.")


""
@receiver(container_deleted)
def delete(sender, container, **kwargs):
    containers = d.containersall()
    tmp = False
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    tmp=True
    if tmp:
	d.delContainer(container.ct_id)
    else:
	print("Container allready deleted")	
    print("Received container_deleted signal.")


""
@receiver(container_started)
def started(sender, container, **kwargs):
    print("Received container_started signal.")
    containers = d.containersall()
    tmp = False
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    tmp=True
    if tmp:
    	d.startContainer(container.ct_id)
    else:
	raise Exception("Container doesnt exist")


""
@receiver(container_stopped)
def stopped(sender, container, **kwargs):
    print("Received container_stopped signal.")
    containers = d.containersall()
    tmp = False
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    tmp=True
    if tmp:
    	d.stopContainer(container.ct_id)
    else:
	raise Exception("Container doesnt exist")

""
@receiver(container_restarted)
def restarted(sender, container, **kwargs):
    print("Received container_stopped signal.")
    containers = d.containersall()
    tmp = False
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    tmp=True
    if tmp:
    	d.restartContainer(container.ct_id)
    else:
	raise Exception("Container doesnt exist")


#
# Bridges
#
""
@receiver(pre_delete, sender=Container)
def pre_delete(sender, instance, **kwargs):
    print("Received container_pre_delete signal from container.")
    containers = d.containers()
    tmp = False
    for cont in containers:
	if cont['Id'] == instance.ct_id:
	    tmp=True
    if tmp:
	container_stopped.send(sender='', container=instance)
    container_deleted.send(sender='', container=instance)
    if instance.is_clone:
	image_deleted.send(sender='', id=instance.image.img_id)

""
@receiver(pre_save, sender=Container)
def pre_save(sender, instance, **kwargs):
    print("Received pre_save signal from container.")
    if instance.status == True:
	container_started.send(sender='',container=instance)
    else:
	container_stopped.send(sender='',container=instance)
    # TODO: raise signals

