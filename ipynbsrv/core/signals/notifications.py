from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from ipynbsrv.core.models import Notification, NotificationLog, CollaborationGroup
from ipynbsrv.core.signals.signals import notification_created


@receiver(notification_created)
def create_notificationlogs(sender, notification, **kwargs):
    """
    Create NotificationLog records for every user in the receiving groups.
    """
    print("notification log signal")
    print(notification)
    print(notification.receiver_groups.all())
    for group in notification.receiver_groups.all():
        print(group)
        for user in group.get_members():
            print("create log for {}".format(str(user)))
            log = NotificationLog(notification=notification, user=user)
            log.save()


@receiver(m2m_changed, sender=Notification.receiver_groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, Notification):
        if 'pk_set' in kwargs:
            if action == 'post_add':
                notification_created.send(sender=sender, notification=instance, kwargs=kwargs)