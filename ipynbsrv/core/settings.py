'''
Setting storing the prefix that will be added to groups created internally for the shares.
'''
SHARE_GROUP_PREFIX = 'share_'


'''
Setting storing the group ID offset to be added to internal share groups to seperate them from regular groups.
'''
SHARE_GROUP_OFFSET = 9999


'''
Setting storing the base directory/path in which the storage backend should work.
'''
STORAGE_DIR_BASE = '/srv/ipynbsrv/data'


'''
Setting storing the path (relative to STORAGE_DIR_BASE) under which user home directories should be created.
'''
STORAGE_DIR_HOME = 'home/'


'''
Setting storing the path (relative to STORAGE_DIR_BASE) under which user publications should be stored.
'''
STORAGE_DIR_PUBLIC = 'public/'


'''
Setting storing the path (relative to STORAGE_DIR_BASE) under which shared directories should be stored.
'''
STORAGE_DIR_SHARES = 'shares/'


'''
Setting storing the unix user ID offset to be added to internal ldap users
'''
UNIX_USER_OFFSET = 2500
