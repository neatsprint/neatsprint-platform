#!/usr/bin/env python3
"""Scaffold a NeatSprint service from templates/service.

Usage:
    python scripts/new-service.py iam 8001 "IAM Service"

The target directory must exist (a fresh git clone of the service repository) and be
empty apart from README/LICENSE/.git.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "service"


def package_name(service: str) -> str:
    return "neatsprint_" + service.replace("-", "_")


def title_for(service: str, title: str | None) -> str:
    if title:
        return title
    return service.replace("-", " ").title() + " Service"


def copy_tree(src: Path, dst: Path, replacements: dict[str, str]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        name = item.name
        for old, new in replacements.items():
            name = name.replace(old, new)
        target = dst / name
        if item.is_dir():
            copy_tree(item, target, replacements)
        else:
            text = item.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            target.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("service", help="service slug, e.g. iam")
    parser.add_argument("port", help="host port used in docs, e.g. 8001")
    parser.add_argument("title", nargs="?", default=None)
    parser.add_argument("--target", default=None, help="target directory")
    args = parser.parse_args()

    replacements = {
        "__SERVICE__": args.service,
        "__PACKAGE__": package_name(args.service),
        "__TITLE__": title_for(args.service, args.title),
        "__PORT__": args.port,
    }

    target = Path(args.target) if args.target else ROOT / "services" / f"neatsprint-{args.service}"
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 1

    copy_tree(TEMPLATE, target, replacements)
    (target / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())

    lock = shutil.which("uv")
    if lock:
        subprocess.run([lock, "lock"], cwd=target, check=False, shell=False)
    else:
        print("uv not found; run `uv lock` manually", file=sys.stderr)

    print(f"scaffolded {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
