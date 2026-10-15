"""One idempotent boot step for Render's startCommand.

    python manage.py bootstrap_site && gunicorn mysite.wsgi:application ...

Why a command instead of a long `a && (b || true) && c` shell chain in render.yaml:
Render has been seen to drop the parentheses on a container restart, which turns
`migrate && x || true && gunicorn` into "start gunicorn even though migrate failed".
Logic in Python can't be re-parsed by a shell. And it can't run in build.sh at all:
the persistent disk is read-only during the build, so `migrate` has nowhere to write.

Every step is safe to run on every boot. A migration failure raises, so the deploy
fails visibly instead of serving a half-migrated database.
"""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Migrate, ensure the superuser exists, and point the Site record at this host."

    def handle(self, *args, **options):
        call_command("migrate", interactive=False, verbosity=1)
        self._ensure_superuser()
        self._sync_site()

    def _ensure_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        if not (username and password):
            self.stdout.write("superuser: DJANGO_SUPERUSER_* not set - skipped")
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"superuser: '{username}' already exists - left alone")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f"superuser: created '{username}'")

    def _sync_site(self):
        """Keep django.contrib.sites (used by allauth for links and OAuth) on the real host.

        Fresh databases ship with example.com, which is the classic reason Google login
        redirects to the wrong place. SITE_DOMAIN wins (set it to your custom domain);
        otherwise the hostname Render assigned.
        """
        domain = os.environ.get("SITE_DOMAIN", "").strip() or settings.RENDER_HOSTNAME
        if not domain:
            self.stdout.write("site: no SITE_DOMAIN / RENDER_EXTERNAL_HOSTNAME - skipped")
            return
        site, _ = Site.objects.get_or_create(pk=settings.SITE_ID)
        if (site.domain, site.name) != (domain, settings.SITE_NAME):
            site.domain, site.name = domain, settings.SITE_NAME
            site.save()
            self.stdout.write(f"site: set to {domain}")
        else:
            self.stdout.write(f"site: already {domain}")
