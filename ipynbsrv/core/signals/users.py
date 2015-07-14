from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf.global_vars import STORAGE_BACKEND as storage_backend
from ipynbsrv.contract.errors import StorageBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.signals.signals import user_created, user_deleted, user_modified


@receiver(user_created)
def create_user_directories(sender, user, **kwargs):
    """
    Every user needs his home and public directories, so we create them here.
    """
    if user is not None:
        username = user.get_username()
        home_dir = settings.STORAGE_DIR_HOME + username
        public_dir = settings.STORAGE_DIR_PUBLIC + username
        try:
            # home directory
            storage_backend.mk_dir(home_dir)
            storage_backend.set_dir_owner(home_dir, username)
            storage_backend.set_dir_group(home_dir, username)
            storage_backend.set_dir_mode(home_dir, 0700)
            # public directory
            storage_backend.mk_dir(public_dir)
            storage_backend.set_dir_owner(public_dir, username)
            storage_backend.set_dir_group(public_dir, username)
            storage_backend.set_dir_mode(public_dir, 0755)
        except StorageBackendError as ex:
            # TODO: error handling
            raise ex


@receiver(user_deleted)
def remove_user_directories(sender, user, **kwargs):
    """
    When a user is deleted we can safely remove his home and public directory.
    """
    if user is not None:
        username = user.get_username()
        home_dir = settings.STORAGE_DIR_HOME + username
        public_dir = settings.STORAGE_DIR_PUBLIC + username
        try:
            storage_backend.rm_dir(home_dir, recursive=True)
            storage_backend.rm_dir(public_dir, recursive=True)
        except StorageBackendError as ex:
            # TODO: error handling
            raise ex
#
#
# @receiver(user_modified)
# def user_modified_handler(sender, user, fields, **kwargs):
#     if settings.DEBUG:
#         print "user_modified_handler receiver fired"
#     kwargs = kwargs['kwargs']
#     if fields is not None and 'groups' in fields:
#         # get the group objects
#         groups = []
#         if kwargs['pk_set'] is not None:
#             for group_pk in kwargs['pk_set']:
#                 groups.append(Group.objects.get(pk=group_pk))
#         # trigger the signals
#         action = kwargs['action']
#         if action == 'post_add':
#             for group in groups:
#                 group_member_added.send(sender=sender, group=group, users=[user], kwargs=kwargs)
#         elif action == 'pre_clear':
#             for group in user.groups.all():
#                 group_member_removed.send(sender=sender, group=group, users=[user], kwargs=kwargs)
#         elif action == 'post_remove':
#             for group in groups:
#                 group_member_removed.send(sender=sender, group=group, users=[user], kwargs=kwargs)
#
#
# """
#
#     Calling custom signals
#
# """
#
#
# @receiver(m2m_changed, sender=User.groups.through)
# def m2m_changed_handler(sender, instance, **kwargs):
#     if isinstance(instance, User):
#         action = kwargs['action']
#         if action == 'post_add' or action == 'pre_clear' or action == 'post_remove':
#             user_modified.send(sender=sender, user=instance, fields=['groups'], kwargs=kwargs)
#
#


@receiver(post_delete, sender=User)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    user_deleted.send(sender=sender, user=instance, kwargs=kwargs)


@receiver(post_save, sender=User)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs['created']:
        user_created.send(sender=sender, user=instance, kwargs=kwargs)
    else:
        user_modified.send(sender=sender, user=instance, fields=kwargs['update_fields'], kwargs=kwargs)
