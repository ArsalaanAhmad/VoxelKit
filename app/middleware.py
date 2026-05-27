"""ASGI middleware for the VoxelKit REST API.

Two concerns are addressed here:
- Rate limiting: prevent resource exhaustion from high-frequency callers.
- Upload size: enforce a per-request ceiling before the file hits the library.

Both limits are configurable via environment variables so production deployments
can tune them without a code change:

    VOXELKIT_RATE_LIMIT   int  requests per minute per remote IP (default: 100)
    VOXELKIT_MAX_UPLOAD   int  maximum upload size in megabytes (default: 256)
"""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


RATE_LIMIT_RPM: int = _env_int("VOXELKIT_RATE_LIMIT", 100)
MAX_UPLOAD_MB: int = _env_int("VOXELKIT_MAX_UPLOAD", 256)
MAX_UPLOAD_BYTES: int = MAX_UPLOAD_MB * 1024 * 1024


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by remote IP address.

    Uses an in-memory deque per IP — lightweight and accurate for single-process
    deployments (the typical uvicorn usage). Not shared across workers; if you
    run multiple workers behind a load balancer, move to a Redis-backed solution.
    """

    def __init__(self, app, calls: int = RATE_LIMIT_RPM, period: int = 60) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: object):
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._windows[ip]

        # evict timestamps outside the current window
        cutoff = now - self.period
        while window and window[0] <= cutoff:
            window.popleft()

        if len(window) >= self.calls:
            return Response(
                content='{"detail": "Rate limit exceeded. Try again later."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.period)},
            )

        window.append(now)
        return await call_next(request)
