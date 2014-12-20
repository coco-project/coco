from django.dispatch import Signal


"""
Set of signals to be triggered when working with groups.

We use these signals to decouple internal Django groups from our LDAP server groups.
It allows us to work with the regular Group model across the whole app, while we
can synchronize the actions/modifications with the LDAP server in the handlers.
"""
group_created  = Signal(providing_args=['group'])
group_deleted  = Signal(providing_args=['group'])
group_modified = Signal(providing_args=['group', 'fields'])


"""
Set of signals to be triggered when working with users.

We use these signals to decouple internal Django users from our LDAP server users.
It allows us to work with the regular User model across the whole app, while we
can synchronize the actions/modifications with the LDAP server in the handlers.
"""
user_created  = Signal(providing_args=['user'])
user_deleted  = Signal(providing_args=['user'])
user_modified = Signal(providing_args=['user', 'fields'])


# ""
container_created  = Signal(providing_args=['container'])
container_deleted  = Signal(providing_args=['container'])
container_started  = Signal(providing_args=['container'])
container_stopped  = Signal(providing_args=['container'])
container_restarted= Signal(providing_args=['container'])
container_commited = Signal(providing_args=['container'])


# ""
image_created  = Signal(providing_args=['image'])
image_deleted  = Signal(providing_args=['image'])
image_edited   = Signal(providing_args=['image'])
image_shared   = Signal(providing_args=['image', 'with_user'])


"""
Set of signals to be triggered when working with shares.

These are meant to be listened to by handlers that work directly on the filesystem,
e.g. to create the share directory.
"""
share_created  = Signal(providing_args=['share'])
share_deleted  = Signal(providing_args=['share'])
share_modified = Signal(providing_args=['share', 'fields'])

share_user_added   = Signal(providing_args=['share', 'user'])
share_user_leaved  = Signal(providing_args=['share', 'user'])
share_user_removed = Signal(providing_args=['share', 'user'])
