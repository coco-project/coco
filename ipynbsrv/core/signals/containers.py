from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.conf.helpers import *
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.contract.errors import ContainerBackendError, \
    ContainerNotFoundError
from ipynbsrv.core import settings
from ipynbsrv.core.models import Container
from ipynbsrv.core.signals.signals import *
from os import path


storage_backend = get_storage_backend()


@receiver(container_created)
def create_on_server(sender, container, **kwargs):
    """
    Create the newly saved container on the server's container backend.
    """
    if container is not None:
        try:
            result = container.server.get_container_backend().create_container(
                container.get_backend_name(),
                container.image.backend_pk,
                [],
                [
                    {   # home directory
                        # TODO: check if we should better use /home/user, because if we create an image
                        # from the container, i.e. Docker keeps the mounts (from old users).
                        'source': path.join(storage_backend.base_dir, settings.STORAGE_DIR_HOME),
                        'target': path.join('/home', container.owner.backend_pk)
                    },
                    {   # public directory
                        'source': path.join(storage_backend.base_dir, settings.STORAGE_DIR_PUBLIC),
                        'target': path.join('/data', 'public')
                    },
                    {   # shares directory
                        'source': path.join(storage_backend.base_dir, settings.STORAGE_DIR_SHARES),
                        'target': path.join('/data', 'shares')
                    }
                ],
                cmd=container.image.command
            )
            container.backend_pk = result.get(ContainerBackend.KEY_PK)
            container.save()
        except ContainerBackendError as ex:
            container.delete()  # XXX: cleanup?
            raise ex


@receiver(container_deleted)
def delete_on_server(sender, container, **kwargs):
    """
    Delete the destroyed container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().delete_container(
                container.backend_pk
            )
        except ContainerNotFoundError as ex:
            pass  # already deleted
        except ContainerBackendError as ex:
            # XXX: restore?
            raise ex


@receiver(container_restarted)
def restart_on_server(sender, container, **kwargs):
    """
    Restart the container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().restart_container(container.backend_pk)
        except ContainerBackendError as ex:
            raise ex


@receiver(container_resumed)
def resume_on_server(sender, container, **kwargs):
    """
    Resume the container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().resume_container(container.backend_pk)
        except ContainerBackendError as ex:
            raise ex


@receiver(container_started)
def start_on_server(sender, container, **kwargs):
    """
    Start the container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().start_container(container.backend_pk)
        except ContainerBackendError as ex:
            raise ex


@receiver(container_stopped)
def stop_on_server(sender, container, **kwargs):
    """
    Stop the container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().stop_container(container.backend_pk)
        except ContainerBackendError as ex:
            raise ex


@receiver(container_suspended)
def suspend_on_server(sender, container, **kwargs):
    """
    Suspend the container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().suspend_container(container.backend_pk)
        except ContainerBackendError as ex:
            raise ex


@receiver(post_delete, sender=Container)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    container_deleted.send(sender=sender, container=instance, kwargs=kwargs)


@receiver(post_save, sender=Container)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs['created']:
        container_created.send(sender=sender, container=instance, kwargs=kwargs)
    else:
        container_modified.send(
            sender=sender,
            container=instance,
            fields=kwargs['update_fields'],
            kwargs=kwargs
        )
