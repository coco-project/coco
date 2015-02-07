from django.dispatch import Signal


"""
Set of signals to be triggered when working with Docker containers.

We use these signals to decouple internal Django users from our Docker installation.
It allows us to threat containers as regular Django objects across the whole app,
while we can synchronize actions with the Docker installation in the handlers.
"""
container_cloned = Signal(providing_args=['container', 'clone', 'action'])
post_container_cloned = Signal(providing_args=['container', 'clone'])
pre_container_cloned = Signal(providing_args=['container'])
container_commited = Signal(providing_args=['container', 'image', 'action'])
post_container_commited = Signal(providing_args=['container', 'image'])
pre_container_commited = Signal(providing_args=['container'])
container_created = Signal(providing_args=['container', 'action'])
post_container_created = Signal(providing_args=['container'])
pre_container_created = Signal(providing_args=['container'])
container_deleted = Signal(providing_args=['container', 'action'])
post_container_deleted = Signal(providing_args=['container'])
pre_container_deleted = Signal(providing_args=['container'])
container_modified = Signal(providing_args=['container', 'fields', 'action'])
post_container_modified = Signal(providing_args=['container', 'fields'])
pre_container_modified = Signal(providing_args=['container', 'fields'])
container_restarted = Signal(providing_args=['container', 'action'])
post_container_restarted = Signal(providing_args=['container'])
pre_container_restarted = Signal(providing_args=['container'])
container_started = Signal(providing_args=['container', 'action'])
post_container_started = Signal(providing_args=['container'])
pre_container_started = Signal(providing_args=['container'])
container_stopped = Signal(providing_args=['container', 'action'])
post_container_stopped = Signal(providing_args=['container'])
pre_container_stopped = Signal(providing_args=['container'])


"""
Set of signals to be triggered when working with groups.

We use these signals to decouple internal Django groups from our LDAP server groups.
It allows us to work with the regular Group model across the whole app, while we
can synchronize the actions/modifications with the LDAP server in the handlers.
"""
group_created = Signal(providing_args=['group', 'action'])
post_group_created = Signal(providing_args=['group'])
pre_group_created = Signal(providing_args=['group'])
group_deleted = Signal(providing_args=['group', 'action'])
post_group_deleted = Signal(providing_args=['group'])
pre_group_deleted = Signal(providing_args=['group'])
group_member_added = Signal(providing_args=['group', 'member', 'action'])
post_group_member_added = Signal(providing_args=['group', 'member'])
pre_group_member_added = Signal(providing_args=['group', 'member'])
group_member_removed = Signal(providing_args=['group', 'member', 'action'])
post_group_member_removed = Signal(providing_args=['group', 'member'])
pre_group_member_removed = Signal(providing_args=['group', 'member'])
group_modified = Signal(providing_args=['group', 'fields', 'action'])
post_group_modified = Signal(providing_args=['group', 'fields'])
pre_group_modified = Signal(providing_args=['group', 'fields'])


"""
Set of signals to be triggered when working with Docker images.
"""
image_created = Signal(providing_args=['image', 'action'])
post_image_created = Signal(providing_args=['image'])
pre_image_created = Signal(providing_args=['image'])
image_deleted = Signal(providing_args=['image', 'action'])
post_image_deleted = Signal(providing_args=['image'])
pre_image_deleted = Signal(providing_args=['image'])
image_modified = Signal(providing_args=['image', 'fields', 'action'])
post_image_modified = Signal(providing_args=['image', 'fields'])
pre_image_modified = Signal(providing_args=['image', 'fields'])


"""
Set of signals to be triggered when working with shares.

These are meant to be listened to by handlers that work directly on the filesystem,
e.g. to create the share directory.
"""
share_created = Signal(providing_args=['share', 'action'])
post_share_created = Signal(providing_args=['share'])
pre_share_created = Signal(providing_args=['share'])
share_deleted = Signal(providing_args=['share', 'action'])
post_share_deleted = Signal(providing_args=['share'])
pre_share_deleted = Signal(providing_args=['share'])
# share_member_added = Signal(providing_args=['share', 'member', 'action'])
# post_share_member_added = Signal(providing_args=['share', 'member'])
# pre_share_member_added = Signal(providing_args=['share', 'member'])
# share_member_leaved = Signal(providing_args=['share', 'member', 'action'])
# post_share_member_leaved = Signal(providing_args=['share', 'member'])
# pre_share_member_leaved = Signal(providing_args=['share', 'member'])
# share_member_removed = Signal(providing_args=['share', 'member', 'action'])
# post_share_member_removed = Signal(providing_args=['share', 'member'])
# pre_share_member_removed = Signal(providing_args=['share', 'member'])
share_modified = Signal(providing_args=['share', 'fields', 'action'])
post_share_modified = Signal(providing_args=['share', 'fields'])
pre_share_modified = Signal(providing_args=['share', 'fields'])


"""
Set of signals to be triggered when working with users.

We use these signals to decouple internal Django users from our LDAP server users.
It allows us to work with the regular User model across the whole app, while we
can synchronize the actions/modifications with the LDAP server in the handlers.
"""
user_created = Signal(providing_args=['user', 'action'])
post_user_created = Signal(providing_args=['user'])
pre_user_created = Signal(providing_args=['user'])
user_deleted = Signal(providing_args=['user', 'action'])
post_user_deleted = Signal(providing_args=['user'])
pre_user_deleted = Signal(providing_args=['user'])
user_modified = Signal(providing_args=['user', 'fields', 'action'])
post_user_modified = Signal(providing_args=['user', 'fields'])
pre_user_modified = Signal(providing_args=['user', 'fields'])
