"""
WSGI config for slackbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys


sys.path.append('/app')
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slackbot.settings")

# sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

application = get_wsgi_application()

