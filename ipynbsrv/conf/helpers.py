from django_admin_conf_vars.global_vars import config
from ipynbsrv.conf import global_vars
import json


internal_ldap = global_vars.INTERNAL_LDAP
user_backend = global_vars.USER_BACKEND


def get_user_backend_connected(username=None, password=None):
    """
    Return the user backend instance with already called `connect` method.
    """
    user_backend.connect(json.loads(
        get_interpolated_user_backend_connect_credentials(username, password)
    ))
    return user_backend


def get_interpolated_user_backend_connect_credentials(username, password):
    """
    Return the interpolated credentials to connect to the user backend.
    """
    return config.USER_BACKEND_CONNECT_CREDENTIALS.replace('%username%', username).replace('%password%', password)


def get_internal_ldap_connected():
    """
    Return the internal LDAP instance with already called `connect` method.
    """
    internal_ldap.connect(json.loads(config.INTERNAL_LDAP_CONNECT_CREDENTIALS))
    return internal_ldap
