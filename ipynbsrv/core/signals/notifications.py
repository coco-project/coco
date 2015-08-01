from django.db.models.signals import post_save
from django.dispatch import receiver
from ipynbsrv.core.models import Notification, NotificationLog
from ipynbsrv.core.signals.signals import notification_created


@receiver(notification_created)
def create_notificationlogs(sender, notification, **kwargs):
    # create NotificationLog for every user in the receiving groups
    for group in notification.receiver_groups.all():
        for u in group.get_members():
            n = NotificationLog(notification=notification,user=user)
            n.save()


@receiver(post_save, sender=Notification)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        notification_created.send(sender=sender, notification=instance, kwargs=kwargs)
    else:
        # do nothing
        pass
