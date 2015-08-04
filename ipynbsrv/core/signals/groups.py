from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_delete, post_save
from ipynbsrv.core.models import BackendGroup, CollaborationGroup
from ipynbsrv.core.signals.signals import *


@receiver(group_member_added)
def map_to_backend_group_member_added(sender, group, user, **kwargs):
    """
    Map the Django group signal to BackendGroup.
    """
    if group is not None and user is not None:
        if hasattr(group, 'backend_group') and hasattr(user, 'backend_user'):
            backend_group_member_added.send(
                sender=BackendGroup,
                group=group.backend_group,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(group_member_removed)
def map_to_backend_group_member_removed(sender, group, user, **kwargs):
    """
    Map the Django group signal to BackendGroup.
    """
    if group is not None and user is not None:
        if hasattr(group, 'backend_group') and hasattr(user, 'backend_user'):
            backend_group_member_removed.send(
                sender=BackendGroup,
                group=group.backend_group,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(group_member_added)
def map_to_collaboration_group_member_added(sender, group, user, **kwargs):
    """
    Map the Django group signal to BackendGroup.
    """
    if group is not None and user is not None:
        if hasattr(group, 'collaborationgroup') and hasattr(user, 'backend_user'):
            collaboration_group_member_added.send(
                sender=CollaborationGroup,
                group=group.collaborationgroup,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(group_member_removed)
def map_to_collaboration_group_member_removed(sender, group, user, **kwargs):
    """
    Map the Django group signal to BackendGroup.
    """
    if group is not None and user is not None:
        if hasattr(group, 'collaborationgroup') and hasattr(user, 'backend_user'):
            collaboration_group_member_removed.send(
                sender=CollaborationGroup,
                group=group.collaborationgroup,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(group_member_added)
def map_to_share_member_added(sender, group, user, **kwargs):
    """
    Map the Django group signal to share signals if needed.
    """
    if group is not None and user is not None:
        if hasattr(group, 'share') and hasattr(user, 'backend_user'):
            share_member_added.send(
                sender=BackendGroup,
                group=group.share,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(group_member_removed)
def map_to_share_member_removed(sender, group, user, **kwargs):
    """
    Map the Django group signal to share signals if needed.
    """
    if group is not None and user is not None:
        if hasattr(group, 'share') and hasattr(user, 'backend_user'):
            share_member_removed.send(
                sender=BackendGroup,
                group=group.share,
                user=user.backend_user,
                kwargs=kwargs
            )


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, Group):
        if 'pk_set' in kwargs:  # group members
            # get the user objects
            users = []
            if kwargs.get('pk_set') is not None:
                for user_pk in kwargs.get('pk_set'):
                    users.append(User.objects.get(pk=user_pk))
            # trigger the signals
            if action == 'post_add':
                for user in users:
                    group_member_added.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for user in instance.user_set.all():
                    group_member_removed.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for user in users:
                    group_member_removed.send(
                        sender=sender,
                        group=instance,
                        user=user,
                        kwargs=kwargs
                    )
    elif isinstance(instance, User):
        if 'pk_set' in kwargs:  # group memberships
            # get the group objects
            groups = []
            if kwargs.get('pk_set') is not None:
                for group_pk in kwargs.get('pk_set'):
                    groups.append(Group.objects.get(pk=group_pk))
            # trigger the signals
            if action == 'post_add':
                for group in groups:
                    group_member_added.send(
                        sender=sender,
                        group=group,
                        user=instance,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for group in instance.groups.all():
                    group_member_removed.send(
                        sender=sender,
                        group=group,
                        user=instance,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for group in groups:
                    group_member_removed.send(
                        sender=sender,
                        group=group,
                        user=instance,
                        kwargs=kwargs
                    )


@receiver(post_delete, sender=Group)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    group_deleted.send(sender=sender, group=instance, kwargs=kwargs)


@receiver(post_save, sender=Group)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(
            sender=sender,
            group=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
