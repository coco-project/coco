from django_admin_conf_vars.global_vars import config


"""
Storage backend related configuration options.
"""
config.set('STORAGE_BACKEND_CLASS', default='ipynbsrv.backends.storage_backends.LocalFileSystem',
           editable=False, description='The full class path of the storage backend to use.')

config.set('STORAGE_BASE_DIR', default='/srv/ipynbsrv/data', editable=False,
           description='The base directory/path in which the storage backend should work.')


"""
Global variable storing the arguments for the internal ldap backend
"""
config.set('INTERNAL_LDAP_ARGS', default='{ "readonly" : False, "server": "ipynbsrv_ldap" , "user": "cn=admin,dc=ipynbsrv,dc=ldap" , "pw": "123456" }', editable=True,
           description='The arguments needed to instantiate the internal ldap backend. Please provide in json format (i.e. { "arg1": "val1", "arg2": "val2" }')


"""
User backend related configuration options.
"""
config.set('USER_BACKEND_CLASS', default='ipynbsrv.backends.usergroup_backends.LdapBackend', editable=True,
           description='The full class path of the user backend to use.')

config.set('USER_BACKEND_ARGS', default='{ "readonly" : False, "server": "localhost" , "user": "cn=admin,dc=ipynbsrv,dc=ldap" , "pw": "1234" }', editable=True,
           description='The arguments needed to instantiate the provided user backend class. Please provide in json format (i.e. { "arg1": "val1", "arg2": "val2" }')


"""
Global variable storing the instance of the server selection algorithm to use.
"""
config.set('SERVER_SELECTION_ALGORITHM_CLASS', default='ipynbsrv.core.algorithms.server_selection.RoundRobin',
           editable=True, description='The full class path of the server selection algorithm class to use.')
