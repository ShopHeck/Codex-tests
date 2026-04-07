"""Build summary rendering utilities."""

from __future__ import annotations

from typing import Dict, List

from .models import BuildContext


def roadmap_suggestions() -> List[str]:
    """Suggested next-iteration roadmap items."""

    return [
        "Add distributed queue-backed orchestration with per-agent autoscaling.",
        "Introduce model routing (cheap planner model, strong implementation model).",
        "Persist artifacts and logs in a data store for auditability and replay.",
        "Enable policy-driven quality gates (security, linting, performance budgets).",
    ]


def render_build_summary(context: BuildContext) -> Dict[str, object]:
    """Package required output sections into one structure."""

    return {
        "final_working_prototype": context.implementation_files,
        "test_results_summary": context.test_report,
        "risk_assessment": context.risks,
        "technical_debt_report": context.technical_debt,
        "next_iteration_roadmap": roadmap_suggestions(),
        "structured_build_summary": context.to_summary(),
    }
