"""Logging and timing helpers for the multi-agent system."""

from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional

from .models import AgentLogEntry, BuildContext


class BuildLogger:
    """Centralized structured logger used by all agents."""

    def __init__(self, context: BuildContext):
        self.context = context

    def log(
        self,
        agent: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        self.context.logs.append(
            AgentLogEntry(
                timestamp=datetime.now(timezone.utc),
                agent=agent,
                event=event,
                details=details or {},
                duration_ms=duration_ms,
            )
        )

    @contextmanager
    def timed(self, agent: str, event: str, details: Optional[Dict[str, Any]] = None) -> Generator[None, None, None]:
        start = time.perf_counter()
        self.log(agent, f"{event}_started", details)
        try:
            yield
            elapsed = (time.perf_counter() - start) * 1000
            self.log(agent, f"{event}_completed", details, duration_ms=elapsed)
        except Exception as exc:  # intentionally broad for pipeline observability
            elapsed = (time.perf_counter() - start) * 1000
            payload = dict(details or {})
            payload["error"] = str(exc)
            self.log(agent, f"{event}_failed", payload, duration_ms=elapsed)
            raise
