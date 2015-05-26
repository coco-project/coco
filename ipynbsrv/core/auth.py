from ipynbsrv.conf import global_vars


def login_allowed(user):
    '''
    @user_passes_test decorator callback that checks whether the
    passed in user is allowed to access the application or not.

    We do not want to allow non-LDAP users to access the application
    (because we need the LDAP entry for the shares etc.) so we check that here.
    '''
    if not user.username:
        return False
    else:
        l = global_vars._get_user_group_backend()
        return l.user_exists(user.username)
