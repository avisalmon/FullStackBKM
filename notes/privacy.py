"""What the Notes app knows about a person, for their export and erasure (docs/privacy.md)."""

from .models import Note


def export_notes(user):
    return [
        {
            "title": note.title,
            "body": note.body,
            "image": note.image.name if note.image else None,
            "created_at": note.created_at.isoformat(),
        }
        for note in Note.objects.filter(owner=user)
    ]


def erase_notes(user):
    """Deleting the user cascades to their Note rows, but never to the picture FILES on disk:
    delete those here or they would outlive the person (and be mirrored to the backup bucket)."""
    for note in Note.objects.filter(owner=user).exclude(image=""):
        if note.image:
            note.image.delete(save=False)
