from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from ipynbsrv.conf.helpers import *
from ipynbsrv.contract.errors import *
from ipynbsrv.core.models import BackendGroup
from ipynbsrv.core.signals.signals import group_created, group_deleted, group_modified
import logging


logger = logging.getLogger(__name__)


@receiver(group_deleted)
def delete_group_on_internal_ldap(sender, group, **kwargs):
    """
    In case the BackendGroup record is removed, we need to cleanup the internal LDAP server.
    """
    if group is not None:
        internal_ldap = get_internal_ldap_connected()
        try:
            internal_ldap.delete_group(group.backend_pk)
            group.django_group.delete()
        except GroupNotFoundError:
            pass  # already deleted
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
    group_deleted.send(sender=sender, group=instance, kwargs=kwargs)


@receiver(post_save, sender=BackendGroup)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs['created']:
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
