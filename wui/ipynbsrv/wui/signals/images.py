from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import Image
from ipynbsrv.wui.signals.signals import image_created, image_deleted, image_modified
from ipynbsrv.wui.tools import Docker


docker = Docker()


"""
Handler triggered by image_created signals.
"""
@receiver(image_created)
def created_handler(sender, image, kwargs):
    if settings.DEBUG:
        print "image_created handler fired"


"""
Handler triggered by image_deleted signals.
"""
@receiver(image_deleted)
def deleted_handler(sender, image, **kwargs):
    if settings.DEBUG:
        print "Deleting image via signal..."
    img_id = docker.images(name=image.name).first()
    if img_id:
        docker.remove_image(img_id)


"""
Handler triggered by image_modified signals.
"""
@receiver(image_modified)
def modified_handler(sender, image, fields, kwargs):
    if settings.DEBUG:
        print "image_modified handler fired"


"""
Internal receivers to map the Django built-in signals to custom ones.
"""
@receiver(post_delete, sender=Image)
def post_delete_handler(sender, instance, **kwargs):
    image_deleted.send(sender=sender, image=instance, kwargs=kwargs)

@receiver(post_save, sender=Image)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        image_created.send(sender=sender, image=instance, kwargs=kwargs)
    else:
        image_modified.send(sender=sender, image=instance, fields=kwargs['update_fields'], kwargs=kwargs)
