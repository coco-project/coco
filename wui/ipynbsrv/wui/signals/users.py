import os.path
import shutil
import stat
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import django_auth_ldap.backend
from ipynbsrv.wui.models import LdapUser
from ipynbsrv.wui.signals.signals import user_created, user_deleted
from ipynbsrv.wui.tools import Filesystem


"""
Receiver that is called when ever a user gets created.

Every user needs his home and publication directory, so we create them here.
"""
@receiver(user_created)
def created_handler(sender, user, **kwargs):
    if settings.DEBUG:
        print "Creating user via signal..."
    user = LdapUser.objects.filter(pk=user.username).first()
    if user:
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
        print "Deleting user via signal..."
    user = LdapUser.objects.filter(pk=user.username).first()
    if user:
        # delete the user's home directory
        path = os.path.join(settings.HOME_ROOT, user.username)
        shutil.rmtree(path)
        # delete the user's publication directory
        path = os.path.join(settings.PUBLIC_ROOT, user.username)
        shutil.rmtree(path)


"""
"""
@receiver(django_auth_ldap.backend.populate_user)
def populate_user_handler(sender, user, ldap_user, **kwargs):
    if settings.DEBUG:
        print "Populating user from LDAP user..."
    user.ldap = {
        'id': ldap_user.attrs['uidnumber'],
        'group_id': ldap_user.attrs['gidnumber']
    }


"""
Internal receivers to map the Django built-in signals into custom ones.
"""
@receiver(post_delete, sender=User, dispatch_uid='ipynbsrv.wui.signals.users.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    user_deleted.send(sender, user=instance)

@receiver(post_save, sender=User, dispatch_uid='ipynbsrv.wui.signals.users.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        user_created.send(sender, user=instance)
    # else:
    #     user_modified.send(sender, user=instance, fields=kwargs['update_fields'])
