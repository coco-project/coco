import os.path
import shutil
import stat
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapUser
from ipynbsrv.wui.signals.signals import user_created, user_deleted, user_modified
from ipynbsrv.wui.tools import Filesystem


"""
Receiver that is called when ever a user gets created.

Every user needs his home and publication directory, so we create them here.
"""
@receiver(user_created)
def created_handler(sender, user, **kwargs):
    if settings.DEBUG:
        print "user_created handler fired"
    ldap_user = LdapUser.objects.filter(pk=user.username).first()
    if ldap_user:
        # create the user's home directory
        path = os.path.join(settings.HOME_ROOT, user.username)
        Filesystem.ensure_directory(path)
        # set owner and permissions
        os.chown(path, user.uid, user.group)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        # create the user's public directory
        path = os.path.join(settings.PUBLIC_ROOT, user.username)
        Filesystem.ensure_directory(path)
        # set owner and permissions
        os.chown(path, user.uid, user.group)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


"""
Handler triggered by user_deleted signals.

As soon as a user is deleted we can safely remove his home and publication directory.
"""
@receiver(user_deleted)
def deleted_handler(sender, user, **kwargs):
    if settings.DEBUG:
        print "user_deleted handler fired"
    ldap_user = LdapUser.objects.filter(pk=user.username).first()
    if ldap_user:
        # delete the user's home directory
        path = os.path.join(settings.HOME_ROOT, user.username)
        shutil.rmtree(path)
        # delete the user's publication directory
        path = os.path.join(settings.PUBLIC_ROOT, user.username)
        shutil.rmtree(path)


"""
Handler triggered by user_modified signals.
"""
@receiver(user_modified)
def modified_handler(sender, user, fields, kwargs):
    if settings.DEBUG:
        print "user_modified handler fired"


"""
Internal receivers to map the Django built-in signals to custom ones.
"""
@receiver(post_delete, sender=User)
def post_delete_handler(sender, instance, **kwargs):
    user_deleted.send(sender=sender, user=instance, kwargs=kwargs)

@receiver(post_save, sender=User)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], kwargs=kwargs)
