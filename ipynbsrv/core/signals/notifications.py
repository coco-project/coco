from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.core.models import CollaborationGroup, Notification, \
    NotificationLog
from ipynbsrv.core.signals.signals import *


@receiver(notification_receiver_group_added)
def create_notificationlogs_for_receivers(sender, notification, group, **kwargs):
    """
    Create NotificationLog records for every user in the receiving group.
    """
    if notification:
        for user in group.get_members():
            log = NotificationLog(notification=notification, user=user)
            log.save()


@receiver(collaboration_group_member_removed)
def deactivate_group_notifications_for_user(sender, group, user, **kwargs):
    """
    Deactivate all log records for group notification for this user.
    """
    if group is not None and user is not None:
        for notification in group.notifications.all():
            leave = False
            for receiver_group in notification.receiver_groups.all():
                if receiver_group != group:
                    if receiver_group.user_is_member(user):
                        leave = True
                        break
            if not leave:
                logs = NotificationLog.objects.filter(notification=notification).filter(user=user)
                if logs.exists():
                    logs.update(in_use=False)


@receiver(collaboration_group_member_added)
def reactivate_group_notifications_for_user(sender, group, user, **kwargs):
    """
    Reactivate all log records for group notification for this user.
    """
    if group is not None and user is not None:
        for notification in group.notifications.all():
            logs = NotificationLog.objects.filter(notification=notification).filter(user=user)
            if logs.exists():
                logs.update(in_use=True)


@receiver(m2m_changed, sender=Notification.receiver_groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, Notification):
        if 'pk_set' in kwargs:  # receiver groups
            # get the group objects
            groups = []
            if kwargs.get('pk_set') is not None:
                for group_pk in kwargs.get('pk_set'):
                    groups.append(CollaborationGroup.objects.get(pk=group_pk))
            # trigger the signals
            if action == 'post_add':
                for group in groups:
                    notification_receiver_group_added.send(
                        sender=sender,
                        notification=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for group in instance.receiver_groups.all():
                    notification_receiver_group_removed.send(
                        sender=sender,
                        notification=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for group in groups:
                    notification_receiver_group_removed.send(
                        sender=sender,
                        notification=instance,
                        group=group,
                        kwargs=kwargs
                    )


@receiver(post_delete, sender=Notification)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    notification_deleted.send(sender=sender, notification=instance, kwargs=kwargs)


@receiver(post_save, sender=Notification)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        notification_created.send(sender=sender, notification=instance, kwargs=kwargs)
