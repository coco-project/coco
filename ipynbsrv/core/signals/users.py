from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.core.signals.signals import user_created, \
    user_deleted, user_modified


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
