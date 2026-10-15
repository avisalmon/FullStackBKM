# Notes - data model

```
User (shared login, owned by django.contrib.auth)
  1 ──< N  Note
```

## Note

| Field | Type | Notes |
|---|---|---|
| `owner` | FK -> User, `CASCADE`, `related_name="notes"` | Set by the server from the session, never by the client |
| `title` | Char(200) | Required |
| `body` | Text | Optional |
| `image` | ImageField, `upload_to="notes/"` | Optional; stored under `MEDIA_ROOT` (`/var/data/media/notes/` on Render) |
| `created_at` | DateTime, auto | |
| `updated_at` | DateTime, auto | |

Ordering: newest first. Deleting a user deletes their notes. Deleting a note leaves its image file on disk
(a cleanup job is a possible backlog item; the offsite mirror keeps files regardless).

## Relationships to other apps

None. If Notes ever needs per-user settings, they go in a `NotesProfile` with a `OneToOneField` to the user, inside this app.

## Personal data (Rule 7)

| Field | Personal? | Sensitive? | Why we keep it | Who sees it | Kept |
|---|---|---|---|---|---|
| `owner` | yes (links to a person) | no | so notes belong to someone | the person; staff in admin | until the account is deleted |
| `title`, `body` | possibly (free text a person writes) | possibly | it is the product | the owner only | until the note or account is deleted |
| `image` | possibly (photos of people) | possibly | optional attachment | **anyone with the URL** (public `/media/`, random file name) | until deleted; the eraser removes the file |

Export: `notes/privacy.py` (`export_notes`). Erase: `erase_notes` deletes image files; the user delete cascades to the rows. Test: `tests/test_privacy.py`.
Decision to revisit if notes become sensitive: move images to private storage (see [privacy.md](../privacy.md) section 7).
