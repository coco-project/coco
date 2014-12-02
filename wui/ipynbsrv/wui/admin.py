from django.contrib import admin
from ipynbsrv.wui.models import User, Group, Tag, Host, Image, Container, Share


class HostAdmin(admin.ModelAdmin):
    list_display  = ('ip','fqdn')
    list_filter   = ('username','ssh_port')
    search_fields = ('ip','fqdn','username','ssh_port','ssh_pub_key','ssh_priv_key','docker_version','docker_port')


class GroupAdmin(admin.ModelAdmin):
    list_display  = ('gid','groupname')
    search_fields = ('gid','groupname')


class UserAdmin(admin.ModelAdmin):
    list_display  = ('uid','username')
    search_fields = ('uid','username')


class TagAdmin(admin.ModelAdmin):
    list_display  = ('label',)
    search_fields = ('label',)


class ShareAdmin(admin.ModelAdmin):
    list_display  = ('name','owner')
    list_filter   = ('owner','group')
    search_fields = ('name','description','owner','group','tags')


class ImageAdmin(admin.ModelAdmin):
    list_display  = ('name','host','owner')
    list_filter   = ('img_id','host','owner')
    search_fields = ('id','img_id','name','description','host','owner','tags')


class ContainerAdmin(admin.ModelAdmin):
    list_display  = ('name','host','owner')
    list_filter   = ('status','host','image','owner')
    search_fields = ('id','ct_id','name','description','status','host','image','owner','tags')


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(Share, ShareAdmin)
