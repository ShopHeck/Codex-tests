"""CLI entrypoint for running the agentic product builder."""

from __future__ import annotations

import json

from src.agentic_builder import BuildConfig, OrchestratorAgent, render_build_summary


if __name__ == "__main__":
    idea = "AI-assisted product launch planner"
    orchestrator = OrchestratorAgent(BuildConfig(max_iterations=3, max_retries_per_milestone=2))
    context = orchestrator.build(product_idea=idea)
    summary = render_build_summary(context)
    print(json.dumps(summary, indent=2))
