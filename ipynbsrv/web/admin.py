from django.contrib import admin
from ipynbsrv.core.models import *


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


admin.site.register(Backend, BackendAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
