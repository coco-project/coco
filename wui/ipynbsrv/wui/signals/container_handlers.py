from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools.docker import Docker

d = Docker()
""
@receiver(container_backuped)
def backuped(sender, **kwargs):
    d.commitContainer(id, repo, tag)
    print("Received container_backuped signal.")


""
@receiver(container_cloned)
def cloned(sender, **kwargs):
    print("Received container_cloned signal.")


""
@receiver(container_created)
def created(sender, **kwargs):
    d.createContainer(img, cmd, name, tty)
    print("Received container_created signal.")


""
@receiver(container_deleted)
def deleted(sender, **kwargs):
    c = kwargs.pop()
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
def started(sender, **kwargs):
    c = kwargs.pop()
    d.startContainer(c.ct_id)
    print("Received container_started signal.")


""
@receiver(container_stopped)
def stopped(sender, **kwargs):
    c = kwargs.pop()
    d.stopContainer(c.ct_id)
    print("Received container_stopped signal.")


#
# Bridges
#
""
@receiver(pre_delete, sender=Container)
def pre_delete(sender, **kwargs):
    print("Received container_pre_delete signal from container.")
    container_deleted.send(sender=self.__class, **kwargs)


""
@receiver(pre_save, sender=Container)
def pre_save(sender, **kwargs):
    print("Received pre_save signal from container.")
    # TODO: raise signals
