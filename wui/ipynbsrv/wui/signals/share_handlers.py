from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Share
from ipynbsrv.wui.signals.signals import *


""
@receiver(share_accepted)
def accepted(sender, **kwargs):
    print("Received share_accepted signal.")


""
@receiver(share_created)
def created(sender, **kwargs):
    print("Received share_created signal.")


""
@receiver(share_declined)
def declined(sender, **kwargs):
    print("Received share_declined signal.")


""
@receiver(share_deleted)
def deleted(sender, **kwargs):
    print("Received share_deleted signal.")


""
@receiver(share_edited)
def edited(sender, **kwargs):
    print("Received share_edited signal.")


""
@receiver(share_invited)
def invited(sender, **kwargs):
    print("Received share_invited signal.")


""
@receiver(share_leaved)
def leaved(sender, **kwargs):
    print("Received share_leaved signal.")


#
# Bridges
#
""
@receiver(pre_delete, sender=Share)
def pre_delete(sender, **kwargs):
    print("Received pre_delete signal from share.")
    # TODO: raise signals


""
@receiver(pre_save, sender=Share)
def pre_save(sender, **kwargs):
    print("Received pre_save signal from share.")
    # TODO: raise signals
