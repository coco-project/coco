from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Share
from ipynbsrv.wui.signals.signals import *


# ""
# @receiver(share_accepted)
# def accepted(sender, share, user, **kwargs):
#     print("Received share_accepted signal.")


""
@receiver(share_created)
def created_share(sender, share, **kwargs):
    print "created share"


# ""
# @receiver(share_declined)
# def declined(sender, share, user, **kwargs):
#     print("Received share_declined signal.")


""
@receiver(share_deleted)
def deleted_handler(sender, share, **kwargs):
    print "deleted share"


# ""
# @receiver(share_invited)
# def invited(sender, share, user, **kwargs):
#     print("Received share_invited signal.")


# ""
# @receiver(share_leaved)
# def leaved(sender, share, user, **kwargs):
#     print("Received share_leaved signal.")


""
@receiver(share_user_added)
def user_added_handler(sender, share, user, **kwargs):
    print("Received share_user_added signal.")


""
@receiver(share_user_removed)
def user_removed_handler(sender, share, user, **kwargs):
    print("Received share_user_removed signal.")


#
# Bridges
#
@receiver(post_delete, sender=Share)
def post_delete(sender, instance, using, **kwargs):
    share_deleted.send(sender, share=instance)


@receiver(post_save, sender=Share)
def post_save(sender, instance, using, **kwargs):
    share_created.send(sender, share=instance)
