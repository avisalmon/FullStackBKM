import uuid
from pathlib import Path

from django.conf import settings
from django.db import models


def note_image_path(instance, filename):
    """Store uploads under a random name. People name files after themselves and their children
    (`dana-levi-passport.jpg`), and /media/ is served to anyone who has the URL, so the original
    name must never be part of it. This makes the URL unguessable; it does NOT make it private
    (see docs/privacy.md, 'Uploaded files')."""
    return f"notes/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class Note(models.Model):
    """A person's private note, optionally with a picture.

    The only thing this app shares with the rest of the site is the login: `owner` is a
    plain foreign key to the shared user model. Anything else about a user that this app
    needs would go in a one-to-one profile model inside this app, never on `User`
    (docs/building_an_app.md, Rule 2).
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    # Lives under MEDIA_ROOT (the persistent disk on Render): survives redeploys.
    image = models.ImageField(upload_to=note_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title
