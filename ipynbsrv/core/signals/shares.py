from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.conf.helpers import get_storage_backend
from ipynbsrv.contract.errors import DirectoryNotFoundError, StorageBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.models import Share
from ipynbsrv.core.signals.signals import share_created, share_modified, share_deleted
from os import path


storage_backend = get_storage_backend()


@receiver(share_created)
def create_share_directory(sender, share, **kwargs):
    """
    Create the share directory on the storage backend.
    """
    if share is not None:
        share_dir = path.join(settings.STORAGE_DIR_SHARES, share.name)
        try:
            storage_backend.mk_dir(share_dir)
            storage_backend.set_dir_owner(share_dir, 'root')
            storage_backend.set_dir_gid(share_dir, share.group.backend_id)
            storage_backend.set_dir_mode(share_dir, 2770)
        except StorageBackendError as ex:
            share.delete()  # XXX: cleanup
            raise ex


@receiver(share_deleted)
def delete_share_directory(sender, share, **kwargs):
    """
    Remove the share directory from the storage backend.
    """
    if share is not None:
        share_dir = path.join(settings.STORAGE_DIR_SHARES, share.name)
        if storage_backend.dir_exists(share_dir):
            try:
                storage_backend.rm_dir(share_dir, recursive=True)
            except DirectoryNotFoundError:
                pass  # already deleted
            except StorageBackendError as ex:
                # XXX: restore share?
                raise ex


@receiver(post_delete, sender=Share)
def post_share_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    share_deleted.send(sender=sender, share=instance, kwargs=kwargs)


@receiver(post_save, sender=Share)
def post_share_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        share_created.send(sender=sender, share=instance, kwargs=kwargs)
    else:
        share_modified.send(
            sender=sender,
            share=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
