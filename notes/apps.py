from django.apps import AppConfig


class NotesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notes"

    def ready(self):
        from core import privacy

        from . import privacy as notes_privacy

        privacy.register("notes", notes_privacy.export_notes, notes_privacy.erase_notes)
