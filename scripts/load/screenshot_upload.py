#!/usr/bin/env python3
"""Measure screenshot upload latency against the local stack.

Creates a work session, registers a device, starts monitoring, uploads 1 MiB PNGs
and cleans up. Prints per-upload milliseconds and p50/p95.
"""

from __future__ import annotations

import json
import statistics
import time
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime

API = "http://localhost:8000/api/v1"
EMAIL = "owner@acme-labs.com"
PASSWORD = "NeatSprint!2026"
UPLOADS = 5
SIZE = 1024 * 1024


def call(method: str, path: str, body: dict | None = None, token: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw) if raw else {}


def upload(token: str, session_id: str, device_id: str, payload: bytes) -> tuple[int, bytes]:
    boundary = "----neatsprint" + uuid.uuid4().hex
    fields = {
        "session_id": session_id,
        "device_id": device_id,
        "captured_at": datetime.now(UTC).isoformat(),
        "width": "1920",
        "height": "1080",
        "display_index": "0",
    }
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
        )
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="shot.png"\r\n'
            "Content-Type: image/png\r\n\r\n"
        ).encode()
    )
    parts.append(payload)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    request = urllib.request.Request(
        API + "/monitor/screenshots",
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def main() -> None:
    token = call("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})[1]["data"][
        "access_token"
    ]
    projects = call("GET", "/tasks/projects", token=token)[1]["data"]
    project = next(project for project in projects if project["key"] == "AUTH")

    status, body = call(
        "POST", "/work/start", {"project_id": project["id"], "comment": "load probe"}, token
    )
    if status == 409:
        work = call("GET", "/work/current", token=token)[1]["data"]
        work_id = work["id"] if "id" in work else work["session"]["id"]
    else:
        work_id = body["data"]["id"]

    status, body = call(
        "POST",
        "/monitor/devices",
        {
            "name": "load-probe",
            "platform": "WINDOWS",
            "public_key": "load-probe-public-key-" + "x" * 48,
        },
        token,
    )
    device_id = body["data"]["id"]

    status, body = call(
        "POST",
        "/monitor/sessions/start",
        {"work_session_id": work_id, "device_id": device_id},
        token,
    )
    session_id = body["data"]["id"]

    timings: list[float] = []
    for index in range(UPLOADS):
        payload = b"\x89PNG\r\n\x1a\n" + bytes([index]) * (SIZE - 8)
        start = time.perf_counter()
        status, raw = upload(token, session_id, device_id, payload)
        elapsed = (time.perf_counter() - start) * 1000
        if status != 201:
            print("upload failed", status, raw[:200])
            break
        timings.append(elapsed)
        print(f"upload {index + 1}: {elapsed:.0f} ms")

    if timings:
        ordered = sorted(timings)
        p95 = ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]
        print(f"n={len(timings)} p50={statistics.median(timings):.0f} ms p95={p95:.0f} ms")

    call("POST", f"/monitor/sessions/{session_id}/stop", {}, token)
    call("POST", "/work/stop", {"elapsed_seconds": 1}, token)


if __name__ == "__main__":
    main()
