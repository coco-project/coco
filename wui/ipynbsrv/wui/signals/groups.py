from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, LdapUser, Share
from ipynbsrv.wui.signals.signals import *


@receiver(post_group_created)
def create_ldap_group(sender, group, **kwargs):
    """
    Signal receiver that creates an LDAP group when ever a regular Django group is created.
    This is important for us so share groups are created.
    """
    if settings.DEBUG:
        print "create_ldap_group receiver fired"
    next_id = LdapGroup.objects.all().latest('id').id + 1
    if next_id < settings.SHARE_GROUPS_OFFSET:
        next_id = settings.SHARE_GROUPS_OFFSET + 1
    ldap_group = LdapGroup(id=next_id, name=group.name, members="")
    ldap_group.save()


@receiver(post_group_deleted)
def delete_ldap_group(sender, group, **kwargs):
    """
    Signal receiver to delete (share) groups from the LDAP server when
    they are deleted from Django.
    """
    if settings.DEBUG:
        print "delete_ldap_group receiver fired"
    ldap_group = LdapGroup.objects.filter(pk=group.name)
    if ldap_group.exists():
        ldap_group.first().delete()
        # make sure to also delete the share for this group
        share = Share.objects.filter(group=group)
        if share.exists():
            share.first().delete()
            share_deleted.send(sender=None, share=share)  # Django should do that for us


@receiver(post_group_member_added)
def update_ldap_group_members(sender, group, member, **kwargs):
    """
    We use that chance to add LDAP users to the LDAP group if both exist.
    """
    if settings.DEBUG:
        print "add_member_to_ldap_group receiver fired"
    ldap_group = LdapGroup.objects.get(pk=group.name)
    members = []
    for member in group.user_set.all():
        members.append(member.get_username())
    ldap_group.members = members
    ldap_group.save()


@receiver(post_group_member_removed)
def member_removed_handler(sender, group, member, **kwargs):
    update_ldap_group_members(sender=None, group=group, member=member, kwargs=kwargs)


@receiver(group_modified)
def modified_handler(sender, group, fields, **kwargs):
    if settings.DEBUG:
        print "group_modified handler fired"
    if 'user_set' in fields and 'action' in kwargs['kwargs']:
        action = kwargs['kwargs']['action']
        if action == 'post_add' or action == 'pre_add':
            if action == 'post_add':
                post_group_member_added.send(sender=sender, group=group, member=None, kwargs=kwargs)
            else:
                pre_group_member_added.send(sender=sender, group=group, member=None, kwargs=kwargs)
            group_member_added.send(sender=sender, group=group, member=None, action=action, kwargs=kwargs)
        elif action == 'post_remove' or action == 'pre_remove':
            if action == 'post_remove':
                post_group_member_removed.send(sender=sender, group=group, member=None, kwargs=kwargs)
            else:
                pre_group_member_removed.send(sender=sender, group=group, member=None, kwargs=kwargs)
            group_member_removed.send(sender=sender, group=group, member=None, action=action, kwargs=kwargs)


# ###############################################


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_handler(sender, instance, **kwargs):
    if isinstance(instance, Group):
        action = kwargs['action']
        if action == 'post_add' or action == 'post_remove'
        or action == 'pre_add' or action == 'pre_remove':
            if action == 'post_add' or action == 'post_remove':
                post_group_modified.send(sender=sender, group=instance, fields=['user_set'], kwargs=kwargs)
            elif action == 'pre_add' or action == 'pre_remove':
                pre_group_modified.send(sender=sender, group=instance, fields=['user_set'], kwargs=kwargs)
            group_modified.send(sender=sender, group=instance, fields=['user_set'], action=action kwargs=kwargs)


@receiver(post_delete, sender=Group)
def post_delete_handler(sender, instance, **kwargs):
    post_group_deleted.send(sender=sender, group=instance, kwargs=kwargs)
    group_deleted.send(sender=sender, group=instance, action='post_delete' kwargs=kwargs)


@receiver(pre_delete, sender=Group)
def pre_delete_handler(sender, instance, **kwargs):
    pre_group_deleted.send(sender=sender, group=instance, kwargs=kwargs)
    group_deleted.send(sender=sender, group=instance, action='pre_delete' kwargs=kwargs)


@receiver(post_save, sender=Group)
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        post_group_created.send(sender=sender, group=instance, kwargs=kwargs)
        group_created.send(sender=sender, group=instance, action='post_save' kwargs=kwargs)
    else:
        post_group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], action='post_save' kwargs=kwargs)


@receiver(pre_save, sender=Group)
def pre_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        pre_group_created.send(sender=sender, group=instance, kwargs=kwargs)
        group_created.send(sender=sender, group=instance, action='pre_save' kwargs=kwargs)
    else:
        pre_group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], action='pre_save' kwargs=kwargs)
