from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker
import re

d = Docker()

""
@receiver(container_commited)
def commited(sender, image, ct_id, name, **kwargs):
    print("Received container_commited signal.")
    d.commitContainer(ct_id, name, 'latest')
    c_name = name + ":latest"
    cont = d.images_name(name)
    image.img_id = cont[0]['Id']

""
@receiver(container_created)
def created(sender, container, image, **kwargs):
    print("Received container_created signal.")
    check = False
    containers = d.containers()
    while (not check):
	for c in containers:
	    check = True
	    for port in c['Ports']:
		if 'PublicPort' in port:
		    if port['PublicPort'] == container.exposeport:
			container.exposeport = container.exposeport + 1
			check = False
    cont = d.createContainer(image, container.name, 'True', container.image.ports, container.exposeport)
    id = cont['Id']
    id = str(id)
    container.ct_id = id


""
@receiver(container_deleted)
def delete(sender, container, **kwargs):
    print("Received container_deleted signal.")
    containers = d.containersall()
    tmp = False
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    tmp=True
    if tmp:
	d.delContainer(container.ct_id)
    else:
	print("Container allready deleted")	


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
    	d.startContainer(container.ct_id, container.image.ports, container.exposeport)
    else:
	raise Exception("Container doesnt exist")

    tmp = False
    container.ports = ""
    containers = d.containers()
    for cont in containers:
	if cont['Id'] == container.ct_id:
	    for port in cont['Ports']:
		if 'PublicPort' in port:
			if port['PrivatePort'] == 22:
				container.description += "\n SSH-Port = " + str(port['PublicPort'])


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
	container.description = re.sub(r'SSH-Port = [0-9]*',"",container.description)
    else:
	raise Exception("Container doesnt exist")

""
@receiver(container_restarted)
def restarted(sender, container, **kwargs):
    print("Received container_restarted signal.")
#    containers = d.containersall()
#    tmp = False
#    for cont in containers:
#	if cont['Id'] == container.ct_id:
#	    tmp=True
#    if tmp:
#    	d.restartContainer(container.ct_id)
#    else:
#	raise Exception("Container doesnt exist")
    container_stopped.send(sender=sender, container=container)
    container_started.send(sender=sender, container=container)


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

