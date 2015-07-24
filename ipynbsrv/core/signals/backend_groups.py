from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf.helpers import get_internal_ldap_connected
from ipynbsrv.contract.backends import GroupBackend
from ipynbsrv.contract.errors import GroupBackendError, GroupNotFoundError
from ipynbsrv.core.models import BackendGroup
from ipynbsrv.core.signals.signals import backend_group_created, \
    backend_group_deleted, backend_group_modified


@receiver(backend_group_created)
def create_on_internal_ldap(sender, group, **kwargs):
    """
    BackendGroup instances are used to represent external backends (e.g. LDAP) groups.

    If such a group is created, we should therefor create the group on the backend.
    """
    if group is not None:
        internal_ldap = get_internal_ldap_connected()
        try:
            created = internal_ldap.create_group({
                'groupname': group.backend_pk,
                'gidNumber': group.backend_id
            })
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
def delete_on_internal_ldap(sender, group, **kwargs):
    """
    In case the BackendGroup record is deleted, we need to cleanup the internal LDAP server.
    """
    if group is not None:
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.delete_group(group.backend_pk)
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
