# coding=utf-8
__author__ = 'huangfuxin'

import celery
import os
from django.conf import settings

from gevent import monkey
monkey.patch_all()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'console.settings')
app = celery.Celery('console')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
