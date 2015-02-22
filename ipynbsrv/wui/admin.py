from django.contrib import admin
from ipynbsrv.wui.models import Container, Image, PortMapping, Share, Tag


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'running']
    list_filter = ['name', 'image', 'owner', 'running']
    search_fields = ['docker_id', 'name', 'description', 'running']


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public', 'is_clone']
    search_fields = ['docker_id', 'name', 'description', 'cmd']


class PortMappingAdmin(admin.ModelAdmin):
    list_display = ['container', 'internal', 'external']
    list_filter = ['container', 'internal']
    search_fields = ['internal', 'external']


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class TagAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


admin.site.register(Image, ImageAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(PortMapping, PortMappingAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
