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


def auth_call(
    method: str, url: str, token: str, payload: dict | None = None
) -> tuple[int, dict]:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read()
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            return exc.code, json.loads(body) if body else {}
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

    # ---- planning demo: team, project, backlog and sprint ----
    status, body = post(
        f"{env.get('GATEWAY_URL', 'http://localhost:8000')}/api/v1/auth/login",
        {"email": "owner@acme-labs.com", "password": PASSWORD},
        token,
    )
    if status != 200:
        print(f"planning seed skipped: owner login {status}", file=sys.stderr)
        return 0
    token = body["data"]["access_token"]
    gateway = env.get("GATEWAY_URL", "http://localhost:8000")

    status, teams = auth_call("GET", f"{gateway}/api/v1/teams", token)
    team = next((item for item in teams.get("data", []) if item["name"] == "Backend Squad"), None)
    if team is None:
        status, created = auth_call(
            "POST",
            f"{gateway}/api/v1/teams",
            token,
            {"name": "Backend Squad", "description": "Core services and platform"},
        )
        team = created.get("data")
        print(f"team: Backend Squad ({status})")

    status, users = auth_call("GET", f"{gateway}/api/v1/iam/users", token)
    team_users = [
        (prefix, role_in_team)
        for prefix, role_in_team in (
            ("manager@", "MEMBER"),
            ("lead@", "LEAD"),
            ("member@", "MEMBER"),
        )
    ]
    for prefix, role_in_team in team_users:
        user = next(
            (item for item in users.get("data", []) if item["email"].startswith(prefix)),
            None,
        )
        if team and user:
            auth_call(
                "POST",
                f"{gateway}/api/v1/teams/{team['id']}/members",
                token,
                {"user_id": user["id"], "role_in_team": role_in_team},
            )

    status, projects = auth_call("GET", f"{gateway}/api/v1/tasks/projects", token)
    project = next((item for item in projects.get("data", []) if item["key"] == "AUTH"), None)
    if project is None:
        status, created = auth_call(
            "POST",
            f"{gateway}/api/v1/tasks/projects",
            token,
            {
                "name": "Authentication",
                "key": "AUTH",
                "description": "Login, sessions and device binding",
            },
        )
        project = created.get("data")
        print(f"project: AUTH ({status})")
    project_id = project["id"]

    status, backlog = auth_call(
        "GET", f"{gateway}/api/v1/tasks/projects/{project_id}/backlog", token
    )
    if len(backlog.get("data", [])) < 5:
        demo_items = [
            ("Implement device-bound sessions", "HIGH", 5),
            ("Refresh-token rotation", "HIGH", 3),
            ("Google sign-in", "MEDIUM", 5),
            ("Password reset flow", "MEDIUM", 3),
            ("Audit log viewer", "LOW", 2),
        ]
        for title, priority, points in demo_items:
            auth_call(
                "POST",
                f"{gateway}/api/v1/tasks/backlog",
                token,
                {
                    "project_id": project_id,
                    "type": "TASK",
                    "title": title,
                    "priority": priority,
                    "estimate_points": points,
                },
            )
        print(f"backlog: {len(demo_items)} items")

    status, sprints = auth_call(
        "GET", f"{gateway}/api/v1/tasks/sprints?project_id={project_id}", token
    )
    if not any(item["state"] == "ACTIVE" for item in sprints.get("data", [])):
        sprint_name = f"Sprint {len(sprints.get('data', [])) + 1}"
        status, sprint = auth_call(
            "POST",
            f"{gateway}/api/v1/tasks/sprints",
            token,
            {"project_id": project_id, "name": sprint_name, "goal": "Ship identity"},
        )
        if status == 201:
            _, items = auth_call(
                "GET", f"{gateway}/api/v1/tasks/projects/{project_id}/backlog", token
            )
            item_ids = [item["id"] for item in items.get("data", [])][:3]
            if item_ids:
                auth_call(
                    "POST",
                    f"{gateway}/api/v1/tasks/sprints/{sprint['data']['id']}/items",
                    token,
                    {"item_ids": item_ids},
                )
                auth_call(
                    "POST",
                    f"{gateway}/api/v1/tasks/sprints/{sprint['data']['id']}/start",
                    token,
                    {},
                )
            print(f"sprint: {sprint_name} (active)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
