from django.contrib import admin
from ipynbsrv.wui.models import Container, Host, Image, Share, Tag


class ContainerAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description', 'image', 'owner', 'status']
    list_filter   = ['name', 'image', 'owner', 'status']
    search_fields = ['id', 'ct_id', 'name', 'description', 'status', 'exposeport']


class HostAdmin(admin.ModelAdmin):
    list_display  = ['ip', 'fqdn']
    list_filter   = ['username', 'ssh_port']
    search_fields = ['ip', 'fqdn', 'username', 'ssh_port', 'docker_version', 'docker_port']


class ImageAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description', 'owner', 'is_public']
    list_filter   = ['owner', 'is_public', 'is_clone']
    search_fields = ['id', 'img_id', 'name', 'description']


class ShareAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description', 'owner']
    list_filter   = ['owner', 'tags']
    search_fields = ['name', 'description', 'owner', 'group']


class TagAdmin(admin.ModelAdmin):
    list_display  = ['label']
    search_fields = ['label']


admin.site.register(Host, HostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Tag, TagAdmin)
