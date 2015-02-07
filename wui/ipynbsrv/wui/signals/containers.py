import re
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container, Image
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker


docker = Docker()


@receiver(container_commited)
def commit_on_host(sender, container, image, **kwargs):
    """
    Signal to create a new image by commiting a container.
    """
    if settings.DEBUG:
        print "commit_on_host receiver fired"
    if container is not None and image is not None:
        docker.commit(container.docker_id, image.name)


@receiver(container_created)
def create_on_host(sender, container, **kwargs):
    """
    Signal to create new containers and replace the ID with the one from Docker.
    """
    if settings.DEBUG:
        print "create_on_host receiver fired"
    if container is not None:
        # get all needed ports
        ports = container.image.exposed_ports.split(',')
        ports.append(container.image.proxied_port)
        ret = docker.create_container(name=container.name, image=container.image.id, cmd=container.image.cmd,
                                      ports=ports, volumes=None)
        container.docker_id = ret['Id']
        container.save(update_fields=['docker_id'])


@receiver(container_deleted)
def delete_on_host(sender, container, **kwargs):
    """
    Signal to delete the container on the Docker host.
    """
    if settings.DEBUG:
        print "delete_on_host receiver fired"
    if container is not None:
        try:
            docker.remove_container(container.docker_id)
        except:
            pass  # TODO: does not exist. what to do?
        # TODO: is that true? what about clones of clones etc.?
        # clone images are only used internally and can safely be removed
        # after deleting a cloned container
        if container.clone_of:
            container.image.delete()


@receiver(container_restarted)
def restart_on_host(sender, container, **kwargs):
    """
    Signal to restart the container on the Docker host.
    """
    if settings.DEBUG:
        print "restart_on_host receiver fired"
    if container is not None:
        try:
            docker.restart(container.docker_id)
        except:
            pass  # TODO: does not exist. what to do?

@receiver(container_stopped)
def stop_on_host(sender, container, **kwargs):
    """
    Signal to stop the container on the Docker host.
    """
    if settings.DEBUG:
        print "stop_on_host receiver fired"
    if container is not None:
        try:
            docker.stop(container.docker_id)
        except:
            pass  # TODO: does not exist. what to do?


@receiver(container_modified)
def container_modified_handler(sender, container, fields, **kwargs):
    if settings.DEBUG:
        print "container_modified_handler receiver fired"
    # TODO: update container on Docker host (e.g. start/stop etc.)


# ###############################################


@receiver(post_delete, sender=Container)
def post_delete_handler(sender, instance, **kwargs):
    container_deleted.send(sender=sender, container=instance, kwargs=kwargs)


@receiver(post_save, sender=Container)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        container_created.send(sender=sender, container=instance, kwargs=kwargs)
    else:
        container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], kwargs=kwargs)
