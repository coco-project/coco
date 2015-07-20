from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf.helpers import *
from ipynbsrv.contract.errors import *
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser
from ipynbsrv.core.signals.signals import user_created, user_deleted, user_modified
import logging


logger = logging.getLogger(__name__)
storage_backend = get_storage_backend()


@receiver(user_created)
def create_user_directories(sender, user, **kwargs):
    """
    Every user needs his home and public directories, so we create them here.
    """
    if user is not None:
        username = user.django_user.get_username()
        # home directory
        home_dir = settings.STORAGE_DIR_HOME + username
        if not storage_backend.dir_exists(home_dir):
            try:
                storage_backend.mk_dir(home_dir)
                storage_backend.set_dir_uid(home_dir, user.backend_id)
                storage_backend.set_dir_gid(home_dir, user.primary_group.backend_id)
                storage_backend.set_dir_mode(home_dir, 0700)
            except StorageBackendError as ex:
                raise ex
            except Exception as ex:
                raise ex
        else:
            logger.warn("Home directory for user %s already exists." % username)
        # public directory
        public_dir = settings.STORAGE_DIR_PUBLIC + username
        if not storage_backend.dir_exists(public_dir):
            try:
                storage_backend.mk_dir(public_dir)
                storage_backend.set_dir_uid(public_dir, user.backend_id)
                storage_backend.set_dir_gid(public_dir, user.primary_group.backend_id)
                storage_backend.set_dir_mode(public_dir, 0755)
            except StorageBackendError as ex:
                raise ex
            except Exception as ex:
                raise ex
        else:
            logger.warn("Public directory for user %s already exists." % username)


@receiver(user_deleted)
def delete_user_on_internal_ldap(sender, user, **kwargs):
    """
    In case the BackendUser record is removed, we need to cleanup the internal LDAP server.
    """
    if user is not None:
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.delete_user(user.backend_pk)
            user.django_user.delete()
            user.primary_group.delete()
        except UserNotFoundError:
            pass  # already deleted
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(user_deleted)
def remove_user_directories(sender, user, **kwargs):
    """
    When a user is deleted we can safely remove his home and public directory.
    """
    if user is not None:
        username = user.django_user.get_username()
        # home directory
        home_dir = settings.STORAGE_DIR_HOME + username
        if storage_backend.dir_exists(home_dir):
            try:
                storage_backend.rm_dir(home_dir, recursive=True)
            except StorageBackendError as ex:
                raise ex
            except Exception as ex:
                raise ex
        else:
            logger.warn("Home directory for user %s doesn't exist." % username)
        # public directory
        public_dir = settings.STORAGE_DIR_PUBLIC + username
        if storage_backend.dir_exists(public_dir):
            try:
                storage_backend.rm_dir(public_dir, recursive=True)
            except StorageBackendError as ex:
                raise ex
            except Exception as ex:
                raise ex
        else:
            logger.warn("Public directory for user %s doesn't exist." % username)


@receiver(post_delete, sender=BackendUser)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    user_deleted.send(sender=sender, user=instance, kwargs=kwargs)


@receiver(post_save, sender=BackendUser)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs['created']:
        user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], kwargs=kwargs)
