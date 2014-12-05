import os.path
import shutil
import stat
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Group, LdapGroup, Share
from ipynbsrv.wui.signals.signals import share_created, share_deleted, share_modified, share_user_added, share_user_leaved, share_user_removed
from ipynbsrv.wui.tools import Filesystem


"""
"""
@receiver(share_created)
def created_handler(sender, share, **kwargs):
    print "created share via signal"
    # create the directory
    path = os.path.join(settings.SHARE_ROOT, share.name)
    Filesystem.ensure_directory(path)
    # set owner and permissions
    ldap_group = LdapGroup.objects.filter(name="share_" + share.name).first()
    if ldap_group:
        os.chown(path, -1, ldap_group.gid)
        os.chmod(path, stat.S_IRWXO | stat.S_IRWXG | stat.S_ISGID)
    else:
        raise "required LDAP group '{0}' does not exist.".format(share.name)


"""
"""
@receiver(share_deleted)
def deleted_handler(sender, share, **kwargs):
    print "deleted share via signal"
    # make sure the group is removed too
    group = Group.objects.filter(name=share.name).first()
    if group:
        group.delete()
    # remove the directory
    shutil.rmtree(path = os.path.join(settings.SHARE_ROOT, share.name), ignore_errors=not settings.DEBUG)


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
