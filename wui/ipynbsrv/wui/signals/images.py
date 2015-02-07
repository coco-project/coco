from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Image
from ipynbsrv.wui.signals.signals import *
from ipynbsrv.wui.tools import Docker


docker = Docker()


@receiver(post_image_deleted)
def remove_image_on_host(sender, image, **kwargs):
    """
    Signal receiver used to remove Docker images from the host
    when one is deleted from the DB.
    """
    if settings.DEBUG:
        print "remove_image_on_host receiver fired"
    images = docker.images(name=image.name)
    if len(images) == 1:
        docker.remove_image(images.pop())


@receiver(post_image_modified)
def image_modified_handler(self, image, fields, **kwargs):
    if settings.DEBUG:
        print "image_modified_handler receiver fired"
    # TODO: reflect changes to docker host


# ###############################################


@receiver(post_delete, sender=Image)
def post_delete_handler(sender, instance, **kwargs):
    post_image_deleted.send(sender=sender, image=instance, kwargs=kwargs)
    image_deleted.send(sender=sender, image=instance, action='post_delete' kwargs=kwargs)


@receiver(pre_delete, sender=Image)
def pre_delete_handler(sender, instance, **kwargs):
    pre_image_deleted.send(sender=sender, image=instance, kwargs=kwargs)
    image_deleted.send(sender=sender, image=instance, action='pre_delete' kwargs=kwargs)


@receiver(post_save, sender=Image)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        post_image_created.send(sender=sender, image=instance, kwargs=kwargs)
        image_created.send(sender=sender, image=instance, action='post_save' kwargs=kwargs)
    else:
        post_image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], action='post_save' kwargs=kwargs)


@receiver(pre_save, sender=Image)
def pre_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        pre_image_created.send(sender=sender, image=instance, kwargs=kwargs)
        image_created.send(sender=sender, image=instance, action='pre_save' kwargs=kwargs)
    else:
        pre_image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], action='pre_save' kwargs=kwargs)
