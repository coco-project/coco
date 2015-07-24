from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.core.models import CollaborationGroup
from ipynbsrv.core.signals.signals import collaboration_group_created, \
    collaboration_group_deleted, collaboration_group_modified


@receiver(collaboration_group_deleted)
def delete_django_group(sender, group, **kwargs):
    """
    Delete the internal Django group on delete.
    """
    if group is not None:
        group.django_group.delete()


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
