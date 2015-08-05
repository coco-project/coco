from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from ipynbsrv.core.models import BackendUser, CollaborationGroup
from ipynbsrv.core.signals.signals import *


@receiver(collaboration_group_created)
def add_creator_to_collaboration_group(sender, group, **kwargs):
    """
    Add the group creator to the group's user set.
    """
    if group is not None and group.creator is not None:
        group.add_member(group.creator)


@receiver(collaboration_group_admin_added)
def add_admin_to_collaboration_group(sender, group, user, **kwargs):
    """
    Add the admin to the collaboration groups's internal backend group.
    """
    if group is not None and user is not None:
        # TODO: doesn't trigger signal because we're within a group signal already
        group.add_member(user)


@receiver(collaboration_group_admin_removed)
def remove_admin_from_collaboration_group(sender, group, user, **kwargs):
    """
    Remove the admin to the collaboration groups's internal backend group.
    """
    if group is not None and user is not None:
        if not user == group.creator:
            # TODO: doesn't trigger signal because we're within a group signal already
            group.remove_member(user)


@receiver(m2m_changed, sender=CollaborationGroup.admins.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, CollaborationGroup):
        if 'pk_set' in kwargs:  # admins
            # get the user objects
            users = []
            if kwargs.get('pk_set') is not None:
                for user_pk in kwargs.get('pk_set'):
                    users.append(BackendUser.objects.get(pk=user_pk))
            # trigger the signals
            if action == 'post_add':
                for user in users:
                    collaboration_group_admin_added.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for user in instance.admins.all():
                    collaboration_group_admin_removed.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for user in users:
                    collaboration_group_admin_removed.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )


@receiver(post_delete, sender=CollaborationGroup)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    collaboration_group_deleted.send(sender=sender, group=instance, kwargs=kwargs)


@receiver(pre_delete, sender=CollaborationGroup)
def pre_delete_handler(sender, instance, **kwargs):
    """
    Receiver fired before a CollaborationGroup is actually deleted.
    """
    for notification in instance.notifications.all():
        notification.receiver_groups.remove(instance)
    for share in instance.shares.all():
        share.remove_access_group(instance)


@receiver(post_save, sender=CollaborationGroup)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        collaboration_group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        collaboration_group_modified.send(
            sender=sender,
            group=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
