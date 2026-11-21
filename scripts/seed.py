#!/usr/bin/env python3
"""Seed a local NeatSprint tenant and demo users.

Calls the bootstrap endpoints exposed by Core and IAM on their host ports. Those
endpoints are guarded by BOOTSTRAP_TOKEN and disabled when the variable is unset.

Usage: python scripts/seed.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "NeatSprint!2026"

USERS = [
    ("owner@acme-labs.com", "Olivia Owner", ["OWNER"]),
    ("admin@acme-labs.com", "Adam Admin", ["ADMIN"]),
    ("manager@acme-labs.com", "Maya Manager", ["MANAGER"]),
    ("lead@acme-labs.com", "Leo Lead", ["LEAD"]),
    ("member@acme-labs.com", "Mia Member", ["MEMBER"]),
    ("viewer@acme-labs.com", "Victor Viewer", ["VIEWER"]),
]


def load_env() -> dict[str, str]:
    values = dict(os.environ)
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values.setdefault(key.strip(), value.strip().strip('"'))
    return values


def post(url: str, payload: dict, token: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Bootstrap-Token": token,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            return exc.code, json.loads(body or b"{}")
        except json.JSONDecodeError:
            return exc.code, {"raw": body.decode(errors="replace")}


def get_json(url: str, token: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "X-Bootstrap-Token": token,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            return exc.code, json.loads(body or b"{}")
        except json.JSONDecodeError:
            return exc.code, {"raw": body.decode(errors="replace")}


def main() -> int:
    env = load_env()
    token = env.get("BOOTSTRAP_TOKEN", "")
    if not token or token.startswith("change-me"):
        # The default value is intentionally allowed in local development.
        token = token or "dev-bootstrap-token-change-me"

    core = env.get("CORE_INTERNAL_URL", "http://localhost:8002")
    iam = env.get("IAM_INTERNAL_URL", "http://localhost:8001")

    status, body = get_json(f"{core}/internal/tenants/by-slug/acme-labs", token)
    if status == 200:
        tenant_id = body["data"]["id"]
        print(f"tenant already exists: {tenant_id}")
    else:
        status, body = post(
            f"{core}/internal/tenants",
            {
                "name": "Acme Labs",
                "slug": "acme-labs",
                "plan_code": "TEAM",
                "modules": ["TASK_MGMT", "MONITORING", "REPORTS"],
                "settings": {
                    "timezone": "Asia/Colombo",
                    "privacy_window_hours": 24,
                    "screenshot_interval_min": 5,
                    "screenshot_interval_max": 10,
                },
            },
            token,
        )
        if status >= 300:
            print(f"tenant provisioning failed ({status}): {body}", file=sys.stderr)
            return 1
        tenant_id = body["data"]["id"]
        print(f"tenant: {tenant_id}")

    status, body = post(f"{iam}/internal/tenants/{tenant_id}/bootstrap", {}, token)
    if status >= 300:
        print(f"role bootstrap failed ({status}): {body}", file=sys.stderr)
        return 1
    print(f"roles: {', '.join(role['code'] for role in body['data'])}")

    for email, name, roles in USERS:
        status, body = post(
            f"{iam}/internal/users/bootstrap",
            {
                "tenant_id": tenant_id,
                "email": email,
                "full_name": name,
                "password": PASSWORD,
                "role_codes": roles,
            },
            token,
        )
        if status >= 300:
            print(f"user {email} failed ({status}): {body}", file=sys.stderr)
            return 1
        print(f"user: {email}  roles={','.join(roles)}")

    print("")
    print("Demo credentials (local only)")
    print(f"  password: {PASSWORD}")
    for email, _, roles in USERS:
        print(f"  {email:24} {roles[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
