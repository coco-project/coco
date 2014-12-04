from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Image
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools.dock import Docker

d = Docker()
""
@receiver(image_created)
def created(sender, **kwargs):
    print("Received image_created signal.")


""
@receiver(image_deleted)
def deleted(sender, id, **kwargs):
    d.delImage(id)
    print("Received image_deleted signal.")


""
@receiver(image_edited)
def edited(sender, **kwargs):
    print("Received image_edited signal.")


""
@receiver(image_shared)
def shared(sender, **kwargs):
    print("Received image_shared signal.")


#
# Bridges
#
""
@receiver(pre_delete, sender=Image)
def pre_delete(sender, **kwargs):
    print("Received pre_delete signal from image.")
    # TODO: raise signals


""
@receiver(pre_save, sender=Image)
def pre_save(sender, **kwargs):
    print("Received pre_save signal from image.")
    # TODO: raise signals

