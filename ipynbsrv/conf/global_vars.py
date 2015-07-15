from django_admin_conf_vars.global_vars import config
from ipynbsrv.common.utils import ClassLoader


"""
Global variables and functions returning the instance of the storage backend to use.
"""
_STORAGE_BACKEND = None


def _get_storage_backend():
    global _STORAGE_BACKEND
    if _STORAGE_BACKEND is None:
        module, klass = ClassLoader.split(config.STORAGE_BACKEND_CLASS)
        cl = ClassLoader(module, klass, '{"base_dir": "%s"}' % config.STORAGE_BASE_DIR)
        _STORAGE_BACKEND = cl.get_instance()
    return _STORAGE_BACKEND

STORAGE_BACKEND = _get_storage_backend()


'''
Global variables and functions returning the instance of the internal ldap.
'''
_INTERNAL_LDAP = None


def _get_internal_ldap():
    global _INTERNAL_LDAP
    if _INTERNAL_LDAP is None:
        module, klass = ClassLoader.split('ipynbsrv.backends.usergroup_backends.LdapBackend')
        cl = ClassLoader(module, klass, config.INTERNAL_LDAP_ARGS)
        _INTERNAL_LDAP = cl.get_instance()
    return _INTERNAL_LDAP

INTERNAL_LDAP = _get_internal_ldap()


'''
Global variables and functions returning the instance of the user backend to use.
'''
_USER_BACKEND = None


def _get_user_backend():
    global _USER_BACKEND
    if _USER_BACKEND is None:
        module, klass = ClassLoader.split(config.USER_BACKEND_CLASS)
        cl = ClassLoader(module, klass, config.USER_BACKEND_ARGS)
        _USER_BACKEND = cl.get_instance()
    return _USER_BACKEND

USER_BACKEND = _get_user_backend()


"""
Global variables and functions returning the instance of the usergroup backend to use.
"""
_SERVER_SELECTION_ALGORITHM = None


def _get_server_selection_algorithm():
    global _SERVER_SELECTION_ALGORITHM
    if _SERVER_SELECTION_ALGORITHM is None:
        module, klass = ClassLoader.split(config.SERVER_SELECTION_ALGORITHM_CLASS)
        cl = ClassLoader(module, klass)
        _SERVER_SELECTION_ALGORITHM = cl.get_instance()
    return _SERVER_SELECTION_ALGORITHM

SERVER_SELECTION_ALGORITHM = _get_server_selection_algorithm()
