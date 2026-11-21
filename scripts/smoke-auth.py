#!/usr/bin/env python3
"""End-to-end smoke test for M1 auth, tenancy and RBAC.

Requires the local stack and seeded demo tenant (scripts/seed.py).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = "http://localhost:8000/api/v1"
PASSWORD = "NeatSprint!2026"


def call(method: str, path: str, payload: dict | None = None, token: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
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


def login(email: str) -> tuple[int, dict]:
    return call("POST", "/auth/login", {"email": email, "password": PASSWORD})


def check(label: str, condition: bool, detail: str = "") -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {label}{(' :: ' + detail) if not condition else ''}")
    return condition


def main() -> int:
    ok = True

    status, body = login("owner@acme-labs.com")
    ok &= check("owner login", status == 200, f"{status} {body}")
    if status != 200:
        return 1
    owner = body["data"]["access_token"]
    owner_refresh = body["data"]["refresh_token"]
    ok &= check("owner has OWNER role", "OWNER" in body["data"]["user"]["roles"])
    ok &= check(
        "owner has permission scope",
        "core:tenant:update" in body["data"]["user"]["permissions"],
    )

    status, body = call("GET", "/core/tenants/current", token=owner)
    ok &= check("tenant through gateway", status == 200, f"{status} {body}")
    if status == 200:
        ok &= check("tenant name", body["data"]["name"] == "Acme Labs")
        ok &= check("privacy window", body["data"]["settings"]["privacy_window_hours"] == 24)

    status, body = call("GET", "/auth/sessions", token=owner)
    ok &= check("sessions listed", status == 200 and len(body.get("data", [])) >= 1,
                f"{status} {body}")
    if status == 200:
        ok &= check("current session flagged", any(item["current"] for item in body["data"]))

    status, body = call("GET", "/core/tenants/current")
    ok &= check("unauthenticated request denied", status == 401, f"{status} {body}")

    status, body = login("viewer@acme-labs.com")
    ok &= check("viewer login", status == 200)
    viewer = body["data"]["access_token"] if status == 200 else ""
    status, body = call(
        "POST",
        "/iam/invitations",
        {"email": "blocked@acme-labs.com", "role_ids": []},
        token=viewer,
    )
    ok &= check("viewer cannot invite", status in (403, 422), f"{status} {body}")

    status, body = call("POST", "/auth/refresh", {"refresh_token": owner_refresh})
    ok &= check("refresh rotates", status == 200, f"{status} {body}")
    rotated = body["data"]["refresh_token"] if status == 200 else ""
    ok &= check("refresh token changed", rotated != owner_refresh)

    # Reusing the old refresh token must revoke the session family.
    status, body = call("POST", "/auth/refresh", {"refresh_token": owner_refresh})
    ok &= check("refresh reuse detected", status == 401, f"{status} {body}")

    # Fresh login for the invitation flow.
    status, body = login("owner@acme-labs.com")
    owner = body["data"]["access_token"] if status == 200 else ""

    status, body = call(
        "GET", "/iam/roles", token=owner
    )
    ok &= check("roles listed", status == 200, f"{status} {body}")
    roles = body.get("data", []) if status == 200 else []
    member_role = next((role for role in roles if role["code"] == "MEMBER"), None)
    ok &= check("MEMBER role present", member_role is not None)

    invite_email = f"new.hire.{uuid.uuid4().hex[:8]}@acme-labs.com"
    status, body = call(
        "POST",
        "/iam/invitations",
        {
            "email": invite_email,
            "role_ids": [member_role["id"]] if member_role else [],
        },
        token=owner,
    )
    ok &= check("invitation created", status == 201, f"{status} {body}")
    dev_token = body.get("data", {}).get("dev_token") if status == 201 else None

    if dev_token:
        status, accepted = call(
            "POST",
            "/iam/invitations/accept",
            {
                "token": dev_token,
                "full_name": "New Hire",
                "password": "AnotherGood9",
            },
        )
        ok &= check("invitation accepted", status == 201, f"{status} {accepted}")
        status, login_body = call(
            "POST", "/auth/login", {"email": invite_email, "password": "AnotherGood9"}
        )
        ok &= check("invited user can log in", status == 200, f"{status} {login_body}")
    else:
        ok &= check("dev invite token available", False, "email may be disabled")

    print("\nM1 smoke:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
