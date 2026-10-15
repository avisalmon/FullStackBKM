"""Shapes of credentials that must never be committed. Shared by verify_site.py and the tests."""

import re

PATTERNS = {
    "OpenAI key": re.compile(r"sk-(?:proj-|admin-)?[A-Za-z0-9_-]{32,}"),
    "Google OAuth secret": re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,}"),
    "Resend key": re.compile(r"\bre_[A-Za-z0-9]{20,}"),
    "Render API key": re.compile(r"\brnd_[A-Za-z0-9]{20,}"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}"),
    "AWS key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Service-account JSON": re.compile(r'"private_key_id"\s*:'),
}
