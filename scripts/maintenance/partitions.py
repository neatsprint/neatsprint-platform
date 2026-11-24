#!/usr/bin/env python3
"""Create upcoming Worklog monthly and Monitoring weekly partitions.

Usage:
    python scripts/maintenance/partitions.py

Environment:
    WORKLOG_DATABASE_URL  default postgresql://neatsprint:neatsprint@localhost:5432/db_worklog
    MONITORING_DATABASE_URL default .../db_monitoring
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, date, datetime, timedelta

import asyncpg

WORKLOG = os.environ.get(
    "WORKLOG_DATABASE_URL",
    "postgresql://neatsprint:neatsprint@localhost:5432/db_worklog",
)
MONITORING = os.environ.get(
    "MONITORING_DATABASE_URL",
    "postgresql://neatsprint:neatsprint@localhost:5432/db_monitoring",
)


def _dsn(value: str) -> str:
    return value.replace("postgresql+asyncpg://", "postgresql://")


def _month_bounds(start: date) -> tuple[date, date]:
    if start.month == 12:
        return start, date(start.year + 1, 1, 1)
    return start, date(start.year, start.month + 1, 1)


async def ensure_worklog() -> int:
    connection = await asyncpg.connect(_dsn(WORKLOG))
    created = 0
    try:
        today = datetime.now(tz=UTC).date().replace(day=1)
        for index in range(4):
            month = today
            for _ in range(index):
                month = _month_bounds(month)[1]
            start, end = _month_bounds(month)
            name = f"time_entries_{start.year}_{start.month:02d}"
            sql = (
                f"CREATE TABLE IF NOT EXISTS {name} PARTITION OF time_entries "
                f"FOR VALUES FROM ('{start}') TO ('{end}')"
            )
            try:
                await connection.execute(sql)
                created += 1
            except asyncpg.PostgresError as exc:
                print(f"worklog {name}: {exc}")
    finally:
        await connection.close()
    return created


async def ensure_monitoring() -> int:
    connection = await asyncpg.connect(_dsn(MONITORING))
    created = 0
    try:
        today = datetime.now(tz=UTC).date()
        monday = today - timedelta(days=today.weekday())
        for index in range(6):
            start = monday + timedelta(days=7 * index)
            end = start + timedelta(days=7)
            name = f"screenshots_{start.isoformat().replace('-', '_')}"
            sql = (
                f"CREATE TABLE IF NOT EXISTS {name} PARTITION OF screenshots "
                f"FOR VALUES FROM ('{start}') TO ('{end}')"
            )
            try:
                await connection.execute(sql)
                created += 1
            except asyncpg.PostgresError as exc:
                print(f"monitoring {name}: {exc}")
    finally:
        await connection.close()
    return created


async def main() -> None:
    worklog = await ensure_worklog()
    monitoring = await ensure_monitoring()
    print(f"worklog partitions ensured: {worklog}")
    print(f"monitoring partitions ensured: {monitoring}")


if __name__ == "__main__":
    asyncio.run(main())
