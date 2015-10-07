from coco.contract.backends import ContainerBackend
from coco.contract.errors import ContainerBackendError, ContainerImageNotFoundError
from coco.core.models import CollaborationGroup, ContainerImage, Server
from coco.core.signals.signals import *
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver


@receiver(container_committed)
def create_image_on_server(sender, container, image, **kwargs):
    """
    Create the container image for the committed container on the server.
    """
    if container is not None and image is not None:
        backend = container.server.get_container_backend()
        try:
            result = backend.create_container_image(container.backend_pk, image.name)
            image.backend_pk = result.get(ContainerBackend.KEY_PK)
            image.save()
        except ContainerBackendError as ex:
            image.delete()
            raise ex


@receiver(container_image_deleted)
def delete_related_notifications(sender, image, **kwargs):
    """
    Delete the container image's related notifications upon deletion.
    """
    if image is not None and hasattr(image, 'related_notifications'):
        image.related_notifications.all().delete()


@receiver(container_image_deleted)
def delete_on_server(sender, image, **kwargs):
    """
    When an image is removed from the database, we can remove it from the servers as well.
    """
    if image is not None:
        for server in Server.objects.all():
            if server.is_container_host():
                try:
                    # FIXME: isn't deleted....
                    backend = server.get_container_backend()
                    backend.delete_container_image(image.backend_pk)
                except ContainerImageNotFoundError:
                    pass  # already removed
                except ContainerBackendError:
                    # XXX: restore?
                    # raise ex
                    pass


@receiver(m2m_changed, sender=ContainerImage.access_groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, ContainerImage):
        if 'pk_set' in kwargs:  # access groups
            # get the group objects
            groups = []
            if kwargs.get('pk_set') is not None:
                for group_pk in kwargs.get('pk_set'):
                    groups.append(CollaborationGroup.objects.get(pk=group_pk))
            # trigger the signals
            if action == 'post_add':
                for group in groups:
                    container_image_access_group_added.send(
                        sender=sender,
                        image=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for group in instance.access_groups.all():
                    container_image_access_group_removed.send(
                        sender=sender,
                        image=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for group in groups:
                    container_image_access_group_removed.send(
                        sender=sender,
                        image=instance,
                        group=group,
                        kwargs=kwargs
                    )


@receiver(post_delete, sender=ContainerImage)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    container_image_deleted.send(sender=sender, image=instance, kwargs=kwargs)


@receiver(post_save, sender=ContainerImage)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        container_image_created.send(sender=sender, image=instance, kwargs=kwargs)
    else:
        container_image_modified.send(
            sender=sender,
            image=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
