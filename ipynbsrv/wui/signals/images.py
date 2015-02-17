from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Image
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker


docker = Docker()


@receiver(image_created)
def set_docker_image_id(sender, image, **kwargs):
    """
    Signal to replace the internal dummy ID with the one from Docker.
    Since images are only created through container commits, everything else
    is already done.
    """
    if settings.DEBUG:
        print "set_docker_image_id receiver fired"
    if image is not None:
        img = docker.images(name=image.get_full_name())
        if len(img) == 1:
            image.docker_id = img.pop()
            image.save(update_fields=['docker_id'])


@receiver(image_deleted)
def remove_image_on_host(sender, image, **kwargs):
    """
    Signal receiver used to remove Docker images from the host when one is deleted from the DB.
    """
    if settings.DEBUG:
        print "remove_image_on_host receiver fired"
    if image is not None:
        img = docker.images(name=image.get_full_name())
        if len(img) == 1:
            docker.remove_image(img.pop())


@receiver(image_modified)
def image_modified_handler(sender, image, fields, **kwargs):
    if settings.DEBUG:
        print "image_modified_handler receiver fired"
    # TODO: reflect changes to docker host


# ###############################################


@receiver(post_delete, sender=Image)
def post_delete_handler(sender, instance, **kwargs):
    image_deleted.send(sender=sender, image=instance, kwargs=kwargs)


@receiver(post_save, sender=Image)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        image_created.send(sender=sender, image=instance, kwargs=kwargs)
    else:
        image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], kwargs=kwargs)
