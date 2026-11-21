"""HTTP routes for __TITLE__.

Domain routes are added per milestone. Every protected route must declare a required
permission and a tenant scope (see docs/SECURITY.md).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/ping", tags=["platform"], summary="Service liveness echo")
async def ping() -> dict[str, Any]:
    return {"ping": "pong", "service": "__SERVICE__"}
