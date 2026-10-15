#!/usr/bin/env python
"""Drive Render from the terminal, so you (or Claude) never have to click through the dashboard.

Needs a Render API key in RENDER_API_KEY (environment or the git-ignored .env file); the
service id may be kept in RENDER_SERVICE_ID so --service can be omitted.
Create one: Render -> Account Settings -> API Keys. Over HTTPS only, so it works behind
corporate firewalls that block SSH.

    python scripts/render_api.py services
    python scripts/render_api.py logs     --service srv-xxxx --minutes 30 [--grep Traceback]
    python scripts/render_api.py deploys  --service srv-xxxx
    python scripts/render_api.py deploy   --service srv-xxxx
    python scripts/render_api.py env-set  --service srv-xxxx KEY --from-env LOCAL_VAR
    python scripts/render_api.py env-set  --service srv-xxxx KEY --prompt
    python scripts/render_api.py domain   --service srv-xxxx --name www.example.com
    python scripts/render_api.py job      --service srv-xxxx --command "python manage.py check"

Secrets are never taken as a command-line value (they would land in shell history and in
chat transcripts): use --from-env to copy from a local variable, or --prompt to type it
hidden. NOT yet run against live Render: `services`, `logs` and `job` copy calls proven in the
reference site; `deploy`, `env-set` and `domain` follow Render's API reference. If a call is
rejected, the error body it prints says why - fix the script and tell the blueprint's owner.
"""

import argparse
import getpass
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = "https://api.render.com/v1"


def setting(name: str) -> str:
    """A value from the environment, else from the git-ignored .env file, else ''."""
    value = os.environ.get(name, "")
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not value and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                value = line.split("=", 1)[1].strip().strip("\"'")
    return value


def load_key() -> str:
    key = setting("RENDER_API_KEY")
    if not key:
        sys.exit("RENDER_API_KEY is not set. Create one in Render -> Account Settings -> API Keys.")
    return key


def call(method: str, path: str, **kwargs):
    response = requests.request(
        method,
        f"{API}{path}",
        headers={"Authorization": f"Bearer {load_key()}", "Accept": "application/json"},
        timeout=60,
        **kwargs,
    )
    if not response.ok:
        sys.exit(f"{method} {path} -> HTTP {response.status_code}\n{response.text[:1000]}")
    return response.json() if response.content else {}


def logs_params(owner_id: str, service: str, minutes: int, now=None) -> dict:
    """Render's log endpoint is owner-scoped, not service-scoped: both ids are required."""
    end = now or datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return {
        "ownerId": owner_id,
        "resource": service,
        "startTime": start.strftime(fmt),
        "endTime": end.strftime(fmt),
        "limit": 200,
    }


def cmd_services(args):
    for item in call("GET", "/services", params={"limit": 20}):
        svc = item.get("service", item)
        url = (svc.get("serviceDetails") or {}).get("url", "")
        print(f"{svc['id']}  {svc['name']:<24} {svc.get('type', '')}  {url}")


def cmd_logs(args):
    owner = call("GET", f"/services/{args.service}")["ownerId"]
    body = call("GET", "/logs", params=logs_params(owner, args.service, args.minutes))
    lines = sorted(body.get("logs", []), key=lambda entry: entry["timestamp"])
    for entry in lines:
        text = f"{entry['timestamp'][11:19]} {entry['message']}"
        if not args.grep or args.grep.lower() in text.lower():
            print(text)


def cmd_deploys(args):
    for item in call("GET", f"/services/{args.service}/deploys", params={"limit": 5}):
        d = item.get("deploy", item)
        message = d.get("commit", {}).get("message", "")[:60]
        print(f"{d['id']}  {d['status']:<16} {d.get('createdAt', '')}  {message}")


def cmd_deploy(args):
    print(call("POST", f"/services/{args.service}/deploys", json={}))


def cmd_env_set(args):
    if args.from_env:
        value = os.environ.get(args.from_env)
        if value is None:
            sys.exit(f"Local variable {args.from_env} is not set.")
    elif args.prompt:
        value = getpass.getpass(f"Value for {args.key} (hidden): ")
    else:
        sys.exit("Give --from-env NAME or --prompt. Secrets are not accepted as arguments.")
    call("PUT", f"/services/{args.service}/env-vars/{args.key}", json={"value": value})
    print(f"set {args.key} (Render redeploys when env vars change)")


def cmd_domain(args):
    print(call("POST", f"/services/{args.service}/custom-domains", json={"name": args.name}))


def cmd_job(args):
    print(call("POST", f"/services/{args.service}/jobs", json={"startCommand": args.command}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, *flags):
        p = sub.add_parser(name)
        if name != "services":
            p.add_argument(
                "--service",
                default=setting("RENDER_SERVICE_ID"),
                help="service id, e.g. srv-abc123 (default: RENDER_SERVICE_ID in .env)",
            )
        for flag, kwargs in flags:
            p.add_argument(flag, **kwargs)
        p.set_defaults(func=func)
        return p

    add("services", cmd_services)
    add("logs", cmd_logs, ("--minutes", {"type": int, "default": 15}), ("--grep", {}))
    add("deploys", cmd_deploys)
    add("deploy", cmd_deploy)
    p = add("env-set", cmd_env_set, ("--from-env", {}), ("--prompt", {"action": "store_true"}))
    p.add_argument("key")
    add("domain", cmd_domain, ("--name", {"required": True}))
    add("job", cmd_job, ("--command", {"required": True}))
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    if arguments.command != "services" and not arguments.service:
        sys.exit("Pass --service srv-... or set RENDER_SERVICE_ID in .env (see `services`).")
    arguments.func(arguments)
