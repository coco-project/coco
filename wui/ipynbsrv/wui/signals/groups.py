from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import DoesNotExist
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, LdapUser, Share
from ipynbsrv.wui.signals.signals import group_created, group_deleted, group_member_added, \
    group_member_removed, group_modified, share_deleted


"""
Signal receiver that creates an LDAP group when ever a regular Django
group is created.

This is important for us so share groups are created.
"""
@receiver(group_created)
def created_handler(sender, group, **kwargs):
    if settings.DEBUG:
        print "group_created handler fired"
    next_id = LdapGroup.objects.all().latest('id').id + 1
    if next_id < settings.SHARE_GROUPS_OFFSET:
        next_id = settings.SHARE_GROUPS_OFFSET + 1
    ldap_group = LdapGroup(id=next_id, name=group.name, members="")
    ldap_group.save()


"""
Signal receiver to delete (share) groups from the LDAP server when
they are deleted from Django.
"""
@receiver(group_deleted)
def deleted_handler(sender, group, **kwargs):
    if settings.DEBUG:
        print "group_deleted handler fired"
    try:
        ldap_group = LdapGroup.objects.get(pk=group.name)
        ldap_group.delete()
        # make sure to also delete the share for this group
        share = Share.objects.get(group=group)
        share.delete()
        share_deleted.send(None, share=share)  # Django should do that for us
    except DoesNotExist:
        pass


"""
Method triggered by group_member_added signals.

We use that chance to add LDAP users to the LDAP group
if both exist.
"""
@receiver(group_member_added)
def member_added_handler(sender, group, member, **kwargs):
    if settings.DEBUG:
        print "group_member_added handler fired"
    try:
        ldap_group = LdapGroup.objects.get(pk=group.name)
        ldap_user = LdapUser.objects.get(pk=member.username)
        ldap_group.members.add(member.username)
        ldap_group.save()
    except DoesNotExist:
        pass


"""
Method triggered by group_member_removed signals.
"""
@receiver(group_member_removed)
def member_removed_handler(sender, group, member, **kwargs):
    if settings.DEBUG:
        print "group_member_removed handler fired"
    try:
        ldap_group = LdapGroup.objects.get(pk=group.name)
        ldap_user = LdapUser.objects.get(pk=member.username)
        ldap_group.members.remove(member.username)
        ldap_group.save()
    except DoesNotExist:
        pass


"""
Method triggered by group_modified signals.
"""
@receiver(group_modified)
def modified_handler(sender, group, fields, **kwargs):
    if settings.DEBUG:
        print "group_modified handler fired"


"""
Internal receivers to map the Django built-in signals to custom ones.
"""
@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    user = User.objects.get(pk=pk_set.pop())
    action = kwargs['action']
    if action == 'post_save':
        group_member_added.send(sender=sender, group=instance, member=user, kwargs=kwargs)
    elif action == 'post_delete':
        group_member_removed.send(sender=sender, group=instance, member=user, kwargs=kwargs)

@receiver(post_delete, sender=Group)
def post_delete_handler(sender, instance, **kwargs):
    group_deleted.send(sender=sender, group=instance, kwargs=kwargs)

@receiver(post_save, sender=Group)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
