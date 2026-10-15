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
