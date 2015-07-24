from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.core.models import GroupShare
from ipynbsrv.core.signals.signals import group_member_added, group_member_removed, \
    group_share_created, group_share_deleted


@receiver(group_member_added)
def add_user_to_share_groups(sender, group, user, **kwargs):
    """
    Add the user to all share groups the entered group has access to.
    """
    if group is not None and user is not None and \
            hasattr(user, 'backend_user'):
        for group_share in GroupShare.objects.filter(group=group):
            group_share.share.add_member(user.backend_user)


@receiver(group_member_removed)
def remove_user_from_share_groups(sender, group, user, **kwargs):
    """
    Remove the user from share groups the group had access to.

    Scenario: A user is within a group and a share access is granted to that group.
    The user is added to the share group for that reason. Now, he leaves the group
    (not the share directly), so we have to make sure he also leaves all the share groups.
    """
    if group is not None and user is not None and \
            hasattr(user, 'backend_user'):
        # TODO: only if not within an other group that has access as well
        # FIXME: fails (member already deleted on LDAP group -> LdapBackend throws error)
        #        no idea why the user is already removed. modifies other group's as well :O
        for group_share in GroupShare.objects.filter(group=group):
            group_share.share.remove_member(user.backend_user)


@receiver(group_share_created)
def add_group_members_to_share_group(sender, group, share, **kwargs):
    """
    Upon associating a share with a group, all members of that group need to be in the share group.
    """
    if group is not None and share is not None:
        for user in group.user_set.all():
            if hasattr(user, 'backend_user'):
                share.add_member(user.backend_user)


@receiver(group_share_deleted)
def remove_group_members_from_share_group(sender, group, share, **kwargs):
    """
    Remove the users from the group from the share group.
    """
    if group is not None and share is not None:
        # TODO: only if not within an other group that has access as well
        for user in group.user_set.all():
            if hasattr(user, 'backend_user'):
                share.remove_member(user.backend_user)


@receiver(post_delete, sender=GroupShare)
def post_share_delete_handler(sender, instance, **kwargs):
    """
    Method to map Django post_delete model signals to custom ones.
    """
    group_share_deleted.send(
        sender=sender,
        group=instance.group,
        share=instance.share,
        kwargs=kwargs
    )


@receiver(post_save, sender=GroupShare)
def post_share_save_handler(sender, instance, **kwargs):
    """
    Method to map Django post_save model signals to custom ones.
    """
    if 'created' in kwargs and kwargs.get('created'):
        group_share_created.send(
            sender=sender,
            group=instance.group,
            share=instance.share,
            kwargs=kwargs
        )
