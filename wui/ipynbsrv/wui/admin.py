from django.contrib import admin
from ipynbsrv.wui.models import User, Group, Tag, Host, Image, Container, Share


admin.site.register(User)
admin.site.register(Group)
admin.site.register(Tag)
admin.site.register(Host)
admin.site.register(Image)
admin.site.register(Container)
admin.site.register(Share)
