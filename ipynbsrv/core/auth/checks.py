# from ipynbsrv.core.models import BackendUser


def login_allowed(user):
    """
    @user_passes_test decorator to check whether the user is allowed to access the application or not.

    We do not want to allow non-UserBackend users to access the application
    (because we need the LDAP entry for the shares etc.) so we check that here.
    """
    if user is None or user.get_username() is None:
        return False
    return hasattr(user, 'backend_user')
