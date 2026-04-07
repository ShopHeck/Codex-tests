"""Shared data models for the multi-agent build system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """Lifecycle status for milestones and agent tasks."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Milestone:
    """Discrete unit of work derived from a product idea."""

    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    max_retries: int = 2
    notes: List[str] = field(default_factory=list)


@dataclass
class AgentLogEntry:
    """Structured log entry for observability."""

    timestamp: datetime
    agent: str
    event: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None


@dataclass
class BuildArtifact:
    """Captures generated text artifacts for planning and architecture."""

    name: str
    content: str


@dataclass
class BuildContext:
    """Central state shared across agents."""

    product_idea: str
    milestones: List[Milestone] = field(default_factory=list)
    artifacts: Dict[str, BuildArtifact] = field(default_factory=dict)
    implementation_files: Dict[str, str] = field(default_factory=dict)
    test_report: Dict[str, Any] = field(default_factory=dict)
    evaluation_report: Dict[str, Any] = field(default_factory=dict)
    technical_debt: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    iteration_logs: List[Dict[str, Any]] = field(default_factory=list)
    logs: List[AgentLogEntry] = field(default_factory=list)

    def add_artifact(self, name: str, content: str) -> None:
        self.artifacts[name] = BuildArtifact(name=name, content=content)

    def to_summary(self) -> Dict[str, Any]:
        """Return a structured summary suitable for build output."""

        return {
            "idea": self.product_idea,
            "milestones": [
                {
                    "name": m.name,
                    "status": m.status.value,
                    "attempts": m.attempts,
                    "notes": m.notes,
                }
                for m in self.milestones
            ],
            "artifacts": list(self.artifacts.keys()),
            "generated_files": list(self.implementation_files.keys()),
            "test_report": self.test_report,
            "evaluation_report": self.evaluation_report,
            "technical_debt": self.technical_debt,
            "risks": self.risks,
            "iterations": self.iteration_logs,
            "log_count": len(self.logs),
        }
