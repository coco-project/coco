from django.contrib import admin
from ipynbsrv.wui.models import User, Group, Tag, Host, Image, Container, Share

class HostAdmin(admin.ModelAdmin):
    list_display = ('ip','fqdn')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('gid','groupname')

class UserAdmin(admin.ModelAdmin):
    list_display = ('uid','username')

class TagAdmin(admin.ModelAdmin):
    list_display = ('label',)

class ShareAdmin(admin.ModelAdmin):
    list_display = ('name','owner')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('name','host','owner')

class ContainerAdmin(admin.ModelAdmin):
    list_display = ('name','host','owner')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Share, ShareAdmin)
