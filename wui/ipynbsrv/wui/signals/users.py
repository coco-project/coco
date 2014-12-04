from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from ipynbsrv.wui.models import LdapUser
from ipynbsrv.wui.signals.signals import user_created, user_deleted, user_modified


"""
"""
@receiver(user_created)
def created_handler(sender, user, **kwargs):
    print "created user via signal"


"""
"""
@receiver(user_deleted)
def deleted_handler(sender, user, **kwargs):
    print "deleted user via signal"


"""
"""
@receiver(user_modified)
def modified_handler(sender, user, fields, **kwargs):
    print "modified user via signal"


#
# Bridges
#
"""
"""
@receiver(post_delete, sender=User, dispatch_uid='ipynbsrv.wui.signals.users.post_delete_handler')
def post_delete_handler(sender, instance, **kwargs):
    user_deleted.send(sender, user=instance)


"""
"""
@receiver(post_save, sender=User, dispatch_uid='ipynbsrv.wui.signals.users.post_save_handler')
def post_save_handler(sender, instance, **kwargs):
    if kwargs['created']:
        user_created.send(sender, user=instance)
    else:
        user_modified.send(sender, user=instance, fields=kwargs['update_fields'])
