import os.path
import shutil
import stat
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapUser
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Filesystem


@receiver(user_created)
def create_user_directories(sender, user, **kwargs):
    """
    Every LDAP user needs his home and public directory, so we create them here.
    """
    if settings.DEBUG:
        print "create_user_directories receiver fired"
    if user is not None:
        username = user.get_username()
        # TODO


@receiver(user_deleted)
def remove_user_directories(sender, user, **kwargs):
    """
    As soon as a user is deleted we can safely remove his home and public directory.
    """
    if settings.DEBUG:
        print "remove_user_directories receiver fired"
    if user is not None:
        username = user.get_username()
        # TODO


@receiver(user_modified)
def user_modified_handler(sender, user, fields, **kwargs):
    if settings.DEBUG:
        print "user_modified_handler receiver fired"
    kwargs = kwargs['kwargs']
    if fields is not None and 'groups' in fields:
        # get the group objects
        groups = []
        if kwargs['pk_set'] is not None:
            for group_pk in kwargs['pk_set']:
                groups.append(Group.objects.get(pk=group_pk))
        # trigger the signals
        action = kwargs['action']
        if action == 'post_add':
            for group in groups:
                group_member_added.send(sender=sender, group=group, users=[user], kwargs=kwargs)
        elif action == 'pre_clear':
            for group in user.groups.all():
                group_member_removed.send(sender=sender, group=group, users=[user], kwargs=kwargs)
        elif action == 'post_remove':
            for group in groups:
                group_member_removed.send(sender=sender, group=group, users=[user], kwargs=kwargs)


'''

    Calling custom signals

'''


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    if isinstance(instance, User):
        action = kwargs['action']
        if action == 'post_add' or action == 'pre_clear' or action == 'post_remove':
            user_modified.send(sender=sender, user=instance, fields=['groups'], kwargs=kwargs)


@receiver(post_delete, sender=User)
def post_delete_handler(sender, instance, **kwargs):
    user_deleted.send(sender=sender, user=instance, kwargs=kwargs)


@receiver(post_save, sender=User)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], kwargs=kwargs)
