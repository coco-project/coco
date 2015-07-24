from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_delete, post_save
from ipynbsrv.core.signals.signals import *


@receiver(user_modified)
def modified_handler(sender, user, fields, **kwargs):
    """
    Helper method to break modifications into smaller pieces.
    """
    kwargs = kwargs.get('kwargs')
    if fields is not None and 'groups' in fields:
        # get the group objects
        groups = []
        if kwargs.get('pk_set') is not None:
            for group_pk in kwargs.get('pk_set'):
                groups.append(Group.objects.get(pk=group_pk))
        # trigger the signals
        action = kwargs.get('action')
        if action == 'post_add':
            for group in groups:
                group_member_added.send(
                    sender=sender,
                    group=group,
                    user=user,
                    kwargs=kwargs
                )
        elif action == 'pre_clear':
            for group in user.groups.all():
                group_member_removed.send(
                    sender=sender,
                    group=group,
                    user=user,
                    kwargs=kwargs
                )
        elif action == 'post_remove':
            for group in groups:
                group_member_removed.send(
                    sender=sender,
                    group=group,
                    user=user,
                    kwargs=kwargs
                )


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    if isinstance(instance, User):
        action = kwargs.get('action')
        if action == 'post_add' or action == 'pre_clear' or action == 'post_remove':
            user_modified.send(
                sender=sender,
                user=instance,
                fields=['groups'],
                kwargs=kwargs
            )


@receiver(post_delete, sender=User)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    user_deleted.send(sender=sender, user=instance, kwargs=kwargs)


@receiver(post_save, sender=User)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        user_modified.send(
            sender=sender,
            user=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
