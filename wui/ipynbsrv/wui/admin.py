from django.contrib import admin
from ipynbsrv.wui.models import Container, Image, Share, Tag


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'image', 'owner', 'running']
    list_filter = ['name', 'image', 'owner', 'running']
    search_fields = ['id', 'name', 'description', 'running']


class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner', 'is_public']
    list_filter = ['owner', 'is_public', 'is_clone']
    search_fields = ['id', 'name', 'description', 'cmd']


class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'owner']
    list_filter = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class TagAdmin(admin.ModelAdmin):
    list_display = ['label']
    search_fields = ['label']


admin.site.register(Image, ImageAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
