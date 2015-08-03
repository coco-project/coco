from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.errors import DirectoryNotFoundError, StorageBackendError
from ipynbsrv.core import settings
from ipynbsrv.core.helpers import get_storage_backend
from ipynbsrv.core.models import CollaborationGroup, Share
from ipynbsrv.core.signals.signals import *
from os import path


storage_backend = get_storage_backend()


@receiver(share_created)
def add_creator_to_share_group(sender, share, **kwargs):
    """
    Add the share creator to the share's internal backend group.
    """
    if share is not None:
        share.add_member(share.owner)


@receiver(collaboration_group_member_added)
def add_user_to_share_groups(sender, group, user, **kwargs):
    """
    Add the user to all share groups the entered group has access to.
    """
    if group is not None and user is not None:
        for share in group.shares.all():
            # TODO: doesn't trigger signal because we're within a group signal already
            share.add_member(user)


@receiver(share_access_group_added)
def add_group_members_to_share_group(sender, share, group, **kwargs):
    """
    Add all members from the access group to the share group.
    """
    if share is not None and group is not None:
        for user in group.get_members():
            share.add_member(user)


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
            storage_backend.set_dir_gid(share_dir, share.backend_group.backend_id)
            storage_backend.set_dir_mode(share_dir, 2770)
        except StorageBackendError as ex:
            share.delete()  # XXX: cleanup
            raise ex


@receiver(share_deleted)
def delete_backend_group(sender, share, **kwargs):
    """
    Delete the backend group created internally for this share.
    """
    if share is not None:
        share.backend_group.delete()


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


@receiver(share_access_group_removed)
def remove_group_members_from_share_group(sender, share, group, **kwargs):
    """
    Remove all members from the access group from the share group.
    """
    if share is not None and group is not None:
        leave = False
        for user in group.get_members():
            if user == share.owner:
                leave = True
            else:
                for access_group in share.access_groups.all():
                    if access_group != group:
                        if access_group.user_is_member(user):
                            leave = True
                            break
            if not leave:
                share.remove_member(user)


@receiver(collaboration_group_member_removed)
def remove_user_from_share_groups(sender, group, user, **kwargs):
    """
    Remove the user from share groups the group had access to.

    Scenario: A user is within a group and a share access is granted to that group.
    The user is added to the share group for that reason. Now, he leaves the group
    (not the share directly), so we have to make sure he also leaves all the share groups.
    """
    if group is not None and user is not None:
        leave = False
        for share in group.shares.all():
            if user == share.owner:
                leave = True
            else:
                for access_group in share.access_groups.all():
                    if access_group != group:
                        if access_group.user_is_member(user):
                            leave = True
                            break
            if not leave:
                # TODO: doesn't trigger signal because we're within a group signal already
                share.remove_member(user)


@receiver(m2m_changed, sender=Share.access_groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    action = kwargs.get('action')
    if isinstance(instance, Share):
        if 'pk_set' in kwargs:  # access groups
            # get the group objects
            groups = []
            if kwargs.get('pk_set') is not None:
                for group_pk in kwargs.get('pk_set'):
                    groups.append(CollaborationGroup.objects.get(pk=group_pk))
            # trigger the signals
            if action == 'post_add':
                for group in groups:
                    share_access_group_added.send(
                        sender=sender,
                        share=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'pre_clear':
                for group in instance.access_groups.all():
                    share_access_group_removed.send(
                        sender=sender,
                        share=instance,
                        group=group,
                        kwargs=kwargs
                    )
            elif action == 'post_remove':
                for group in groups:
                    share_access_group_removed.send(
                        sender=sender,
                        share=instance,
                        group=group,
                        kwargs=kwargs
                    )


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
