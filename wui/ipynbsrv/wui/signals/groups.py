from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup
from ipynbsrv.wui.signals.signals import *


""
@receiver(group_created)
def created_handler(sender, group, **kwargs):
    next_guid = LdapGroup.objects.all().latest('gid').gid + 1
    ldap_group = LdapGroup(gid=next_guid, name=group.name, members="")
    ldap_group.save()


""
@receiver(group_deleted)
def deleted_handler(sender, group, **kwargs):
    group = LdapGroup.objects.filter(name=group.name)
    if group:
        group[0].delete()


#
# Bridges
#
@receiver(post_delete, sender=Group)
def post_delete(sender, instance, using, **kwargs):
    group_deleted.send(sender, group=instance)


@receiver(post_save, sender=Group)
def post_save(sender, instance, using, **kwargs):
    group_created.send(sender, group=instance)
