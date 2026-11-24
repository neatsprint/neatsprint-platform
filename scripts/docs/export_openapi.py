#!/usr/bin/env python3
"""Merge service OpenAPI documents into one reference file for Redoc."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

SERVICES = {
    "iam": 8001,
    "core": 8002,
    "task": 8003,
    "team": 8004,
    "worklog": 8005,
    "monitoring": 8006,
    "chat": 8007,
    "reports": 8008,
    "ai": 8009,
}
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "openapi.json"


def prefix_refs(value: object, service: str) -> object:
    if isinstance(value, dict):
        return {key: prefix_refs(item, service) for key, item in value.items()}
    if isinstance(value, list):
        return [prefix_refs(item, service) for item in value]
    if isinstance(value, str) and value.startswith("#/components/schemas/"):
        return value.replace(
            "#/components/schemas/", f"#/components/schemas/{service}."
        )
    return value


def main() -> None:
    merged = {
        "openapi": "3.1.0",
        "info": {
            "title": "NeatSprint API",
            "version": "1.0.0",
            "description": "Merged OpenAPI reference for every NeatSprint service.",
        },
        "servers": [{"url": "http://localhost:8000", "description": "Local gateway"}],
        "paths": {},
        "components": {"schemas": {}, "securitySchemes": {}},
        "tags": [],
    }
    for service, port in SERVICES.items():
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/openapi.json", timeout=5
            ) as response:
                spec = json.loads(response.read())
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"{service}: skipped ({exc})")
            continue
        for path, operations in spec.get("paths", {}).items():
            merged["paths"][path] = prefix_refs(operations, service)
        for name, schema in spec.get("components", {}).get("schemas", {}).items():
            merged["components"]["schemas"][f"{service}.{name}"] = prefix_refs(
                schema, service
            )
        merged["tags"].append({"name": service})
        print(f"{service}: {len(spec.get('paths', {}))} paths")
    OUTPUT.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
