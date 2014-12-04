import os.path
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Share
from ipynbsrv.wui.signals.signals import share_created, share_deleted, share_modified, share_user_added, share_user_leaved, share_user_removed
from ipynbsrv.wui.tools import Filesystem


"""
"""
@receiver(share_created)
def created_handler(sender, share, **kwargs):
    print "created share via signal"

    path = os.path.join(settings.DATA_ROOT, share.name)
    #Filesystem.ensure_directory(path)


"""
"""
@receiver(share_deleted)
def deleted_handler(sender, share, **kwargs):
    print "deleted share via signal"


"""
"""
@receiver(share_modified)
def modified_handler(sender, share, fields, **kwargs):
    print "modified share via signal"


"""
"""
@receiver(share_user_added)
def user_added_handler(sender, share, user, **kwargs):
    print "user added share via signal"


"""
"""
@receiver(share_user_leaved)
def user_leaved_handler(sender, share, user, **kwargs):
    print "user leaved share via signal"


"""
"""
@receiver(share_user_removed)
def user_removed_handler(sender, share, user, **kwargs):
    print "user removed from share via signal"


#
# Bridges
#
"""
"""
@receiver(post_delete, sender=Share, dispatch_uid='ipynbsrv.wui.signals.shares.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    share_deleted.send(sender, share=instance)


"""
"""
@receiver(post_save, sender=Share, dispatch_uid='ipynbsrv.wui.signals.shares.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        share_created.send(sender, share=instance)
    else:
        share_modified.send(sender, share=instance, fields=kwargs['update_fields'])
