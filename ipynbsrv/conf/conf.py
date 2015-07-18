from django_admin_conf_vars.global_vars import config


"""
Storage backend related configuration options.
"""
config.set('STORAGE_BACKEND_CLASS',
           default='ipynbsrv.backends.storage_backends.LocalFileSystem',
           editable=True,
           description='The full class path of the storage backend to use.')

config.set('STORAGE_BACKEND_ARGS',
           default='{"base_dir": "/srv/ipynbsrv/data"}',
           editable=True,
           description='The arguments needed to instantiate the storage backend. Please provide in JSON format (i.e. { "arg1": "val1", "arg2": "val2" }).')


"""
Global variable storing the arguments for the internal ldap backend
"""
config.set('INTERNAL_LDAP_CLASS',
           default='ipynbsrv.backends.usergroup_backends.LdapBackend',
           editable=True,
           description='The full class path of the backend to use for the internal server.')

config.set('INTERNAL_LDAP_ARGS',
           default='{"server": "ipynbsrv_ldap", "base_dn": "dc=ipynbsrv,dc=ldap", "users_dn": "ou=users", "groups_dn": "ou=groups"}',
           editable=True,
           description='The arguments needed to instantiate the internal LDAP backend. Please provide in JSON format (i.e. { "arg1": "val1", "arg2": "val2" }).')

config.set('INTERNAL_LDAP_CONNECT_CREDENTIALS',
           default='{"dn": "cn=admin,dc=ipynbsrv,dc=ldap", "password": "123456"}',
           editable=True,
           description='The credentials used to establish a connection to the user backend. Use %username% and %password% for the credentials of the currently authenticating user.')


"""
User backend related configuration options.
"""
config.set('USER_BACKEND_CLASS',
           default='ipynbsrv.backends.usergroup_backends.LdapBackend',
           editable=True,
           description='The full class path of the user backend to use.')

config.set('USER_BACKEND_ARGS',
           default='{"server": "ipynbsrv_ldap", "base_dn": "dc=ipynbsrv,dc=ldap", "users_dn": "ou=users"}',
           editable=True,
           description='The arguments needed to instantiate the provided user backend class. Please provide in json format (i.e. { "arg1": "val1", "arg2": "val2" }).')

config.set('USER_BACKEND_CONNECT_CREDENTIALS',
           default='{"dn": "cn=admin,dc=ipynbsrv,dc=ldap", "password": "123456"}',
           editable=True,
           description='The credentials used to establish a connection to the user backend. Use %username% and %password% for the credentials of the currently authenticating user.')


"""
Global variable storing the instance of the server selection algorithm to use.
"""
config.set('SERVER_SELECTION_ALGORITHM_CLASS', default='ipynbsrv.core.algorithms.server_selection.RoundRobin',
           editable=True, description='The full class path of the server selection algorithm class to use.')
