from django.contrib import admin
from ipynbsrv.wui.models import Container, Image, PortMapping, Share, Tag


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'running']
    list_filter = ['name', 'image', 'owner', 'running']
    search_fields = ['docker_id', 'name', 'description', 'running']

    def get_readonly_fields(self, request, obj=None, **kwargs):
        if obj is not None:  # only interested in updates
            return Container.get_unsynchonized_fields()
        else:
            return ()


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public', 'is_clone']
    search_fields = ['docker_id', 'name', 'description', 'cmd']

    def get_readonly_fields(self, request, obj=None, **kwargs):
        if obj is not None:  # only interested in updates
            return Image.get_unsynchonized_fields()
        else:
            return ()


class PortMappingAdmin(admin.ModelAdmin):
    list_display = ['container', 'internal', 'external']
    list_filter = ['container', 'internal']
    search_fields = ['internal', 'external']

    def get_readonly_fields(self, request, obj=None, **kwargs):
        if obj is not None:  # only interested in updates
            return PortMapping.get_unsynchonized_fields()
        else:
            return ()


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']

    def get_readonly_fields(self, request, obj=None, **kwargs):
        if obj is not None:  # only interested in updates
            return Share.get_unsynchonized_fields()
        else:
            return ()


class TagAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


admin.site.register(Container, ContainerAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(PortMapping, PortMappingAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
