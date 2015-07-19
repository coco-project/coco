from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from ipynbsrv.core.models import *


class BackendAdmin(admin.ModelAdmin):
    list_display = ['module', 'klass', 'arguments']
    list_filter = ['kind']
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


class GroupAdmin(GroupAdmin):
    inlines = (BackendGroupInline, )


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public']
    search_fields = ['docker_id', 'name', 'description', 'cmd']


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


class UserAdmin(UserAdmin):
    inlines = (BackendUserInline, )


admin.site.register(Backend, BackendAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(ContainerImage, ContainerImageAdmin)
admin.site.register(ContainerSnapshot, ContainerSnapshotAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
