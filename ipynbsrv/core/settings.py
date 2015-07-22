"""
Settings defining the prefixes to be used in backend names for container resources.
"""
CONTAINER_NAME_PREFIX = 'ipynbsrv-'
CONTAINER_IMAGE_NAME_PREFIX = CONTAINER_NAME_PREFIX
CONTAINER_SNAPSHOT_PREFIX = 'snapshot_'


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
