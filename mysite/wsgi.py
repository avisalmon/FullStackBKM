"""WSGI entry point - what gunicorn serves (`gunicorn mysite.wsgi:application`)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

application = get_wsgi_application()
