from django.dispatch import Signal


""
group_created = Signal(providing_args=['group'])
group_deleted = Signal(providing_args=['group'])


# ""
container_backuped = Signal(providing_args=['container'])
container_cloned   = Signal(providing_args=['container', 'clone'])
container_created  = Signal(providing_args=['container'])
container_deleted  = Signal(providing_args=['container'])
container_edited   = Signal(providing_args=['container'])
container_restored = Signal(providing_args=['container', 'backup'])
container_shared   = Signal(providing_args=['container', 'with_user'])
container_started  = Signal(providing_args=['container'])
container_stopped  = Signal(providing_args=['container'])


# ""
image_created  = Signal(providing_args=['image'])
image_deleted  = Signal(providing_args=['image'])
image_edited   = Signal(providing_args=['image'])
image_shared   = Signal(providing_args=['image', 'with_user'])


""
# share_accepted   = Signal(providing_args=['share', 'user'])
share_created    = Signal(providing_args=['share'])
# share_declined   = Signal(providing_args=['share', 'user'])
share_deleted    = Signal(providing_args=['share'])
# share_invited    = Signal(providing_args=['share', 'user'])
# share_leaved     = Signal(providing_args=['share', 'user'])
share_user_added = Signal(providing_args=['share', 'user'])
share_user_removed = Signal(providing_args=['share', 'user'])
