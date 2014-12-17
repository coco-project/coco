from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, LdapUser, Share
from ipynbsrv.wui.signals.signals import group_created, group_deleted, group_modified, share_deleted


"""
"""
@receiver(group_created)
def created_handler(sender, group, **kwargs):
    if settings.DEBUG:
        print "Created LDAP group via signal"
    next_gid = LdapGroup.objects.all().latest('gid').gid + 1
    if next_gid < settings.SHARE_GROUPS_OFFSET:
        next_gid = settings.SHARE_GROUPS_OFFSET + 1
    ldap_group = LdapGroup(gid=next_gid, name=group.name, members="")
    ldap_group.save()


"""
"""
@receiver(group_deleted)
def deleted_handler(sender, group, **kwargs):
    ldap_group = LdapGroup.objects.filter(pk=group.name).first()
    if ldap_group:
        if settings.DEBUG:
            print "Deleted LDAP group via signal"
        ldap_group.delete()
        # make sure to also delete the share for this group
        share = Share.objects.filter(group=group).first()
        if share:
            share.delete()
            share_deleted.send(None, share=share) # Django should do that


"""
Note: Supports only updating the group members
"""
@receiver(group_modified)
def modified_handler(sender, group, fields, **kwargs):
    if settings.DEBUG:
        print "Modified LDAP group via signal"
    ldap_group = LdapGroup.objects.get(pk=group.name)
    # update the group memberships
    members = []
    for member in group.user_set.all():
        members.append(member.username)
    if members:
        ldap_group.members = members
        ldap_group.save()


#
# Bridges
#
"""
"""
@receiver(post_delete, sender=Group, dispatch_uid='ipynbsrv.wui.signals.groups.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    group_deleted.send(sender=sender, group=instance)


"""
"""
@receiver(post_save, sender=Group, dispatch_uid='ipynbsrv.wui.signals.groups.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        group_created.send(sender, group=instance)
    else:
        group_modified.send(sender, group=instance, fields=kwargs['update_fields'])
