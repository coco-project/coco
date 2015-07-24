from django.dispatch import Signal


"""
Set of signals to be triggered for `BackendUser` model events.
"""
backend_user_created = Signal(providing_args=['user'])
backend_user_deleted = Signal(providing_args=['user'])
backend_user_modified = Signal(providing_args=['user', 'fields'])


"""
Set of signals to be triggered for `BackendGroup` model events.
"""
backend_group_created = Signal(providing_args=['group'])
backend_group_deleted = Signal(providing_args=['group'])
backend_group_modified = Signal(providing_args=['group', 'fields'])


"""
Set of signals to be triggered for `Container` model events.
"""
container_cloned = Signal(providing_args=['container', 'clone'])
container_created = Signal(providing_args=['container'])
container_deleted = Signal(providing_args=['container'])
container_modified = Signal(providing_args=['container', 'fields'])
container_restarted = Signal(providing_args=['container'])
container_started = Signal(providing_args=['container'])
container_stopped = Signal(providing_args=['container'])
# SuspendableContainerBackend
container_resumed = Signal(providing_args=['container'])
container_suspended = Signal(providing_args=['container'])


"""
Set of signals to be triggered for `ContainerImage` model events.
"""
container_image_created = Signal(providing_args=['image'])
container_image_deleted = Signal(providing_args=['image'])
container_image_modified = Signal(providing_args=['image'])


"""
Set of signals to be triggered for `ContainerSnapshot` model events.
"""
container_snapshot_created = Signal(providing_args=['snapshot'])
container_snapshot_deleted = Signal(providing_args=['snapshot'])
container_snapshot_modified = Signal(providing_args=['snapshot', 'fields'])
container_snapshot_restored = Signal(providing_args=['snapshot'])


"""
Set of signals to be triggered for `Group` model events.
"""
group_created = Signal(providing_args=['group'])
group_deleted = Signal(providing_args=['group'])
group_member_added = Signal(providing_args=['group', 'user'])
group_member_removed = Signal(providing_args=['group', 'user'])
group_modified = Signal(providing_args=['group', 'fields'])


"""
Set of signals to be triggered for `GroupShare` model events.
"""
group_share_created = Signal(providing_args=['group', 'share'])
group_share_deleted = Signal(providing_args=['group', 'share'])


"""
Set of signals to be triggered for `Share` model events.
"""
share_created = Signal(providing_args=['share'])
share_deleted = Signal(providing_args=['share'])
share_modified = Signal(providing_args=['share', 'fields'])


"""
Set of signals to be triggered for `User` model events.
"""
user_created = Signal(providing_args=['user'])
user_deleted = Signal(providing_args=['user'])
user_modified = Signal(providing_args=['user', 'fields'])
