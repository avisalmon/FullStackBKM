"""Minimal Google Cloud Storage client over the JSON API (service-account auth).

Used for offsite backups and the optional media bucket. Built on google-auth plus the
`requests` already in use, not the heavy google-cloud-storage package.

Configuration (both required, both secrets, both set in Render and your local .env):
    GCS_BUCKET           bucket name
    GCS_SERVICE_ACCOUNT  the service-account JSON key, base64-encoded
Set-up walkthrough: docs/procedures/gcs_bucket.md
"""

import base64
import json
import os
from datetime import datetime
from urllib.parse import quote

API = "https://storage.googleapis.com/storage/v1"
UPLOAD = "https://storage.googleapis.com/upload/storage/v1"
SCOPE = "https://www.googleapis.com/auth/devstorage.read_write"


class Bucket:
    def __init__(self, name: str, session):
        self.name = name
        self.session = session

    @classmethod
    def from_env(cls):
        """Return a Bucket, or None when GCS is not configured (the normal local case)."""
        name = os.environ.get("GCS_BUCKET", "").strip()
        encoded = os.environ.get("GCS_SERVICE_ACCOUNT", "").strip()
        if not (name and encoded):
            return None
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        info = json.loads(base64.b64decode(encoded))
        credentials = service_account.Credentials.from_service_account_info(info, scopes=[SCOPE])
        return cls(name, AuthorizedSession(credentials))

    def upload(self, path, object_name: str) -> None:
        with open(path, "rb") as handle:
            response = self.session.post(
                f"{UPLOAD}/b/{self.name}/o",
                params={"uploadType": "media", "name": object_name},
                data=handle,
                headers={"Content-Type": "application/octet-stream"},
            )
        response.raise_for_status()

    def list(self, prefix: str = "") -> list[dict]:
        """All objects under `prefix` as {name, size, created}; follows pagination."""
        items, token = [], None
        while True:
            params = {"prefix": prefix}
            if token:
                params["pageToken"] = token
            response = self.session.get(f"{API}/b/{self.name}/o", params=params)
            response.raise_for_status()
            body = response.json()
            for item in body.get("items", []):
                items.append(
                    {
                        "name": item["name"],
                        "size": int(item.get("size", 0)),
                        "created": datetime.fromisoformat(
                            item["timeCreated"].replace("Z", "+00:00")
                        ),
                    }
                )
            token = body.get("nextPageToken")
            if not token:
                return items

    def delete(self, object_name: str) -> None:
        response = self.session.delete(f"{API}/b/{self.name}/o/{quote(object_name, safe='')}")
        response.raise_for_status()

    def total_bytes(self, prefix: str = "") -> int:
        return sum(item["size"] for item in self.list(prefix))
