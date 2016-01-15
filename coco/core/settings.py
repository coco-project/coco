from django.conf import settings

"""
Settings related to containers.
"""
CONTAINER_ACCESS_BASE_URI = '/' + settings.SUBDIRECTORY + 'ct/'
CONTAINER_PORT_MAPPINGS_START_PORT = 49152
CONTAINER_PORT_MAPPINGS_END_PORT = 65534

"""
Settings storing the paths (relative to STORAGE_DIR_BASE) under which (user) directories should be created.
"""
STORAGE_DIR_HOME = 'homes/'
STORAGE_DIR_PUBLIC = 'public/'
STORAGE_DIR_SHARES = 'shares/'

"""
Setting storing the prefix for the helper groups used to manage access to shares.
"""
SHARE_GROUP_PREFIX = 'SHR_'

"""
Setting storing the user ID offset to be added to internal ldap users
"""
USER_ID_OFFSET = 2500

"""
Setting storing the group ID offset to be added to internal ldap groups
"""
GROUP_ID_OFFSET = 5500
