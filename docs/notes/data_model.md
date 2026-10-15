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
