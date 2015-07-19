from django_admin_conf_vars.global_vars import config
from ipynbsrv.common.utils import ClassLoader
import json


"""
Internal LDAP helpers.
"""
_INTERNAL_LDAP = None


def get_internal_ldap():
    global _INTERNAL_LDAP
    if _INTERNAL_LDAP is None:
        module, klass = ClassLoader.split(config.INTERNAL_LDAP_CLASS)
        _INTERNAL_LDAP = ClassLoader(module, klass, config.INTERNAL_LDAP_ARGS)
    return _INTERNAL_LDAP.get_instance()


def get_internal_ldap_connected():
    """
    Return the internal LDAP instance with already called `connect` method.
    """
    backend = get_internal_ldap()
    backend.connect(json.loads(config.INTERNAL_LDAP_CONNECT_CREDENTIALS))
    return backend


"""
Server selection algorithm helpers.
"""
_SERVER_SELECTION_ALGORITHM = None


def get_server_selection_algorithm():
    global _SERVER_SELECTION_ALGORITHM
    if _SERVER_SELECTION_ALGORITHM is None:
        module, klass = ClassLoader.split(config.SERVER_SELECTION_ALGORITHM_CLASS)
        cl = ClassLoader(module, klass)
        _SERVER_SELECTION_ALGORITHM = cl.get_instance()
    return _SERVER_SELECTION_ALGORITHM


"""
Storage backend helpers.
"""
_STORAGE_BACKEND = None


def get_storage_backend():
    global _STORAGE_BACKEND
    if _STORAGE_BACKEND is None:
        module, klass = ClassLoader.split(config.STORAGE_BACKEND_CLASS)
        cl = ClassLoader(module, klass, config.STORAGE_BACKEND_ARGS)
        _STORAGE_BACKEND = cl.get_instance()
    return _STORAGE_BACKEND


"""
User backend helpers.
"""
_USER_BACKEND = None


def get_user_backend():
    global _USER_BACKEND
    if _USER_BACKEND is None:
        module, klass = ClassLoader.split(config.USER_BACKEND_CLASS)
        _USER_BACKEND = ClassLoader(module, klass, config.USER_BACKEND_ARGS)
    return _USER_BACKEND.get_instance()


def get_user_backend_connected():
    """
    Return the user backend instance with already called `connect` method.
    """
    backend = get_user_backend()
    backend.connect(json.loads(config.USER_BACKEND_CONNECT_CREDENTIALS))
    return backend
