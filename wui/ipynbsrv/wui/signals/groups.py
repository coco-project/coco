from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, LdapUser, Share
from ipynbsrv.wui.signals.signals import group_created, group_deleted, group_member_added, \
    group_member_removed, group_modified, share_deleted, user_modified


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
    ldap_group = LdapGroup.objects.filter(pk=group.name)
    if ldap_group.exists():
        ldap_group.first().delete()
        # make sure to also delete the share for this group
        share = Share.objects.filter(group=group)
        if share.exists():
            share.first().delete()
            share_deleted.send(sender=None, share=share)  # Django should do that for us


"""
Method triggered by group_member_added signals.

We use that chance to add LDAP users to the LDAP group
if both exist.
"""
@receiver(group_member_added)
def member_added_handler(sender, group, member, **kwargs):
    if settings.DEBUG:
        print "group_member_added handler fired"
    ldap_group = LdapGroup.objects.get(pk=group.name)
    members = []
    for member in group.user_set.all():
        members.append(member.get_username())
    ldap_group.members = members
    ldap_group.save()


"""
Method triggered by group_member_removed signals.
"""
@receiver(group_member_removed)
def member_removed_handler(sender, group, member, **kwargs):
    if settings.DEBUG:
        print "group_member_removed handler fired"
    member_added_handler(sender=sender, group=group, member=member, kwargs=kwargs)


"""
Method triggered by group_modified signals.
"""
@receiver(group_modified)
def modified_handler(sender, group, fields, **kwargs):
    if settings.DEBUG:
        print "group_modified handler fired"
    if 'user_set' in fields and 'action' in kwargs['kwargs']:
        action = kwargs['kwargs']['action']
        if action == 'post_add':
            group_member_added.send(sender=sender, group=group, member=None, kwargs=kwargs)
        elif action == 'post_remove':
            group_member_removed.send(sender=sender, group=group, member=None, kwargs=kwargs)



"""
Internal receivers to map the Django built-in signals to custom ones.
"""
@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    if isinstance(instance, Group):
        action = kwargs['action']
        if action == 'post_add' or action == 'post_remove':
            group_modified.send(sender=sender, group=instance, fields=['user_set'], kwargs=kwargs)


@receiver(post_delete, sender=Group)
def post_delete_handler(sender, instance, **kwargs):
    group_deleted.send(sender=sender, group=instance, kwargs=kwargs)

@receiver(post_save, sender=Group)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
