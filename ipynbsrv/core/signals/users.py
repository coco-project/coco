from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf import global_vars
from ipynbsrv.contract.errors import StorageBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser
from ipynbsrv.core.signals.signals import user_created, user_deleted, user_modified
import logging


internal_ldap = global_vars.INTERNAL_LDAP
logger = logging.getLogger(__name__)
storage_backend = global_vars.STORAGE_BACKEND


@receiver(user_created)
def create_user_directories(sender, user, **kwargs):
    """
    Every user needs his home and public directories, so we create them here.
    """
    if user is not None:
        username = user.get_username()
        # home directory
        home_dir = settings.STORAGE_DIR_HOME + username
        if not storage_backend.dir_exists(home_dir):
            try:
                storage_backend.mk_dir(home_dir)
                storage_backend.set_dir_owner(home_dir, user.backend_pk)
                storage_backend.set_dir_group(home_dir, user.backend_pk)
                storage_backend.set_dir_mode(home_dir, 0700)
            except StorageBackendError as ex:
                logger.error("Creating the home directory for user %s failed." % username)
                logger.exception(ex)
            except Exception as ex:
                raise ex
        else:
            logger.warn("Home directory for user %s already exists." % username)
        # public directory
        public_dir = settings.STORAGE_DIR_PUBLIC + username
        if not storage_backend.dir_exists(public_dir):
            try:
                storage_backend.mk_dir(public_dir)
                storage_backend.set_dir_owner(public_dir, user.backend_pk)
                # storage_backend.set_dir_group(public_dir, user.backend_pk)
                storage_backend.set_dir_mode(public_dir, 0755)
            except StorageBackendError as ex:
                logger.error("Creating the public directory for user %s failed." % username)
                logger.exception(ex)
            except Exception as ex:
                raise ex
        else:
            logger.warn("Public directory for user %s already exists." % username)


@receiver(user_deleted)
def remove_internal_ldap_user(sender, user, **kwargs):
    """
    Upon user deletion, we need to cleanup the internal LDAP server.
    """
    if user is not None:
        # LDAP group
        if internal_ldap.group_exists(user.group.backend_pk):
            try:
                internal_ldap.delete_group(user.group.backend_pk)
            except Exception as ex:
                # TODO: error handling
                raise ex
        else:
            logger.warn("Internal LDAP group %s does not exist." % user.group)
        # LDAP user
        if internal_ldap.user_exists(user.backend_pk):
            try:
                internal_ldap.delete_user(user.backend_pk)
            except Exception as ex:
                # TODO: error handling
                raise ex
        else:
            logger.warn("Internal LDAP user %s does not exist." % user.get_username())


@receiver(user_deleted)
def remove_user_directories(sender, user, **kwargs):
    """
    When a user is deleted we can safely remove his home and public directory.
    """
    if user is not None:
        username = user.get_username()
        # home directory
        home_dir = settings.STORAGE_DIR_HOME + username
        if storage_backend.dir_exists(home_dir):
            try:
                storage_backend.rm_dir(home_dir, recursive=True)
            except StorageBackendError as ex:
                logger.error("Removing the home directory for user %s failed." % username)
                logger.exception(ex)
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
                logger.error("Removing the public directory for user %s failed." % username)
                logger.exception(ex)
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
