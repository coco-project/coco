from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.contract.errors import ConnectionError, ContainerBackendError, ContainerImageNotFoundError
from ipynbsrv.core.models import Container, ContainerImage, Server
from ipynbsrv.core.signals.signals import *


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


@receiver(container_deleted)
def delete_internal_image_if_latest(sender, container, **kwargs):
    """
    Delete the internal only image if this is the last container using it.
    """
    if container is not None:
        try:
            if container.is_image_based() and container.image.is_internal and not container.has_clones():
                if not Container.objects.filter(image=container.image).exists():
                    container.image.delete()
        except ContainerImage.DoesNotExist:
            pass


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
                    backend.delete_container_image(image.backend_pk, force=True)
                except ContainerImageNotFoundError:
                    pass  # already removed
                except ContainerBackendError as ex:
                    # XXX: restore?
                    raise ex


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
