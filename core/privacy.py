"""Where personal data is declared, exported and erased.

Privacy rights (a person can see their data, take a copy, and have it deleted) only work if the
site knows *where* it keeps personal data. So each app that stores something about a person
registers two small functions in its AppConfig.ready():

    from core import privacy
    privacy.register("notes", exporter=export_notes, eraser=erase_notes)

* exporter(user) -> anything JSON-serialisable: the person's data from that app.
* eraser(user)   -> remove what deleting the User row would NOT remove by itself, typically
                    uploaded FILES (a cascade deletes rows, never files on disk).

`erase_user_data` runs every eraser and then deletes the user, which cascades to their rows.
See docs/privacy.md. The blueprint is an advisor here: whether and how you offer these is the
owner's decision (record it in docs/privacy_decisions.md).
"""

import logging

from .models import ConsentRecord

logger = logging.getLogger(__name__)

EXPORTERS = {}
ERASERS = {}


def register(name, exporter, eraser=None):
    EXPORTERS[name] = exporter
    if eraser is not None:
        ERASERS[name] = eraser


def export_user_data(user) -> dict:
    """Everything the site holds about `user`, as plain data."""
    data = {
        "account": {
            "username": user.get_username(),
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        },
        "consents": [
            {
                "kind": c.kind,
                "version": c.version,
                "granted": c.granted,
                "source": c.source,
                "recorded_at": c.recorded_at.isoformat(),
            }
            for c in ConsentRecord.objects.filter(user=user)
        ],
    }
    for name, exporter in EXPORTERS.items():
        data[name] = exporter(user)
    return data


def erase_user_data(user) -> None:
    """Run every app's eraser, then delete the account (cascading to the person's rows)."""
    for name, eraser in ERASERS.items():
        try:
            eraser(user)
        except Exception:  # noqa: BLE001 - never leave a half-erased person: keep going, log loudly
            logger.exception("eraser %s failed for user %s", name, user.pk)
            raise
    user.delete()


def has_consent(user, kind: str, version: str | None = None) -> bool:
    """True if the most recent record of this kind (and version, if given) is a grant."""
    records = ConsentRecord.objects.filter(user=user, kind=kind)
    if version is not None:
        records = records.filter(version=version)
    latest = records.order_by("-recorded_at", "-id").first()
    return bool(latest and latest.granted)
