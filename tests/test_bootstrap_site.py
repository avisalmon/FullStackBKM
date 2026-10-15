"""bootstrap_site runs on EVERY boot, so the second run is the one that matters."""

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def run():
    call_command("bootstrap_site", verbosity=0)


def test_creates_superuser_once_and_never_resets_the_password(monkeypatch, django_user_model):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "first-password")
    run()
    admin = django_user_model.objects.get(username="admin")
    assert admin.is_superuser and admin.check_password("first-password")

    # Someone changes their password, then the service redeploys with the old env var.
    admin.set_password("changed-by-the-human")
    admin.save()
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "first-password")
    run()

    assert django_user_model.objects.filter(username="admin").count() == 1
    admin.refresh_from_db()
    assert admin.check_password("changed-by-the-human")


def test_without_superuser_env_it_creates_nobody(monkeypatch, django_user_model):
    for name in ("DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    run()
    assert django_user_model.objects.count() == 0


def test_site_record_follows_site_domain(monkeypatch, settings):
    monkeypatch.setenv("SITE_DOMAIN", "www.example.org")
    settings.SITE_NAME = "Example"
    run()
    site = Site.objects.get(pk=settings.SITE_ID)
    assert (site.domain, site.name) == ("www.example.org", "Example")
    run()  # idempotent
    assert Site.objects.filter(pk=settings.SITE_ID).count() == 1


def test_site_record_falls_back_to_render_hostname(monkeypatch, settings):
    monkeypatch.delenv("SITE_DOMAIN", raising=False)
    settings.RENDER_HOSTNAME = "my-site-ab12.onrender.com"
    run()
    assert Site.objects.get(pk=settings.SITE_ID).domain == "my-site-ab12.onrender.com"
