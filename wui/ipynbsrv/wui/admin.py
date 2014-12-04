from django.contrib import admin
from ipynbsrv.wui.models import Container, Host, Image, Share, Tag


"""
"""
class ContainerAdmin(admin.ModelAdmin):
    list_display  = ['name']
    list_filter   = ['status']
    search_fields = ['id', 'ct_id', 'name', 'description', 'status']


"""
"""
class HostAdmin(admin.ModelAdmin):
    list_display  = ['ip', 'fqdn']
    list_filter   = ['username', 'ssh_port']
    search_fields = ['ip', 'fqdn', 'username', 'ssh_port', 'docker_version', 'docker_port']


"""
"""
class ImageAdmin(admin.ModelAdmin):
    list_display  = ['name']
    list_filter   = ['img_id']
    search_fields = ['id', 'img_id', 'name', 'description']


"""
"""
class TagAdmin(admin.ModelAdmin):
    list_display  = ['label']
    search_fields = ['label']


"""
"""
class ShareAdmin(admin.ModelAdmin):
    list_display  = ['name', 'owner']
    list_filter   = ['owner', 'group']
    search_fields = ['name', 'description', 'owner', 'group', 'tags']


admin.site.register(Host, HostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Tag, TagAdmin)
