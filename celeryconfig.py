# needed for celery docker container
CELERY_IMPORTS = ('ipynbsrv.wui.tasks')
CELERY_RESULT_BACKEND = 'rpc'
