import json

import pytest


def test_home_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1>My Site</h1>" in response.content


def test_healthz_is_ok_and_json(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert json.loads(response.content) == {"status": "ok"}


def test_healthz_is_exempt_from_https_redirect_but_pages_are_not(settings, client):
    """Render's health check may arrive over plain http; a 301 would fail the deploy."""
    settings.SECURE_SSL_REDIRECT = True
    assert client.get("/healthz").status_code == 200
    assert client.get("/").status_code == 301


def test_media_is_served_when_debug_is_false(client, media_root, settings):
    """Gotcha #13: django.conf.urls.static.static() returns [] when DEBUG=False."""
    settings.DEBUG = False
    (media_root / "hello.txt").write_text("hi")
    response = client.get("/media/hello.txt")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b"hi"


def test_media_rejects_path_traversal(client, media_root):
    (media_root.parent / "secret.txt").write_text("nope")
    response = client.get("/media/..%2Fsecret.txt")
    # Django refuses a path that escapes MEDIA_ROOT (400 SuspiciousFileOperation).
    assert response.status_code in (400, 404)
    assert b"nope" not in response.content


def test_unknown_url_uses_site_404_page(client):
    response = client.get("/definitely/not/here/")
    assert response.status_code == 404
    assert b"Page not found" in response.content


@pytest.mark.django_db  # allauth looks up the Site record
def test_login_page_is_inside_site_layout(client):
    """allauth pages are wrapped by templates/allauth/layouts/base.html."""
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert b'class="site-header"' in response.content


def test_google_button_hidden_without_credentials(client, settings):
    settings.GOOGLE_LOGIN_ENABLED = False
    assert b"Continue with Google" not in client.get("/").content


def test_google_button_shown_with_credentials(client, settings):
    settings.GOOGLE_LOGIN_ENABLED = True
    assert b"Continue with Google" in client.get("/").content


def test_robots_txt_blocks_private_areas(client):
    body = client.get("/robots.txt").content.decode()
    assert "Disallow: /admin/" in body
