from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapGroup, LdapUser, Share
from ipynbsrv.wui.signals.signals import *


@receiver(group_created)
def create_ldap_group(sender, group, **kwargs):
    """
    Signal to create an LDAP group when ever a Django group is created.
    Since Django groups are only used for shares, we always need a corresponding LDAP group.
    """
    if settings.DEBUG:
        print "create_ldap_group receiver fired"
    if group is not None:
        next_id = LdapGroup.objects.all().latest('id').id + 1
        # if this is the first share group, make sure to add the defined offset
        if next_id < settings.SHARE_GROUPS_OFFSET:
            next_id = settings.SHARE_GROUPS_OFFSET + 1
        ldap_group = LdapGroup(id=next_id, name=group.name, members="")
        ldap_group.save()


@receiver(group_deleted)
def delete_ldap_group(sender, group, **kwargs):
    """
    Signal to delete a removed group from the LDAP server.
    """
    if settings.DEBUG:
        print "delete_ldap_group receiver fired"
    if group is not None:
        ldap_group = LdapGroup.objects.filter(pk=group.name)
        if ldap_group.exists():
            ldap_group.first().delete()
            # make sure to also delete the share for this group
            share = Share.objects.filter(group=group)
            if share.exists():
                share.first().delete()
                # share_deleted.send(sender=None, share=share)  # Django should do that for us


@receiver(group_member_added)
def add_member_to_ldap_group(sender, group, users, **kwargs):
    """
    When ever a member is added to a group we need to sync the LDAP group
    so shares work as expected.
    """
    if settings.DEBUG:
        print "add_member_to_ldap_group receiver fired"
    if group is not None and users is not None:
        ldap_group = LdapGroup.objects.get(pk=group.name)
        for user in users:
            ldap_group.members.append(user.get_username())
        ldap_group.save()


@receiver(group_member_removed)
def remove_member_from_ldap_group(sender, group, users, **kwargs):
    """
    When ever a member is removed to a group we need to sync the LDAP group
    so shares work as expected.
    """
    if settings.DEBUG:
        print "remove_member_from_ldap_group receiver fired"
    if group is not None and users is not None:
        ldap_group = LdapGroup.objects.get(pk=group.name)
        for user in users:
            ldap_group.members.remove(user.get_username())
        ldap_group.save()


@receiver(group_modified)
def group_modified_handler(sender, group, fields, **kwargs):
    if settings.DEBUG:
        print "group_modified_handler receiver fired"
    kwargs = kwargs['kwargs']  # not sure why this is needed
    if 'user_set' in fields:
        # get the user objects
        users = []
        if kwargs['pk_set'] is not None:
            for user_pk in kwargs['pk_set']:
                users.append(User.objects.get(pk=user_pk))
        # trigger the signals
        action = kwargs['action']
        if action == 'post_add':
            group_member_added.send(sender=sender, group=group, users=users, kwargs=kwargs)
        elif action == 'post_remove':
            group_member_removed.send(sender=sender, group=group, users=users, kwargs=kwargs)


# ###############################################


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
    if 'created' in kwargs and kwargs['created']:
        group_created.send(sender=sender, group=instance, kwargs=kwargs)
    else:
        group_modified.send(sender=sender, group=instance, fields=kwargs['update_fields'], kwargs=kwargs)
