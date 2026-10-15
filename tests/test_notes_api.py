import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from notes.models import Note

API = "/notes/api/notes/"

pytestmark = pytest.mark.django_db


@pytest.fixture
def api(alice):
    client = APIClient()
    client.force_authenticate(alice)
    return client


def png_upload(name="pic.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


# --- the refusals first: they are what make the API safe to build on -----------------


def test_anonymous_is_refused_everywhere(alice):
    note = Note.objects.create(owner=alice, title="private")
    anon = APIClient()
    assert anon.get(API).status_code == 403
    assert anon.post(API, {"title": "x"}, format="json").status_code == 403
    assert anon.get(f"{API}{note.pk}/").status_code == 403
    assert anon.delete(f"{API}{note.pk}/").status_code == 403


def test_other_peoples_notes_do_not_exist_for_you(api, bob):
    theirs = Note.objects.create(owner=bob, title="bob's")
    url = f"{API}{theirs.pk}/"
    assert api.get(url).status_code == 404
    assert api.patch(url, {"title": "mine now"}, format="json").status_code == 404
    assert api.delete(url).status_code == 404
    theirs.refresh_from_db()
    assert theirs.title == "bob's"


def test_list_contains_only_my_notes(api, alice, bob):
    Note.objects.create(owner=alice, title="mine")
    Note.objects.create(owner=bob, title="bob's")
    titles = [n["title"] for n in api.get(API).json()]
    assert titles == ["mine"]


def test_owner_cannot_be_chosen_by_the_client(api, alice, bob):
    response = api.post(API, {"title": "t", "owner": bob.pk}, format="json")
    assert response.status_code == 201
    assert Note.objects.get(pk=response.json()["id"]).owner == alice
    assert "owner" not in response.json()


def test_title_is_required(api):
    assert api.post(API, {"body": "no title"}, format="json").status_code == 400


# --- the happy paths ----------------------------------------------------------------


def test_full_crud_cycle(api):
    created = api.post(API, {"title": "first", "body": "hello"}, format="json")
    assert created.status_code == 201
    pk = created.json()["id"]

    assert api.get(f"{API}{pk}/").json()["body"] == "hello"

    patched = api.patch(f"{API}{pk}/", {"title": "renamed"}, format="json")
    assert patched.status_code == 200
    assert patched.json()["title"] == "renamed"
    assert patched.json()["body"] == "hello"

    replaced = api.put(f"{API}{pk}/", {"title": "again", "body": ""}, format="json")
    assert replaced.status_code == 200

    assert api.delete(f"{API}{pk}/").status_code == 204
    assert api.get(f"{API}{pk}/").status_code == 404


def test_image_upload_lands_on_media_and_is_served(api, client, media_root):
    response = api.post(API, {"title": "pic", "image": png_upload()}, format="multipart")
    assert response.status_code == 201
    image_url = response.json()["image"]
    assert "/media/notes/" in image_url
    path = image_url.split("/media/", 1)[1]
    assert (media_root / path).is_file()
    assert client.get("/media/" + path).status_code == 200


# --- the page ------------------------------------------------------------------------


def test_page_requires_login(client):
    response = client.get("/notes/")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_page_renders_with_its_own_layout(client, alice):
    client.force_login(alice)
    response = client.get("/notes/")
    assert response.status_code == 200
    html = response.content.decode()
    assert 'id="notes-list"' in html
    # Rule 3: the app brings its own chrome and never the site's.
    assert 'class="site-header"' not in html


def test_uploaded_files_never_keep_the_original_name(api, media_root):
    upload = png_upload("dana-levi-passport.PNG")
    response = api.post(API, {"title": "x", "image": upload}, format="multipart")
    name = response.json()["image"]
    assert "dana" not in name and "passport" not in name
    assert name.endswith(".png")
