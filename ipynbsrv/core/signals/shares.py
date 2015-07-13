from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.conf.global_vars import STORAGE_BACKEND as storage_backend
from ipynbsrv.contract.errors import StorageBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.models import Share
from ipynbsrv.core.signals.signals import share_created, share_modified, share_deleted


@receiver(share_created)
def create_share_directory(sender, share, **kwargs):
    '''
    Signal receiver that creates the filesystem directory for a created share.
    '''
    if share is not None:
        share_dir = settings.STORAGE_DIR_SHARES + share.name
        try:
            storage_backend.mk_dir(share_dir)
            # storage_backend.set_dir_owner(share_dir, 'root')
            storage_backend.set_dir_group(share_dir, share.group.name)
            storage_backend.set_dir_mode(share_dir, 2770)
        except StorageBackendError as ex:
            # TODO: error handling
            raise ex


@receiver(share_deleted)
def delete_share_directory(sender, share, **kwargs):
    '''
    Signal receiver that deletes the filesystem directory for a removed share.
    '''
    if share is not None:
        share_dir = settings.STORAGE_DIR_SHARES + share.name
        try:
            storage_backend.rm_dir(share_dir, recursive=True)
        except StorageBackendError as ex:
            # TODO: error handling
            raise ex
        share.group.delete()


# @receiver(share_modified)
# def share_modified_handler(sender, share, fields, **kwargs):
#     if settings.DEBUG:
#         print "share_modified_handler receiver fired"
#     # TODO: update share (name, owner etc)


@receiver(post_delete, sender=Share)
def post_delete_handler(sender, instance, **kwargs):
    share_deleted.send(sender=sender, share=instance, kwargs=kwargs)


@receiver(post_save, sender=Share)
def post_save_handler(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        share_created.send(sender, share=instance, kwargs=kwargs)
    else:
        share_modified.send(sender, share=instance, fields=kwargs['update_fields'], kwargs=kwargs)
