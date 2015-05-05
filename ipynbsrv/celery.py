from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipynbsrv.settings')

# causes problems with celery docker container
# from django.conf import settings

app = Celery('ipynbsrv',
             broker='amqp://guest:guest@172.17.0.2',
             backend='rpc',)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

# automatically search for tasks.py files (causes problems with celery docker container)
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))