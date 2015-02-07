import re
from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container, Image
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker


docker = Docker()


@receiver(post_container_commited)
def commit_on_host(sender, container, image, **kwargs):
    if settings.DEBUG:
        print "commit_on_host receiver fired"
    img = docker.commit(container.id, image.name)
    image.id = img['Id']


@receiver(pre_container_created)
def create_on_host(sender, container, **kwargs):
    """
    pre_ because we need the Docker ID.
    """
    if settings.DEBUG:
        print "create_on_host receiver fired"
    ports = container.image.exposed_ports.split(',')
    ports.append(container.image.proxied_port)
    ret = docker.create_container(name=container.name, image=container.image, cmd=container.image.cmd,
                                  ports=ports, volumes=None)
    container.id = ret['Id']


@receiver(post_container_deleted)
def delete_on_host(sender, container, **kwargs):
    if settings.DEBUG:
        print "delete_on_host receiver fired"
    if container.docker_id in docker.containers():
        docker.remove_container(container.id)
    # clone images are only used internally and can safely be removed
    # after deleting a cloned container
    if container.clone_of:
        container.image.delete()


@receiver(post_container_restarted)
def restart_on_host(sender, container, **kwargs):
    if settings.DEBUG:
        print "restart_on_host receiver fired"
    if container.id in docker.containers():
        docker.restart(container=container.id)


@receiver(post_container_stopped)
def stop_on_host(sender, container, **kwargs):
    if settings.DEBUG:
        print "stop_on_host receiver fired"
    if container.id in docker.containers(all=False):
        docker.stop(container=container.id)


@receiver(post_container_modified)
def container_modified_handler(sender, container, fields, **kwargs):
    if settings.DEBUG:
        print "container_modified_handler receiver fired"
    # TODO: update container on Docker host (e.g. start/stop etc.)


# ###############################################


@receiver(post_delete, sender=Container)
def post_delete_handler(sender, instance, **kwargs):
    post_container_deleted.send(sender=sender, container=instance, kwargs=kwargs)
    container_deleted.send(sender=sender, container=instance, action='post_delete', kwargs=kwargs)


@receiver(post_delete, sender=Container)
def pre_delete_handler(sender, instance, **kwargs):
    pre_container_deleted.send(sender=sender, container=instance, kwargs=kwargs)
    container_deleted.send(sender=sender, container=instance, action='pre_delete', kwargs=kwargs)


@receiver(post_save, sender=Container)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        post_container_created.send(sender=sender, container=instance, kwargs=kwargs)
        container_created.send(sender=sender, container=instance, action='post_save', kwargs=kwargs)
    else:
        post_container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], action='post_save', kwargs=kwargs)


@receiver(pre_save, sender=Container)
def pre_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        pre_container_created.send(sender=sender, container=instance, kwargs=kwargs)
        container_created.send(sender=sender, container=instance, action='pre_save', kwargs=kwargs)
    else:
        pre_container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        container_modified.send(sender=sender, container=instance, fields=kwargs['update_fields'], action='pre_save', kwargs=kwargs)
