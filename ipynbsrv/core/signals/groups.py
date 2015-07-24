from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_delete, post_save
from ipynbsrv.conf.helpers import *
from ipynbsrv.contract.backends import GroupBackend
from ipynbsrv.contract.errors import *
from ipynbsrv.core.signals.signals import *


@receiver(group_member_added)
def add_member_to_internal_ldap_group(sender, group, user, **kwargs):
    """
    When ever a member is added to a group we need to sync the LDAP group.
    """
    if group is not None and user is not None and \
            hasattr(group, 'backend_group') and hasattr(user, 'backend_user'):
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.add_group_member(group.backend_group.backend_pk, user.backend_user.backend_pk)
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(group_created)
def create_on_internal_ldap(sender, group, **kwargs):
    """
    BackendGroup instances are used to represent external backends (e.g. LDAP) groups.

    If such a group is created, we should therefor create the group on the backend.
    """
    if group is not None and hasattr(group, 'backend_group'):
        internal_ldap = get_internal_ldap_connected()
        try:
            created = internal_ldap.create_group({
                'groupname': group.backend_group.backend_pk,
                'gidNumber': group.backend_group.backend_id
            })
            # FIXME: this is the first time we really know the ID/PK given by the backend.
            # all other operations having used to old ones might not be valid anymore...
            group.backend_group.backend_id = created.get(GroupBackend.FIELD_ID)
            group.backend_group.backend_pk = created.get(GroupBackend.FIELD_PK)
            group.backend_group.save()
        except GroupBackendError as ex:
            group.backend_group.delete()  # XXX: cleanup?
            raise ex
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(group_deleted)
def delete_on_internal_ldap(sender, group, **kwargs):
    """
    In case the BackendGroup record is deleted, we need to cleanup the internal LDAP server.
    """
    if group is not None and hasattr(group, 'backend_group'):
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.delete_group(group.backend_group.backend_pk)
            group.delete()
        except GroupNotFoundError:
            pass  # already deleted
        except GroupBackendError as ex:
            # XXX: recreate?
            raise ex
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(group_member_removed)
def remove_member_from_internal_ldap_group(sender, group, user, **kwargs):
    """
    When ever a member is removed to a group we need to sync the LDAP group.
    """
    if group is not None and user is not None and \
            hasattr(group, 'backend_group') and hasattr(user, 'backend_user'):
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.remove_group_member(group.backend_group.backend_pk, user.backend_user.backend_pk)
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(group_modified)
def group_modified_handler(sender, group, fields, **kwargs):
    """
    Helper method to break modifications into smaller pieces.
    """
    kwargs = kwargs.get('kwargs')  # not sure why this is needed
    if fields is not None and 'user_set' in fields:
        # get the user objects
        users = []
        if kwargs.get('pk_set') is not None:
            for user_pk in kwargs.get('pk_set'):
                users.append(User.objects.get(pk=user_pk))
        # trigger the signals
        action = kwargs.get('action')
        if action == 'post_add':
            for user in users:
                group_member_added.send(
                    sender=sender,
                    group=group,
                    user=user,
                    kwargs=kwargs
                )
        elif action == 'post_remove':
            for user in users:
                group_member_removed.send(
                    sender=sender,
                    group=group,
                    user=user,
                    kwargs=kwargs
                )


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    """
    Method to map Django m2m_changed model signals to custom ones.
    """
    if isinstance(instance, Group):
        action = kwargs.get('action')
        if action == 'post_add' or action == 'post_remove':
            group_modified.send(
                sender=sender,
                group=instance,
                fields=['user_set'],
                kwargs=kwargs
            )


@receiver(post_delete, sender=Group)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    group_deleted.send(sender=sender, group=instance, kwargs=kwargs)


@receiver(post_save, sender=Group)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(
            sender=sender,
            group=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
