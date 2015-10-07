from coco.contract.backends import GroupBackend
from coco.contract.errors import GroupBackendError, GroupNotFoundError
from coco.core.helpers import get_internal_ldap_connected
from coco.core.models import BackendGroup
from coco.core.signals.signals import backend_group_created, \
    backend_group_deleted, backend_group_member_added, \
    backend_group_member_removed, backend_group_modified
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save


@receiver(backend_group_member_added)
def add_member_to_internal_ldap_group(sender, group, user, **kwargs):
    """
    Whenever a member is added to a group we need to sync the LDAP group.
    """
    if group is not None and user is not None:
        try:
            internal_ldap = get_internal_ldap_connected()
            internal_ldap.add_group_member(group.backend_pk, user.backend_pk)
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(backend_group_member_removed)
def remove_member_from_internal_ldap_group(sender, group, user, **kwargs):
    """
    Whenever a member is removed from a group we need to sync the LDAP group.
    """
    if group is not None and user is not None:
        try:
            internal_ldap = get_internal_ldap_connected()
            internal_ldap.remove_group_member(group.backend_pk, user.backend_pk)
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(backend_group_created)
def create_on_internal_ldap(sender, group, **kwargs):
    """
    BackendGroup instances are used to represent external backends (e.g. LDAP) groups.

    If such a group is created, we should therefor create the group on the backend.
    """
    if group is not None:
        try:
            internal_ldap = get_internal_ldap_connected()
            created = internal_ldap.create_group(group.backend_id, group.backend_pk)
            # FIXME: this is the first time we really know the ID/PK given by the backend.
            # all other operations having used to old ones might not be valid anymore...
            group.backend_id = created.get(GroupBackend.FIELD_ID)
            group.backend_pk = created.get(GroupBackend.FIELD_PK)
            group.save()
        except GroupBackendError as ex:
            group.delete()  # XXX: cleanup?
            raise ex
        finally:
            try:
                internal_ldap.disconnect()
            except:
                pass


@receiver(backend_group_deleted)
def delete_django_group(sender, group, **kwargs):
    """
    Delete the internal Django group on delete.
    """
    if group is not None:
        try:
            group.django_group.delete()
        except:
            pass  # already deleted?


@receiver(backend_group_deleted)
def delete_on_internal_ldap(sender, group, **kwargs):
    """
    In case the BackendGroup record is deleted, we need to cleanup the internal LDAP server.
    """
    if group is not None:
        try:
            internal_ldap = get_internal_ldap_connected()
            internal_ldap.delete_group(group.backend_pk)
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


@receiver(post_delete, sender=BackendGroup)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    backend_group_deleted.send(sender=sender, group=instance, kwargs=kwargs)


@receiver(post_save, sender=BackendGroup)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        backend_group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        backend_group_modified.send(
            sender=sender,
            group=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
