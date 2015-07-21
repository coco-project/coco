from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.errors import ContainerBackendError, ContainerImageNotFoundError
from ipynbsrv.core.models import ContainerImage, Server
from ipynbsrv.core.signals.signals import container_image_created, \
    container_image_deleted, container_image_modified
import logging


logger = logging.getLogger(__name__)


@receiver(container_image_deleted)
def remove_on_server(sender, image, **kwargs):
    """
    When an image is removed from the database, we can remove it from the servers as well.
    """
    if image is not None:
        for server in Server.objects.all():
            if server.is_container_host():
                backend = server.get_container_backend()
                if backend.container_image_exists(image.backend_pk):
                    try:
                        backend.delete_container_image(image.backend_pk)
                    except ContainerImageNotFoundError:
                        pass  # already removed
                    except ContainerBackendError as ex:
                        # XXX: restore?
                        raise ex
                else:
                    logger.warn(
                        "Container image %s doesn't exist on server %s. Not removing it."
                        % (image, server)
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
    if 'created' in kwargs and kwargs['created']:
        container_image_created.send(sender=sender, image=instance, kwargs=kwargs)
    else:
        container_image_modified.send(
            sender=sender,
            image=instance,
            fields=kwargs['update_fields'],
            kwargs=kwargs
        )
