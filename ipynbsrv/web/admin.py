from django.contrib import admin
from ipynbsrv.core.models import Backend, Container, Image, Share, Tag, IpynbUser, IpynbGroup, Server
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


class BackendAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the Backend model.
    '''
    list_display = ['kind', 'module', 'klass', 'arguments']
    list_filter = ['kind', 'module', 'klass']
    search_fields = ['kind', 'module', 'klass', 'arguments']


class ContainerAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the Container model.
    '''
    list_display = ['name', 'description', 'owner', 'is_running']
    list_filter = ['name', 'image', 'owner']
    search_fields = ['docker_id', 'name', 'description']


class ImageAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the container Images model.
    '''
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public']
    search_fields = ['docker_id', 'name', 'description', 'cmd']


class ServerAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the Server model.
    '''
    list_display = ['name', 'hostname', 'internal_ip']
    list_filter = ['container_backend']
    search_fields = ['name', 'hostname', 'internal_ip', 'external_ip', 'container_backend']


class ShareAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the Share model.
    '''
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class TagAdmin(admin.ModelAdmin):
    '''
    Django admin definition for the Tag model.
    '''
    list_display = ['label']
    search_fields = ['label']


class IpynbUserInline(admin.StackedInline):
    model = IpynbUser
    can_delete = False
    verbose_name_plural = 'Ipynb Frontend User'


class UserAdmin(UserAdmin):
    inlines = (IpynbUserInline, )


class IpynbGroupInline(admin.StackedInline):
    model = IpynbGroup
    can_delete = False
    verbose_name_plural = 'Ipynb Frontend User'


class GroupAdmin(GroupAdmin):
    inlines = (IpynbGroupInline, )


admin.site.register(Backend, BackendAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
