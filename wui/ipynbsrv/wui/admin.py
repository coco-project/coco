from django.contrib import admin
from ipynbsrv.wui.models import Container, Host, Image, LdapGroup, LdapUser, Share, Tag


""
class ContainerAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    list_filter   = ('status',)
    search_fields = ('id','ct_id','name','description','status')


""
class HostAdmin(admin.ModelAdmin):
    list_display  = ('ip','fqdn')
    list_filter   = ('username','ssh_port')
    search_fields = ('ip','fqdn','username','ssh_port','ssh_pub_key','ssh_priv_key','docker_version','docker_port')


""
class ImageAdmin(admin.ModelAdmin):
    list_display  = ('name','host','owner')
    list_filter   = ('img_id','host','owner')
    search_fields = ('id','img_id','name','description','host','owner','tags')


class LdapGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'usernames']
    list_display = ['name', 'gid']
    search_fields = ['name']


class LdapUserAdmin(admin.ModelAdmin):
    exclude = ['dn', 'password']
    list_display = ['username', 'uid']
    search_fields = ['username']


""
class TagAdmin(admin.ModelAdmin):
    list_display  = ('label',)
    search_fields = ('label',)


admin.site.register(Container, ContainerAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(LdapGroup, LdapGroupAdmin)
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(Tag, TagAdmin)
