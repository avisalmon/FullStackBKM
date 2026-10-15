"""Root pytest configuration shared by every test."""

import pytest


def pytest_configure(config):
    from django.conf import settings

    # Plain static storage so templates using {% static %} render without a prior
    # collectstatic (the manifest storage used when DEBUG=False needs one).
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    # Password hashing is deliberately slow; a test that logs in as five people pays that
    # five times. Nothing here asserts anything about the algorithm.
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def media_root(tmp_path, settings):
    """Point uploads at a throwaway folder so tests never write into the real media/."""
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.MEDIA_ROOT.mkdir()
    return settings.MEDIA_ROOT


@pytest.fixture
def alice(django_user_model):
    return django_user_model.objects.create_user("alice", "alice@example.com", "pw-alice-123")


@pytest.fixture
def bob(django_user_model):
    return django_user_model.objects.create_user("bob", "bob@example.com", "pw-bob-123")


REAL_SERVICE_ENV = (
    "GCS_BUCKET",
    "GCS_SERVICE_ACCOUNT",
    "OPENAI_API_KEY",
    "OPENAI_ADMIN_KEY",
    "RESEND_API_KEY",
    "RENDER_API_KEY",
    "RENDER_SERVICE_ID",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "TASK_TRIGGER_TOKEN",
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_PASSWORD",
    "SITE_DOMAIN",
)


@pytest.fixture(autouse=True)
def isolate_from_the_owners_real_configuration(monkeypatch, settings):
    """Tests must behave the same on every machine, whatever is in the owner's `.env`.

    Found by a cold-start test: after `init_site.py` renamed the site, a test that expected the
    placeholder name failed; and with a real GCS bucket or OpenAI key in `.env`, the backup and AI
    tests would have talked to the owner's REAL accounts (and spent their money / touched their
    backups). So every credential is removed and every environment-dependent setting is pinned
    before each test. A test that needs a service sets it up itself, with a fake.
    """
    for name in REAL_SERVICE_ENV:
        monkeypatch.delenv(name, raising=False)
    settings.SITE_NAME = "My Site"
    settings.OPENAI_API_KEY = ""
    settings.RESEND_API_KEY = ""
    settings.GOOGLE_LOGIN_ENABLED = False
    settings.TASK_TRIGGER_TOKEN = ""
    settings.PLAUSIBLE_DOMAIN = ""
    settings.OWNER_EMAIL = ""
    settings.ADMINS = []
    settings.PRIVACY_REVIEWED = False
    settings.MONTHLY_BUDGET_USD = 0
    settings.DOMAIN_YEARLY_USD = 0
    settings.RENDER_MONTHLY_USD = 7.25
    settings.OPENAI_MONTHLY_COST_CAP_USD = 20
    settings.OPENAI_DAILY_TOKEN_LIMIT_PER_USER = 50000
    settings.RENDER_HOSTNAME = ""
