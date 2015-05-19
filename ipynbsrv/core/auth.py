from ipynbsrv.core.models import LdapUser


def login_allowed(user):
    '''
    @user_passes_test decorator callback that checks either the
    passed in user is allowed to access the application or not.

    We do not want to allow non-LDAP users to access the application
    (because we need the LDAP entry for the shares etc.) so we check that here.
    '''
    return user.is_active and LdapUser.objects.filter(pk=user.username).exists()
