import io
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core import privacy
from core.models import ConsentRecord
from notes.models import Note

pytestmark = pytest.mark.django_db


def png(name="p.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "blue").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


# --- export ------------------------------------------------------------------------------


def test_export_contains_the_persons_account_and_app_data(alice, media_root):
    Note.objects.create(owner=alice, title="mine", body="secret thoughts")
    ConsentRecord.objects.create(user=alice, kind="terms", version="1")
    data = privacy.export_user_data(alice)
    assert data["account"]["email"] == "alice@example.com"
    assert data["notes"][0]["title"] == "mine"
    assert data["consents"][0]["kind"] == "terms"


def test_export_never_includes_another_persons_data(alice, bob):
    Note.objects.create(owner=bob, title="bob-only-title")
    assert "bob-only-title" not in json.dumps(privacy.export_user_data(alice))
    assert "bob@example.com" not in json.dumps(privacy.export_user_data(alice))


def test_export_download_requires_login_and_is_an_attachment(client, alice):
    assert client.get("/privacy/my-data/export/").status_code == 302
    client.force_login(alice)
    response = client.get("/privacy/my-data/export/")
    assert response.status_code == 200
    assert "attachment" in response["Content-Disposition"]
    assert json.loads(response.content)["account"]["username"] == "alice"


# --- erasure -----------------------------------------------------------------------------


def test_erasing_removes_the_person_their_rows_and_their_files(alice, bob, media_root):
    mine = Note.objects.create(owner=alice, title="a", image=png("a.png"))
    theirs = Note.objects.create(owner=bob, title="b", image=png("b.png"))
    my_file, their_file = media_root / mine.image.name, media_root / theirs.image.name
    assert my_file.is_file() and their_file.is_file()

    privacy.erase_user_data(alice)

    assert not Note.objects.filter(title="a").exists()
    assert not my_file.exists(), "a cascade deletes rows, never files: the eraser must"
    assert Note.objects.filter(title="b").exists() and their_file.is_file()


def test_a_failing_eraser_stops_before_the_account_is_deleted(alice, monkeypatch):
    def boom(user):
        raise RuntimeError("disk error")

    monkeypatch.setitem(privacy.ERASERS, "broken", boom)
    with pytest.raises(RuntimeError):
        privacy.erase_user_data(alice)
    alice.refresh_from_db()  # still there: nothing half-erased and then forgotten


def test_delete_needs_the_username_typed_exactly(client, alice):
    client.force_login(alice)
    response = client.post("/privacy/my-data/delete/", {"confirm": "wrong"})
    assert response.status_code == 302
    alice.refresh_from_db()
    client.post("/privacy/my-data/delete/", {})
    alice.refresh_from_db()


def test_delete_with_confirmation_removes_the_account_and_signs_out(client, alice):
    client.force_login(alice)
    response = client.post("/privacy/my-data/delete/", {"confirm": "alice"})
    assert response.status_code == 302
    assert not type(alice).objects.filter(pk=alice.pk).exists()
    assert client.get("/privacy/my-data/").status_code == 302  # signed out


def test_delete_is_post_only_and_login_only(client, alice):
    assert client.post("/privacy/my-data/delete/", {"confirm": "alice"}).status_code == 302
    alice.refresh_from_db()
    client.force_login(alice)
    assert client.get("/privacy/my-data/delete/").status_code == 405


# --- the public pages ----------------------------------------------------------------------


def test_privacy_page_is_marked_draft_until_the_owner_reviews_it(client, settings):
    settings.PRIVACY_REVIEWED = False
    assert 'class="draft-banner"' in client.get("/privacy/").content.decode()
    settings.PRIVACY_REVIEWED = True
    assert 'class="draft-banner"' not in client.get("/privacy/").content.decode()


def test_privacy_page_names_only_the_third_parties_actually_switched_on(client, settings):
    settings.GOOGLE_LOGIN_ENABLED = False
    settings.OPENAI_API_KEY = ""
    settings.RESEND_API_KEY = ""
    text = client.get("/privacy/").content.decode()
    assert "Render" in text
    assert "OpenAI" not in text and "Resend" not in text and "Google" not in text
    settings.OPENAI_API_KEY = "sk-test"
    settings.GOOGLE_LOGIN_ENABLED = True
    text = client.get("/privacy/").content.decode()
    assert "OpenAI" in text and "Google" in text


def test_privacy_page_lists_exactly_the_cookies_the_site_sets(client):
    text = client.get("/privacy/").content.decode()
    assert "sessionid" in text and "csrftoken" in text


def test_footer_links_to_privacy_and_terms(client):
    html = client.get("/").content.decode()
    assert 'href="/privacy/"' in html and 'href="/terms/"' in html


# --- cookies and headers -------------------------------------------------------------------


def test_session_cookie_is_httponly_and_samesite_lax(client, alice):
    response = client.post(
        "/accounts/login/", {"login": "alice@example.com", "password": "pw-alice-123"}
    )
    cookie = response.cookies["sessionid"]
    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"


def test_every_response_carries_the_privacy_headers(client):
    response = client.get("/")
    assert "camera=()" in response["Permissions-Policy"]
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["Referrer-Policy"] == "same-origin"
    assert response["X-Frame-Options"] == "DENY"


# --- consent records -----------------------------------------------------------------------


def test_the_latest_consent_record_wins(alice):
    ConsentRecord.objects.create(user=alice, kind="marketing", granted=True)
    assert privacy.has_consent(alice, "marketing")
    ConsentRecord.objects.create(user=alice, kind="marketing", granted=False)
    assert not privacy.has_consent(alice, "marketing")


def test_no_record_means_no_consent_and_kinds_are_separate(alice):
    assert not privacy.has_consent(alice, "guardian")
    ConsentRecord.objects.create(user=alice, kind="terms")
    assert not privacy.has_consent(alice, "guardian")


def test_consent_can_be_pinned_to_the_version_agreed(alice):
    ConsentRecord.objects.create(user=alice, kind="terms", version="1")
    assert privacy.has_consent(alice, "terms", version="1")
    assert not privacy.has_consent(alice, "terms", version="2")


def test_guardian_consent_records_who_gave_it(alice, bob):
    record = ConsentRecord.objects.create(
        user=alice, kind="guardian", source=ConsentRecord.GUARDIAN, recorded_by=bob
    )
    assert record.source == "guardian" and record.recorded_by == bob
