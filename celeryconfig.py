# needed for celery docker container
CELERY_IMPORTS = ('ipynbsrv.wui.tools')
CELERY_RESULT_BACKEND = 'rpc'