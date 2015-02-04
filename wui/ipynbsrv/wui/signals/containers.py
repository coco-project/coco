import re
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Container, Image
from ipynbsrv.wui.signals.signals import container_commited, container_created, container_deleted, container_modified, \
    container_restarted, container_started, container_stopped, image_created
from ipynbsrv.wui.tools import Docker


docker = Docker()


@receiver(container_commited)
def commited_handler(sender, container, image, **kwargs):
    if settings.DEBUG:
        print "container_commited handler fired"
    image_created.send(sender=sender, image=image, kwargs=kwargs)


@receiver(container_created)
def created_handler(sender, container, **kwargs):
    if settings.DEBUG:
        print "container_created handler fired"
    # TODO


@receiver(container_deleted)
def deleted_handler(sender, container, **kwargs):
    if settings.DEBUG:
        print "container_deleted handler fired"
    if container.docker_id in docker.containers():
        docker.remove_container(container.docker_id)


@receiver(container_modified)
def modified_handler(sender, container, fields, **kwargs):
    if settings.DEBUG:
        print "container_modified handler fired"
    # TODO


@receiver(container_restarted)
def restarted_handler(sender, container, **kwargs):
    if settings.DEBUG:
        print "container_restarted handler fired"
    if container.docker_id in docker.containers():
        docker.restart(container=container.docker_id)


@receiver(container_started)
def started_handler(sender, container, **kwargs):
    if settings.DEBUG:
        print "container_started handler fired"
    # TOOD


@receiver(container_stopped)
def stopped_handler(sender, container, **kwargs):
    if settings.DEBUG:
        print "container_stopped handler fired"
    if container.docker_id in docker.containers(all=False):
        docker.stop(container=container.docker_id)


"""
Internal receivers to map the Django built-in signals into custom ones.
"""
@receiver(post_delete, sender=Container, dispatch_uid='ipynbsrv.wui.signals.containers.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    container_deleted.send(sender, container=instance)

@receiver(post_save, sender=Container, dispatch_uid='ipynbsrv.wui.signals.containers.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        container_created.send(sender, container=instance)
    else:
        container_modified.send(sender, container=instance, fields=kwargs['update_fields'])
