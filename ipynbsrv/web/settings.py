'''
Setting storing the name of the cookie that is used to check access via the reverse proxy to containers.
'''
AUTH_COOKIE_NAME = 'username'


'''
Setting storing the name of the header that is indicating the requested URI, the reverse proxy is adding to sub-requests.
'''
PROXY_URI_HEADER = 'HTTP_X_ORIGINAL_URI'


'''
Setting storing the URL under which the application\'s documentation can be found.
'''
URL_DOCS = '/docs/'


'''
Setting storing the URL under which the user publications can be found.
'''
URL_PUBLIC = '/public/'
