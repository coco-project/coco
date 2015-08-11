from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.contract.errors import ContainerBackendError, ContainerNotFoundError
from ipynbsrv.core import settings
from ipynbsrv.core.helpers import get_storage_backend
from ipynbsrv.core.models import Container, ContainerImage, PortMapping
from ipynbsrv.core.signals.signals import *
from os import path
import time


storage_backend = get_storage_backend()


def create_container_port_mappings(container):
    """
    Create the port mappings for the given container.

    :param container: The container to create the mappings for.
    """
    ports = []
    image = None
    if container.is_image_based():
        image = container.image
    elif container.is_clone() and container.clone_of.is_image_based():
        image = container.clone_of.image

    if image:
        protected_port = image.protected_port
        public_ports = image.public_ports
        if protected_port:
            mapping = PortMapping(
                server=container.server,
                container=container,
                external_port=PortMapping.get_available_server_port(container.server),
                internal_port=protected_port
            )
            mapping.save()
            ports.append({
                ContainerBackend.PORT_MAPPING_KEY_ADDRESS: mapping.server.internal_ip,
                ContainerBackend.PORT_MAPPING_KEY_EXTERNAL: mapping.external_port,
                ContainerBackend.PORT_MAPPING_KEY_INTERNAL: mapping.internal_port
            })
        if public_ports:
            for port in public_ports.split(','):
                mapping = PortMapping(
                    server=container.server,
                    container=container,
                    external_port=PortMapping.get_available_server_port(container.server),
                    internal_port=port
                )
                mapping.save()
                ports.append({
                    ContainerBackend.PORT_MAPPING_KEY_ADDRESS: '0.0.0.0',
                    ContainerBackend.PORT_MAPPING_KEY_EXTERNAL: mapping.external_port,
                    ContainerBackend.PORT_MAPPING_KEY_INTERNAL: mapping.internal_port
                })
    return ports


@receiver(container_created)
def create_on_server(sender, container, **kwargs):
    """
    Create the newly saved container on the server's container backend.
    """
    if container is not None:
        ports = create_container_port_mappings(container)
        clone_of = None
        cmd = None
        image = None
        if container.is_image_based():
            cmd = container.image.command
            image = container.image.backend_pk
        elif container.is_clone():
            clone_of = container.clone_of.backend_pk
            if container.clone_of.is_image_based():
                cmd = container.clone_of.image.command

        result = None
        try:
            result = container.server.get_container_backend().create_container(
                container.owner.backend_pk,
                container.owner.backend_id,
                container.name,
                ports,
                [
                    {   # home directory
                        ContainerBackend.VOLUME_KEY_SOURCE: path.join(storage_backend.base_dir, settings.STORAGE_DIR_HOME),
                        ContainerBackend.VOLUME_KEY_TARGET: '/home'
                    },
                    {   # public directory
                        ContainerBackend.VOLUME_KEY_SOURCE: path.join(storage_backend.base_dir, settings.STORAGE_DIR_PUBLIC),
                        ContainerBackend.VOLUME_KEY_TARGET: path.join('/data', 'public')
                    },
                    {   # shares directory
                        ContainerBackend.VOLUME_KEY_SOURCE: path.join(storage_backend.base_dir, settings.STORAGE_DIR_SHARES),
                        ContainerBackend.VOLUME_KEY_TARGET: path.join('/data', 'shares')
                    }
                ],
                cmd=cmd,
                base_url=container.get_backend_base_url(),
                image=image,
                clone_of=clone_of
            )
        except ContainerBackendError as ex:
            container.delete()  # XXX: cleanup?
            raise ex

        if result.get(ContainerBackend.CONTAINER_KEY_CLONE_IMAGE, None) is None:
            container.backend_pk = result.get(ContainerBackend.KEY_PK)
        else:
            container.backend_pk = result.get(ContainerBackend.CONTAINER_KEY_CLONE_CONTAINER).get(ContainerBackend.KEY_PK)
            # an image has been created internally, add it to our DB
            # TODO: what is the base container doesn't base on an image?
            backend_image = result.get(ContainerBackend.CONTAINER_KEY_CLONE_IMAGE)
            image = ContainerImage(
                backend_pk=backend_image.get(ContainerBackend.KEY_PK),
                name=container.clone_of.image.name + '-clone-' + str(int(time.time())),
                description="Internal only image created during the cloning process of container %s." % container.clone_of.get_friendly_name(),
                command=container.clone_of.image.command,
                protected_port=container.clone_of.image.protected_port,
                public_ports=container.clone_of.image.public_ports,
                owner=container.owner.django_user,
                is_internal=True
            )
            image.save()
            container.image = image
        container.save()


@receiver(container_deleted)
def delete_related_notifications(sender, container, **kwargs):
    """
    Delete the container's related notifications upon deletion.
    """
    if container is not None and hasattr(container, 'related_notifications'):
        container.related_notifications.all().delete()


@receiver(container_deleted)
def delete_on_server(sender, container, **kwargs):
    """
    Delete the destroyed container on the container_backend.
    """
    if container is not None:
        try:
            container.server.get_container_backend().delete_container(container.backend_pk)
            # cleanup internal images
            # if container.is_image_based() and container.image.is_internal and not container.has_clones():
            #     if not Container.objects.filter(image=container.image).exists():
            #         container.image.delete()
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
    if 'created' in kwargs and kwargs.get('created'):
        container_created.send(sender=sender, container=instance, kwargs=kwargs)
    else:
        container_modified.send(
            sender=sender,
            container=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
