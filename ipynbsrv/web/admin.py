from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from ipynbsrv.core.models import *


class BackendAdmin(admin.ModelAdmin):
    list_display = ['kind', 'module', 'klass', 'arguments']
    list_filter = ['kind', 'module', 'klass']
    search_fields = ['kind', 'module', 'klass', 'arguments']


class BackendGroupInline(admin.StackedInline):
    model = BackendGroup
    can_delete = False
    verbose_name_plural = "GroupBackend group"


class BackendUserInline(admin.StackedInline):
    model = BackendUser
    can_delete = False
    verbose_name_plural = "UserBackend user"


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_running']
    list_filter = ['name', 'image', 'owner']
    search_fields = ['docker_id', 'name', 'description']


class GroupAdmin(GroupAdmin):
    inlines = (BackendGroupInline, )


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public']
    search_fields = ['docker_id', 'name', 'description', 'cmd']


class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostname', 'internal_ip']
    list_filter = ['container_backend']
    search_fields = ['name', 'hostname', 'internal_ip', 'external_ip', 'container_backend']


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class NotificationReceiversInline(admin.StackedInline):
    model = NotificationReceivers


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['date', 'sender', 'message']
    list_filter = ['date', 'sender']
    search_fields = ['sender', 'message']
    inlines = (NotificationReceiversInline, )


class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'user', 'read']


class TagAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


class UserAdmin(UserAdmin):
    inlines = (BackendUserInline, )


admin.site.register(NotificationLog, NotificationLogAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Backend, BackendAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
