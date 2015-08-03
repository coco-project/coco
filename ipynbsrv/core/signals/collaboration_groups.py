from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_delete, post_save
from ipynbsrv.core.models import BackendUser, CollaborationGroup
from ipynbsrv.core.signals.signals import *


# @receiver(collaboration_group_admin_added)
# def add_admin_to_collaboration_group(sender, group, user, **kwargs):
#     """
#     Add the admin to the collaboration groups's internal backend group.
#     """
#     if group is not None and user is not None:
#         group.add_member(user)


@receiver(collaboration_group_deleted)
def delete_django_group(sender, group, **kwargs):
    """
    Delete the internal Django group on delete.
    """
    if group is not None:
        group.django_group.delete()


# @receiver(collaboration_group_admin_removed)
# def remove_admin_from_collaboration_group(sender, group, user, **kwargs):
#     """
#     Remove the admin to the collaboration groups's internal backend group.
#     """
#     if group is not None and user is not None:
#         group.remove_member(user)


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
                for user in instance.django_group.user_set.all():
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
