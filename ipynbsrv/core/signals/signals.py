from django.dispatch import Signal


"""
Set of signals to be triggered when working with backend containers.

We use these signals to decouple internal Django users from our container installation.
It allows us to threat containers as regular Django objects across the whole app,
while we can synchronize actions with the container backend in the handlers.
"""
container_created = Signal(providing_args=['container'])
container_deleted = Signal(providing_args=['container'])
container_modified = Signal(providing_args=['container', 'fields'])
container_restarted = Signal(providing_args=['container'])
container_started = Signal(providing_args=['container'])
container_stopped = Signal(providing_args=['container'])
# CloneableContainerBackend
container_cloned = Signal(providing_args=['container', 'clone'])
# SuspendableContainerBackend
container_resumed = Signal(providing_args=['container'])
container_suspended = Signal(providing_args=['container'])


"""
Set of signals to be triggered when working with container_backend images.
"""
container_image_created = Signal(providing_args=['image'])
container_image_deleted = Signal(providing_args=['image'])
container_image_modified = Signal(providing_args=['image'])


"""
Set of signals to be triggered when working with container_backend container instance snapshots.
"""
container_snapshot_created = Signal(providing_args=['snapshot'])
container_snapshot_deleted = Signal(providing_args=['snapshot'])
container_snapshot_modified = Signal(providing_args=['snapshot', 'fields'])
container_snapshot_restored = Signal(providing_args=['snapshot'])


"""
Set of signals to be triggered when working with groups.

We use these signals to decouple internal Django groups from our backend server groups.
It allows us to work with the regular Group model across the whole app, while we
can synchronize the actions/modifications with the backend in the handlers.
"""
group_created = Signal(providing_args=['group'])
group_deleted = Signal(providing_args=['group'])
group_member_added = Signal(providing_args=['group', 'user'])
group_member_removed = Signal(providing_args=['group', 'user'])
group_modified = Signal(providing_args=['group', 'fields'])


"""
Set of signals to be triggered when working with shares.

These are meant to be listened to by handlers that work directly on the filesystem,
e.g. to create the share directory.
"""
share_created = Signal(providing_args=['share'])
share_deleted = Signal(providing_args=['share'])
# share_member_added = Signal(providing_args=['share', 'member'])
# share_member_leaved = Signal(providing_args=['share', 'member'])
# share_member_removed = Signal(providing_args=['share', 'member'])
share_modified = Signal(providing_args=['share', 'fields'])


"""
Set of signals to be triggered when working with users.

We use these signals to decouple internal Django users from our backend server users.
It allows us to work with the regular User model across the whole app, while we
can synchronize the actions/modifications with the backend in the handlers.
"""
user_created = Signal(providing_args=['user'])
user_deleted = Signal(providing_args=['user'])
user_modified = Signal(providing_args=['user', 'fields'])
