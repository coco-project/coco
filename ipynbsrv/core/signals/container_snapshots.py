from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.contract.backends import ContainerBackend
from ipynbsrv.contract.errors import ContainerBackendError, ContainerSnapshotNotFoundError
from ipynbsrv.core.models import ContainerSnapshot
from ipynbsrv.core.signals.signals import container_snapshot_created, \
    container_snapshot_deleted, container_snapshot_modified, container_snapshot_restored


@receiver(container_snapshot_created)
def create_on_server(sender, snapshot, **kwargs):
    """
    When a snapshot is created, we should do that on the server as well.
    """
    if snapshot is not None:
        backend = snapshot.container.server.get_container_backend()
        try:
            created = backend.create_container_snapshot(
                snapshot.container.backend_pk,
                snapshot.name
            )
            snapshot.backend_pk = created.get(ContainerBackend.KEY_PK)
            snapshot.save()
        except ContainerBackendError as ex:
            snapshot.delete()  # XXX: cleanup?
            raise ex


@receiver(container_snapshot_deleted)
def delete_on_server(sender, snapshot, **kwargs):
    """
    When a snapshot is removed from the database, we can remove it from the servers as well.
    """
    if snapshot is not None:
        backend = snapshot.container.server.get_container_backend()
        try:
            backend.delete_container_snapshot(snapshot.backend_pk)
        except ContainerSnapshotNotFoundError as ex:
            pass  # already removed?
        except ContainerBackendError as ex:
            # XXX: restore?
            raise ex


@receiver(container_snapshot_restored)
def restore_on_server(sender, snapshot, **kwargs):
    """
    Restore the restored snapshot on the container backend.
    """
    if snapshot is not None:
        backend = snapshot.container.server.get_container_backend()
        try:
            backend.restore_container_snapshot(snapshot.container.backend_pk, snapshot.backend_pk)
        except ContainerBackendError as ex:
            # XXX: restore?
            raise ex


@receiver(post_delete, sender=ContainerSnapshot)
def post_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    container_snapshot_deleted.send(sender=sender, snapshot=instance, kwargs=kwargs)


@receiver(post_save, sender=ContainerSnapshot)
def post_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        container_snapshot_created.send(sender=sender, snapshot=instance, kwargs=kwargs)
    else:
        container_snapshot_modified.send(
            sender=sender,
            snapshot=instance,
            fields=kwargs.get('update_fields'),
            kwargs=kwargs
        )
