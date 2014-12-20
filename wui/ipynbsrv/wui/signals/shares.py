import os.path
import shutil
import stat
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Group, LdapGroup, Share
from ipynbsrv.wui.signals.signals import share_created, share_deleted
from ipynbsrv.wui.tools import Filesystem


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
    ldap_group = LdapGroup.objects.filter(name='share_' + share.name).first()
    if ldap_group:
        os.chown(path, -1, ldap_group.gid)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_ISGID)
    else:
        raise "required LDAP group '{0}' does not exist.".format(share.name)


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
    shutil.rmtree(path = os.path.join(settings.SHARE_ROOT, share.name), ignore_errors=not settings.DEBUG)


"""
Internal receivers to map the Django built-in signals into custom ones.
"""
@receiver(post_delete, sender=Share, dispatch_uid='ipynbsrv.wui.signals.shares.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    share_deleted.send(sender, share=instance)

@receiver(post_save, sender=Share, dispatch_uid='ipynbsrv.wui.signals.shares.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        share_created.send(sender, share=instance)
    # else:
    #     share_modified.send(sender, share=instance, fields=kwargs['update_fields'])
