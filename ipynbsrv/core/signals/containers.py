from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.contract.errors import ContainerBackendError, \
    ContainerNotFoundError
from ipynbsrv.core.models import Container, Server
from ipynbsrv.core.signals.signals import *


@receiver(container_created)
def create_on_server(sender, container, **kwargs):
    """
    Create the newly saved container on the server's container backend.
    """
    if container is not None:
        try:
            # TODO: get_required_container_creation_fields
            result = container.server.get_container_backend().create_container({
                'name': container.get_backend_name(),
                'image': container.image.backend_pk,
                'command': container.image.command
            })
            container.backend_pk = result.get(ContainerBackend.FIELD_PK)
            container.save()
        except ContainerBackendError as ex:
            raise ex


        # # find start port for this container
        # port_mappings = PortMapping.objects.all()
        # if port_mappings.exists():
        #     exposed_port = port_mappings.latest().external + 1
        # else:
        #     exposed_port = settings.DOCKER_FIRST_PORT
        # # allocate ports and add them to the list for create_container
        # ports = []
        # for port in container.image.exposed_ports.split(','):
        #     port = int(port)
        #     ports.append(port)
        #     port_mapping = PortMapping(container=container, internal=port, external=exposed_port)
        #     port_mapping.save()
        #     exposed_port += 1
        # ports.append(container.image.proxied_port)
        # port_mapping = PortMapping(container=container, internal=container.image.proxied_port, external=exposed_port)
        # port_mapping.save()
        # # list of mountpoints
        # volumes = [
        #     os.path.join('/home/', container.owner.get_username()),
        #     os.path.join('/data/', 'public'),
        #     os.path.join('/data/', 'shares')
        # ]
        #
        # ret = ContainerTask.create_container(
        #     container_backend=container.host.get_container_backend_instance(),
        #     host=container.host, name=container.get_full_name(), image=container.image.get_full_name(),
        #     cmd=container.image.cmd.replace('{{PORT}}', str(port_mapping.external)),
        #     ports=ports, volumes=volumes
        # )
        #
        # container.docker_id = str(json.loads(ret)['data']['Id'])
        # container.save(update_fields=['docker_id'])


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
            raise ex


@receiver(post_delete, sender=Container)
def post_delete_handler(sender, instance, **kwargs):
    container_deleted.send(sender=sender, container=instance, kwargs=kwargs)


@receiver(post_save, sender=Container)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        container_created.send(sender=sender, container=instance, kwargs=kwargs)
    else:
        container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], kwargs=kwargs)
