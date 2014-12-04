from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker

d = Docker()
""
@receiver(container_backuped)
def backuped(sender, **kwargs):
    print("Received container_backuped signal.")


""
@receiver(container_cloned)
def cloned(sender, **kwargs):
    print("Received container_cloned signal.")

""
@receiver(container_commited)
def commited(sender, image, ct_id, name, **kwargs):
    d.commitContainer(ct_id, name, 'latest')
    c_name = name + ":latest"
    cont = d.images(name)
    print(cont[0])
    image.img_id = cont[0]['Id']

""
@receiver(container_created)
def created(sender, container, image, **kwargs):
    cont = d.createContainer(image, '/bin/bash', container.name, 'True')
    id = cont['Id']
    print(id)
    id = str(id)
    print(id)
    container.ct_id = id
    print(container.id)
    print("Received container_created signal.")


""
@receiver(container_deleted)
def delete(sender, container, **kwargs):
    c = container
    d.delContainer(c.ct_id)
    print("Received container_deleted signal.")


""
@receiver(container_edited)
def edited(sender, **kwargs):
    print("Received container_edited signal.")


""
@receiver(container_restored)
def restored(sender, **kwargs):
    print("Received container_restored signal.")


""
@receiver(container_shared)
def shared(sender, **kwargs):
    print("Received container_shared signal.")

""
@receiver(container_started)
def started(sender, container, **kwargs):
    c = container
    d.startContainer(c.ct_id)
    print("Received container_started signal.")


""
@receiver(container_stopped)
def stopped(sender, container, **kwargs):
    c = container
    d.stopContainer(c.ct_id)
    print("Received container_stopped signal.")


#
# Bridges
#
""
@receiver(pre_delete, sender=Container)
def pre_delete(sender, **kwargs):
    print("Received container_pre_delete signal from container.")
    #container_deleted.send(sender='', **kwargs)


""
@receiver(pre_save, sender=Container)
def pre_save(sender, **kwargs):
    print("Received pre_save signal from container.")
    # TODO: raise signals

