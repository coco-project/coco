from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Share
from ipynbsrv.wui.signals.signals import share_accepted, share_created, share_declined, share_deleted, share_invited, share_leaved, share_user_added


""
@receiver(share_accepted)
def accepted(sender, share, user, **kwargs):
    print("Received share_accepted signal.")


""
@receiver(share_created)
def created(sender, share, **kwargs):
    print "created share"


""
@receiver(share_declined)
def declined(sender, share, user, **kwargs):
    print("Received share_declined signal.")


""
@receiver(share_deleted)
def deleted(sender, share, **kwargs):
    print "deleted share"


""
@receiver(share_invited)
def invited(sender, share, user, **kwargs):
    print("Received share_invited signal.")


""
@receiver(share_leaved)
def leaved(sender, share, user, **kwargs):
    print("Received share_leaved signal.")


""
@receiver(share_user_added)
def user_added(sender, share, user, **kwargs):
    print("Received share_user_added signal.")

#
# Bridges
#
""
@receiver(pre_delete, sender=Share)
def pre_delete(sender, instance, using, **kwargs):
    share_deleted.send(sender, share=instance)


""
@receiver(pre_save, sender=Share)
def pre_save(sender, instance, using, **kwargs):
    share_created.send(sender, share=instance)
