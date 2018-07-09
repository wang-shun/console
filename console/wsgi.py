"""
WSGI config for Console project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

from gevent import monkey

monkey.patch_all()
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "console.settings")

os.environ['DJANGO_SETTINGS_MODULE'] = 'console.settings'


application = get_wsgi_application()