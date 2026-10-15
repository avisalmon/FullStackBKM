#!/usr/bin/env python
"""Rename the blueprint's placeholders to your site's real name.

    python scripts/init_site.py --name coffee-club --site-name "Coffee Club"

Rewrites, in place, only the places that carry the placeholder name:
  render.yaml   - service name, disk name, SITE_NAME
  .env.example, .env (if present) - SITE_NAME
Safe to re-run with a different name. See docs/new_site_checklist.md.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = re.compile(r"^[a-z][a-z0-9-]{1,40}[a-z0-9]$")


def apply(root: Path, name: str, site_name: str) -> list[str]:
    """Apply the rename under `root`. Returns the files changed."""
    if not SLUG.match(name):
        raise ValueError("--name must be lowercase letters, digits and hyphens (e.g. coffee-club)")
    changed = []

    render = root / "render.yaml"
    text = render.read_text(encoding="utf-8")
    new = re.sub(r"(- type: web\n\s+name: )\S+", rf"\g<1>{name}", text)
    new = re.sub(r"(disk:\n\s+name: )\S+", rf"\g<1>{name}-disk", new)
    new = re.sub(r"(key: SITE_NAME\n\s+value: ).*", rf"\g<1>{site_name}", new)
    if new != text:
        render.write_text(new, encoding="utf-8", newline="\n")
        changed.append("render.yaml")

    # .env is the owner's live copy (already made from .env.example); keep both in step.
    for env_name in (".env.example", ".env"):
        env_file = root / env_name
        if not env_file.exists():
            continue
        text = env_file.read_text(encoding="utf-8")
        line = f"SITE_NAME={site_name}"
        if re.search(r"^SITE_NAME=", text, flags=re.M):
            new = re.sub(r"^SITE_NAME=.*$", lambda _: line, text, flags=re.M)
        else:
            new = text.rstrip("\n") + "\n" + line + "\n"
        if new != text:
            env_file.write_text(new, encoding="utf-8", newline="\n")
            changed.append(env_name)
    return changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--name", required=True, help="Render service slug, e.g. coffee-club")
    parser.add_argument("--site-name", help='Display name, e.g. "Coffee Club"')
    args = parser.parse_args(argv)
    site_name = args.site_name or args.name.replace("-", " ").title()
    try:
        changed = apply(ROOT, args.name, site_name)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("changed: " + (", ".join(changed) if changed else "nothing (already up to date)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
