from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf.helpers import get_internal_ldap_connected, get_storage_backend
from ipynbsrv.contract.backends import UserBackend
from ipynbsrv.contract.errors import DirectoryNotFoundError, StorageBackendError, \
    UserBackendError, UserNotFoundError
from ipynbsrv.core import settings
from ipynbsrv.core.models import BackendUser
from ipynbsrv.core.signals.signals import backend_user_created, \
    backend_user_deleted, backend_user_modified
import logging
from os import path


logger = logging.getLogger(__name__)
storage_backend = get_storage_backend()


@receiver(backend_user_created)
def create_home_directory(sender, user, **kwargs):
    """
    Every user needs a home directory. Create it right after user creation.
    """
    if user is not None:
        home_dir = path.join(settings.STORAGE_DIR_HOME, user.backend_pk)
        if not storage_backend.dir_exists(home_dir):
            try:
                storage_backend.mk_dir(home_dir)
                storage_backend.set_dir_uid(home_dir, user.backend_id)
                storage_backend.set_dir_gid(home_dir, user.primary_group.backend_id)
                storage_backend.set_dir_mode(home_dir, 0700)
            except StorageBackendError as ex:
                raise ex
        else:
            logger.warn("Home directory for user %s already exists." % user.django_user.get_username())


@receiver(backend_user_created)
def create_on_internal_ldap(sender, user, **kwargs):
    """
    BackendUser instances are used to represent external backends (e.g. LDAP) users.

    If such a user is created, we should therefor create the user on the backend.
    """
    if user is not None:
        username = user.backend_pk
        internal_ldap = get_internal_ldap_connected()
        try:
            created = internal_ldap.create_user({
                'username': username,
                'password': user.django_user.password,
                'uidNumber': user.backend_id,
                'gidNumber': user.primary_group.backend_id,
                'homeDirectory': "/home/" + username  # TODO: make variable/constant
            })
            # FIXME: this is the first time we really know the ID/PK given by the backend.
            # all other operations having used to old ones might not be valid anymore...
            user.backend_id = created.get(UserBackend.FIELD_ID)
            user.backend_pk = created.get(UserBackend.FIELD_PK)
            user.save()
        except UserBackendError as ex:
            user.delete()  # XXX: cleanup?
            raise ex
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(backend_user_created)
def create_public_directory(sender, user, **kwargs):
    """
    Every user needs a public directory. Create it right after user creation.
    """
    if user is not None:
        public_dir = path.join(settings.STORAGE_DIR_PUBLIC, user.backend_pk)
        if not storage_backend.dir_exists(public_dir):
            try:
                storage_backend.mk_dir(public_dir)
                storage_backend.set_dir_uid(public_dir, user.backend_id)
                storage_backend.set_dir_gid(public_dir, user.primary_group.backend_id)
                storage_backend.set_dir_mode(public_dir, 0755)
            except StorageBackendError as ex:
                raise ex
        else:
            logger.warn("Public directory for user %s already exists." % user.django_user.get_username())


@receiver(backend_user_deleted)
def delete_on_internal_ldap(sender, user, **kwargs):
    """
    In case the BackendUser record is deleted, we need to cleanup the LDAP server.
    """
    if user is not None:
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.delete_user(user.backend_pk)
            user.delete()
            user.primary_group.delete()
        except UserNotFoundError:
            pass  # already deleted
        except UserBackendError as ex:
            # XXX: recreate?
            raise ex
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(backend_user_deleted)
def remove_home_directory(sender, user, **kwargs):
    """
    When a user is deleted we can safely remove his home directory.
    """
    if user is not None:
        home_dir = path.join(settings.STORAGE_DIR_HOME, user.backend_pk)
        if storage_backend.dir_exists(home_dir):
            try:
                storage_backend.rm_dir(home_dir, recursive=True)
            except DirectoryNotFoundError:
                pass  # already deleted
            except StorageBackendError as ex:
                raise ex
        else:
            logger.warn("Home directory for user %s doesn't exist." % user.django_user.get_username())


@receiver(backend_user_deleted)
def remove_public_directory(sender, user, **kwargs):
    """
    When a user is deleted we can safely remove his public directory.
    """
    if user is not None:
        public_dir = path.join(settings.STORAGE_DIR_PUBLIC, user.backend_pk)
        if storage_backend.dir_exists(public_dir):
            try:
                storage_backend.rm_dir(public_dir, recursive=True)
            except DirectoryNotFoundError:
                pass  # already deleted
            except StorageBackendError as ex:
                raise ex
        else:
            logger.warn("Public directory for user %s doesn't exist." % user.django_user.get_username())


@receiver(post_delete, sender=BackendUser)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    backend_user_deleted.send(sender=sender, user=instance, kwargs=kwargs)


@receiver(post_save, sender=BackendUser)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        backend_user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        backend_user_modified.send(
            sender=sender,
            user=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
