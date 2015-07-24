from django.contrib import admin
from ipynbsrv.core.models import *


class BackendAdmin(admin.ModelAdmin):
    list_display = ['module', 'klass', 'arguments']
    list_filter = ['kind']
    search_fields = ['kind', 'module', 'klass', 'arguments']


class BackendGroupAdmin(admin.ModelAdmin):
    list_display = ['django_group', 'backend_id', 'backend_pk']
    list_filter = []
    search_fields = ['backend_id', 'backend_pk']


class BackendUserAdmin(admin.ModelAdmin):
    list_display = ['django_user', 'backend_id', 'backend_pk']
    list_filter = []
    search_fields = ['backend_id', 'backend_pk']


class CollaborationGroupAdmin(admin.ModelAdmin):
    list_display = ['django_group', 'creator']
    list_filter = ['creator']


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['image', 'owner', 'server']
    search_fields = ['backend_pk', 'name', 'description']


class ContainerImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['owner', 'is_public']
    search_fields = ['backend_pk', 'name', 'description']


class ContainerSnapshotAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['container']
    search_fields = ['backend_pk', 'name', 'description']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'sender', 'date']
    list_filter = ['sender', 'date']
    search_fields = ['sender', 'message']


class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'user', 'read']
    list_filter = ['notification', 'user']


class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostname', 'internal_ip', 'external_ip']
    list_filter = ['container_backend']
    search_fields = ['name', 'hostname', 'internal_ip', 'external_ip', 'container_backend', 'container_backend_args']


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class TagAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


admin.site.register(Backend, BackendAdmin)
admin.site.register(BackendGroup, BackendGroupAdmin)
admin.site.register(BackendUser, BackendUserAdmin)
admin.site.register(CollaborationGroup, CollaborationGroupAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(ContainerImage, ContainerImageAdmin)
admin.site.register(ContainerSnapshot, ContainerSnapshotAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationLog, NotificationLogAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
