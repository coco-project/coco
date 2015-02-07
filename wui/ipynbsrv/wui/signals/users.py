import os.path
import shutil
import stat
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapUser
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Filesystem


@receiver(post_user_created)
def create_user_directories(sender, user, **kwargs):
    """
    Every LDAP user needs his home and public directory, so we create them here.
    """
    if settings.DEBUG:
        print "create_user_directories receiver fired"
    username = user.get_username()
    ldap_user = LdapUser.objects.filter(pk=username)
    if ldap_user.exists():
        ldap_user = ldap_user.first()
        # create the user's home directory
        path = os.path.join(settings.HOME_ROOT, username)
        Filesystem.ensure_directory(path)
        # set owner and permissions
        os.chown(path, ldap_user.id, ldap_user.group_id)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        # create the user's public directory
        path = os.path.join(settings.PUBLIC_ROOT, username)
        Filesystem.ensure_directory(path)
        # set owner and permissions
        os.chown(path, ldap_user.id, ldap_user.group_id)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


@receiver(post_user_deleted)
def remove_user_directories(sender, user, **kwargs):
    """
    As soon as a user is deleted we can safely remove his home and public directory.
    """
    if settings.DEBUG:
        print "remove_user_directories receiver fired"
    username = user.get_username()
    ldap_user = LdapUser.objects.filter(pk=username)
    if ldap_user.exists():
        ldap_user = ldap_user.first()
        # delete the user's home directory
        path = os.path.join(settings.HOME_ROOT, username)
        shutil.rmtree(path)
        # delete the user's public directory
        path = os.path.join(settings.PUBLIC_ROOT, username)
        shutil.rmtree(path)


@receiver(post_user_modified)
def user_modified_handler(sender, user, fields, **kwargs):
    if settings.DEBUG:
        print "user_modified_handler receiver fired"
    # TODO: update LDAP user + group memberships


# ###############################################


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    if isinstance(instance, User):
        action = kwargs['action']
        if action == 'post_add' or action == 'post_remove' or action == 'pre_add' or action == 'pre_remove':
            if action == 'post_add' or action == 'post_remove':
                post_user_modified.send(sender=sender, user=instance, fields=['groups'], kwargs=kwargs)
            elif action == 'pre_add' or action == 'pre_remove':
                pre_user_modified.send(sender=sender, user=instance, fields=['groups'], kwargs=kwargs)
            user_modified.send(sender=sender, user=instance, fields=['groups'], action=action kwargs=kwargs)


@receiver(post_delete, sender=User)
def post_delete_handler(sender, instance, **kwargs):
    post_user_deleted.send(sender=sender, user=instance, kwargs=kwargs)
    user_deleted.send(sender=sender, user=instance, action='post_delete' kwargs=kwargs)


@receiver(pre_delete, sender=User)
def pre_delete_handler(sender, instance, **kwargs):
    pre_user_deleted.send(sender=sender, user=instance, kwargs=kwargs)
    user_deleted.send(sender=sender, user=instance, action='pre_delete' kwargs=kwargs)


@receiver(post_save, sender=User)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        post_user_created.send(sender=sender, user=instance, kwargs=kwargs)
        user_created.send(sender=sender, user=instance, action='post_save' kwargs=kwargs)
    else:
        post_user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], action='post_save' kwargs=kwargs)


@receiver(pre_save, sender=User)
def pre_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        pre_user_created.send(sender=sender, user=instance, kwargs=kwargs)
        user_created.send(sender=sender, user=instance, action='pre_save' kwargs=kwargs)
    else:
        pre_user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], action='pre_save' kwargs=kwargs)
