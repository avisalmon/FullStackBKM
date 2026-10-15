"""ASGI entry point (unused by the default Render start command; kept for completeness)."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

application = get_asgi_application()
