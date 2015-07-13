from django_admin_conf_vars.global_vars import config

'''
Global variable storing the full class path of the storage backend to use.
'''
config.set('STORAGE_BACKEND_CLASS', default='ipynbsrv.backends.storage_backends.LocalFileSystem',
           editable=False, description='The full class path of the storage backend to use.')


'''
Global variable storing the base directory/path in which the storage backend should work.
'''
config.set('STORAGE_BASE_DIR', default='/srv/ipynbsrv/data/shares', editable=False,
           description='The base directory/path in which the storage backend should work.')


'''
Global variable storing the full class path of the group backend to use.
'''
config.set('GROUP_BACKEND_CLASS', default='ipynbsrv.backends.usergroup_backends.LdapGroupBackend', editable=False,
           description='The full class path of the group backend to use.')

'''
Global variable storing the arguments for the group backend
'''
config.set('GROUP_BACKEND_ARGS', default='{ "readonly" : False, "server": "localhost" , "user": "cn=admin,dc=ipynbsrv,dc=ldap" , "pw": "1234" }', editable=True,
           description='The arguments needed to instantiate the provided group backend class. Please provide in json format (i.e. { "arg1": "val1", "arg2": "val2" }')

'''
Global variable storing the full class path of the user backend to use.
'''
config.set('USER_BACKEND_CLASS', default='ipynbsrv.backends.usergroup_backends.LdapUserBackend', editable=True,
           description='The full class path of the user backend to use.')

'''
Global variable storing the arguments for the user backend
'''
config.set('USER_BACKEND_ARGS', default='{ "readonly" : False, "server": "localhost" , "user": "cn=admin,dc=ipynbsrv,dc=ldap" , "pw": "1234" }', editable=True,
           description='The arguments needed to instantiate the provided user backend class. Please provide in json format (i.e. { "arg1": "val1", "arg2": "val2" }')


'''
Global variable storing the instance of the server selection algorithm to use.
'''
config.set('SERVER_SELECTION_ALGORITHM_CLASS', default='ipynbsrv.core.algorithms.server_selection.RoundRobin',
           editable=True, description='The full class path of the server selection algorithm class to use.')