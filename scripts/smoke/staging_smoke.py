#!/usr/bin/env python3
"""Post-deploy smoke check for a staging URL.

Environment:
  BASE_URL        API gateway base, e.g. https://staging.neatsprint.example/api/v1
  WEB_URL         web origin, e.g. https://staging.neatsprint.example
  SMOKE_EMAIL     a seeded smoke user
  SMOKE_PASSWORD  its password

Exits non-zero on the first failed check. No credentials are stored in the repo.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1").rstrip("/")
API_ORIGIN = BASE[: -len("/api/v1")] if BASE.endswith("/api/v1") else BASE
WEB = os.environ.get("WEB_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.environ.get("SMOKE_EMAIL", "owner@acme-labs.com")
PASSWORD = os.environ.get("SMOKE_PASSWORD", "")

failures: list[str] = []


def call(method: str, path: str, body: dict | None = None, token: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    url = path if path.startswith("http") else BASE + path
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read()
            try:
                return response.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return response.status, {"raw": raw.decode(errors="replace")}
    except urllib.error.HTTPError as exc:
        return exc.code, {}
    except OSError as exc:
        return 0, {"error": str(exc)}


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("ok   " if ok else "fail ") + name + (f" ({detail})" if detail else ""))
    if not ok:
        failures.append(name)


status, body = call("GET", API_ORIGIN + "/ping")
check("api ping", status == 200, str(status))

if not PASSWORD:
    check("login", False, "SMOKE_PASSWORD is not set")
    token = None
else:
    status, body = call("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
    check("login", status == 200, str(status))
    token = body.get("data", {}).get("access_token") if status == 200 else None

if token:
    for path, name in [
        ("/tasks/projects", "projects"),
        ("/work/timesheet", "timesheet"),
        ("/teams", "teams"),
        ("/reports/time", "reports"),
    ]:
        status, _ = call("GET", path, token=token)
        check(name, status == 200, str(status))

try:
    with urllib.request.urlopen(WEB + "/login", timeout=15) as response:
        check("web login page", response.status == 200, str(response.status))
except OSError as exc:
    check("web login page", False, str(exc))

if failures:
    print(f"\n{len(failures)} check(s) failed: {', '.join(failures)}")
    sys.exit(1)
print("\nstaging smoke passed")
