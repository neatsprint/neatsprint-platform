#!/usr/bin/env python3
"""Cross-tenant isolation probe.

Creates (idempotently) a second tenant and checks that tenant A cannot read tenant B's
projects, items, teams or people through the public API. Intended for local/staging use.

Usage: python scripts/security/cross_tenant_probe.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8000")
CORE = os.environ.get("CORE_INTERNAL_URL", "http://localhost:8002")
IAM = os.environ.get("IAM_INTERNAL_URL", "http://localhost:8001")
TOKEN = os.environ.get("BOOTSTRAP_TOKEN", "dev-bootstrap-token-change-me")
PASSWORD = "NeatSprint!2026"
BETA = {
    "name": "Beta Labs",
    "slug": "beta-labs",
    "email": "owner@beta-labs.com",
}


def call(method: str, url: str, body: dict | None = None, token: str | None = None,
         bootstrap: bool = False) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if bootstrap:
        headers["X-Bootstrap-Token"] = TOKEN
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            return exc.code, json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return exc.code, {"raw": raw.decode(errors="replace")}


def login(email: str) -> tuple[str, str]:
    status, body = call(
        "POST", f"{GATEWAY}/api/v1/auth/login", {"email": email, "password": PASSWORD}
    )
    if status != 200:
        raise SystemExit(f"login failed for {email}: {status} {body}")
    return body["data"]["access_token"], body["data"]["user"]["tenant_id"]


def provision_beta() -> tuple[str, str]:
    status, body = call(
        "GET", f"{CORE}/internal/tenants/by-slug/{BETA['slug']}", bootstrap=True
    )
    if status == 200:
        tenant_id = body["data"]["id"]
    else:
        status, body = call(
            "POST",
            f"{CORE}/internal/tenants",
            {
                "name": BETA["name"],
                "slug": BETA["slug"],
                "plan_code": "TEAM",
                "modules": ["TASK_MGMT", "MONITORING", "REPORTS"],
                "settings": {"timezone": "UTC", "week_start": "MONDAY"},
            },
            bootstrap=True,
        )
        if status not in (200, 201):
            raise SystemExit(f"tenant provision failed: {status} {body}")
        tenant_id = body["data"]["id"]
    call("POST", f"{IAM}/internal/tenants/{tenant_id}/bootstrap", bootstrap=True)
    call(
        "POST",
        f"{IAM}/internal/users/bootstrap",
        {
            "tenant_id": tenant_id,
            "email": BETA["email"],
            "full_name": "Beta Owner",
            "password": PASSWORD,
            "role_codes": ["OWNER"],
        },
        bootstrap=True,
    )
    return tenant_id, login(BETA["email"])[0]


def ensure_beta_data(token: str) -> tuple[str, str, str, str]:
    _, projects = call("GET", f"{GATEWAY}/api/v1/tasks/projects", token=token)
    project = next(
        (item for item in projects.get("data", []) if item["key"] == "BETA"), None
    )
    if project is None:
        status, body = call(
            "POST",
            f"{GATEWAY}/api/v1/tasks/projects",
            {"name": "Beta Project", "key": "BETA", "description": "Isolation probe"},
            token,
        )
        if status not in (200, 201):
            raise SystemExit(f"project create failed: {status} {body}")
        project = body["data"]
    _, backlog = call(
        "GET", f"{GATEWAY}/api/v1/tasks/projects/{project['id']}/backlog", token=token
    )
    if backlog.get("data"):
        item = backlog["data"][0]
    else:
        status, body = call(
            "POST",
            f"{GATEWAY}/api/v1/tasks/backlog",
            {"project_id": project["id"], "type": "TASK", "title": "Beta secret"},
            token,
        )
        item = body["data"]
    _, teams = call("GET", f"{GATEWAY}/api/v1/teams", token=token)
    team = next((row for row in teams.get("data", []) if row["name"] == "Beta Team"), None)
    if team is None:
        status, body = call(
            "POST",
            f"{GATEWAY}/api/v1/teams",
            {"name": "Beta Team", "description": "Isolation probe"},
            token,
        )
        team = body["data"]
    return project["id"], item["id"], team["id"], BETA["email"]


def main() -> int:
    beta_tenant, beta_token = provision_beta()
    project_id, item_id, team_id, beta_email = ensure_beta_data(beta_token)
    alpha_token, alpha_tenant = login("owner@acme-labs.com")
    _, alpha_projects = call(
        "GET", f"{GATEWAY}/api/v1/tasks/projects", token=alpha_token
    )
    alpha_project = next(
        row for row in alpha_projects["data"] if row["key"] == "AUTH"
    )
    _, beta_users = call(
        "GET", f"{GATEWAY}/api/v1/iam/users", token=beta_token
    )
    beta_user = next(
        row["id"] for row in beta_users["data"] if row["email"] == beta_email
    )

    checks = [
        ("project read", f"{GATEWAY}/api/v1/tasks/projects/{project_id}", alpha_token, 404),
        (
            "project backlog",
            f"{GATEWAY}/api/v1/tasks/projects/{project_id}/backlog",
            alpha_token,
            404,
        ),
        ("item read", f"{GATEWAY}/api/v1/tasks/backlog/{item_id}", alpha_token, 404),
        ("team read", f"{GATEWAY}/api/v1/teams/{team_id}", alpha_token, 404),
        ("team members", f"{GATEWAY}/api/v1/teams/{team_id}/members", alpha_token, 404),
        ("user read", f"{GATEWAY}/api/v1/iam/users/{beta_user}", alpha_token, 404),
        (
            "alpha project via beta",
            f"{GATEWAY}/api/v1/tasks/projects/{alpha_project['id']}",
            beta_token,
            404,
        ),
    ]
    failed = 0
    for label, url, token, expected in checks:
        status, _ = call("GET", url, token=token)
        ok = status == expected
        failed += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} {label}: {status} (expected {expected})")

    status, sheet = call(
        "GET",
        f"{GATEWAY}/api/v1/work/timesheet?user_id={beta_user}",
        token=alpha_token,
    )
    rows = sheet.get("data", {}).get("entries", []) if status == 200 else []
    ok = status == 200 and rows == []
    failed += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} beta timesheet via alpha: {status}, {len(rows)} rows")

    print(f"\ntenants: alpha={alpha_tenant} beta={beta_tenant}")
    print(f"result: {'PASS' if failed == 0 else f'{failed} FAILED'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
