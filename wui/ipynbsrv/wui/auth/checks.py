from django.contrib.auth.models import User
from ipynbsrv.wui.models import LdapUser


"""
"""
def login_allowed(user):
    return user.is_active \
        and LdapUser.objects.filter(pk=user.username).exists()
