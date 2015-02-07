import os.path
import shutil
import stat
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, Share
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Filesystem


@receiver(share_created)
def create_share_directory(sender, share, **kwargs):
    """
    Signal receiver that creates the filesystem directory for a created share.
    """
    if settings.DEBUG:
        print "create_share_directory receiver fired"
    if share is not None:
        # create the directory
        path = os.path.join(settings.SHARE_ROOT, share.name)
        Filesystem.ensure_directory(path)
        # set owner and permissions
        ldap_group = LdapGroup.objects.get(name=settings.SHARE_GROUP_PREFIX + share.name)
        os.chown(path, -1, ldap_group.id)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_ISGID)


@receiver(share_deleted)
def delete_share_directory(sender, share, **kwargs):
    """
    Signal receiver that deletes the filesystem directory for a removed share.
    """
    if settings.DEBUG:
        print "delete_share_directory receiver fired"
    if share is not None:
        # remove the directory
        shutil.rmtree(path=os.path.join(settings.SHARE_ROOT, share.name), ignore_errors=not settings.DEBUG)
        # make sure the group is removed too
        share.group.delete()


@receiver(share_modified)
def share_modified_handler(sender, share, fields, **kwargs):
    if settings.DEBUG:
        print "share_modified_handler receiver fired"
    # TODO: update share (name, owner etc)


# ###############################################


@receiver(post_delete, sender=Share)
def post_delete_handler(sender, instance, **kwargs):
    share_deleted.send(sender=sender, share=instance, kwargs=kwargs)


@receiver(post_save, sender=Share)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs:
        share_created.send(sender, share=instance, kwargs=kwargs)
    else:
        share_modified.send(sender, share=instance, fields=kwargs['update_fields'], kwargs=kwargs)
