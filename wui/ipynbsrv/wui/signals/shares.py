import os.path
import shutil
import stat
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, Share
from ipynbsrv.wui.signals.signals import share_created, share_deleted, share_modified
from ipynbsrv.wui.tools import Filesystem


GROUP_PREFIX = 'share_'


"""
Signal receiver that creates the filesystem directory for a created share.
"""
@receiver(share_created)
def created_handler(sender, share, **kwargs):
    if settings.DEBUG:
        print "Creating share via signal..."
    # create the directory
    path = os.path.join(settings.SHARE_ROOT, share.name)
    Filesystem.ensure_directory(path)
    # set owner and permissions
    ldap_group = LdapGroup.objects.get(name=GROUP_PREFIX + share.name)
    os.chown(path, -1, ldap_group.id)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_ISGID)


"""
Signal receiver that deletes the filesystem directory for a removed share.
"""
@receiver(share_deleted)
def deleted_handler(sender, share, **kwargs):
    if settings.DEBUG:
        print "Deleting share via signal..."
    # make sure the group is removed too
    share.group.delete()
    # remove the directory
    shutil.rmtree(path=os.path.join(settings.SHARE_ROOT, share.name), ignore_errors=not settings.DEBUG)


"""
Method triggered by group_modified signals.
"""
@receiver(share_modified)
def modified_handler(sender, share, fields, **kwargs):
    if settings.DEBUG:
        print "share_modified handler fired"

"""
Internal receivers to map the Django built-in signals to custom ones.
"""
@receiver(post_delete, sender=Share)
def post_delete_handler(sender, instance, **kwargs):
    share_deleted.send(sender=sender, share=instance, kwargs=kwargs)

@receiver(post_save, sender=Share)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        share_created.send(sender, share=instance, kwargs=kwargs)
    else:
        share_modified.send(sender, share=instance, fields=kwargs['update_fields'], kwargs=kwargs)
