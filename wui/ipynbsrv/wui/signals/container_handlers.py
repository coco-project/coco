from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container
from ipynbsrv.wui.signals.signals import *


""
@receiver(container_backuped)
def backuped(sender, **kwargs):
    print("Received container_backuped signal.")


""
@receiver(container_cloned)
def cloned(sender, **kwargs):
    print("Received container_cloned signal.")


""
@receiver(container_created)
def created(sender, **kwargs):
    print("Received container_created signal.")


""
@receiver(container_deleted)
def deleted(sender, **kwargs):
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
    print("Received container_started signal.")


""
@receiver(container_stopped)
def stopped(sender, **kwargs):
    print("Received container_stopped signal.")


#
# Bridges
#
""
@receiver(pre_delete, sender=Container)
def pre_delete(sender, **kwargs):
    print("Received container_pre_delete signal from container.")
    # TODO: raise signals


""
@receiver(pre_save, sender=Container)
def pre_save(sender, **kwargs):
    print("Received pre_save signal from container.")
    # TODO: raise signals
