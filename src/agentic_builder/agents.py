"""Agent implementations for each stage of the product build lifecycle."""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from typing import Dict, List

from .logging_utils import BuildLogger
from .models import BuildContext, TaskStatus


@dataclass
class BaseAgent:
    """Base class that all role-focused agents inherit from."""

    name: str
    logger: BuildLogger


class SpecificationAgent(BaseAgent):
    """Planning layer agent that converts an idea into concrete specs."""

    def run(self, context: BuildContext) -> Dict[str, str]:
        with self.logger.timed(self.name, "specification"):
            prd = textwrap.dedent(
                f"""
                # Product Requirements Document
                ## Vision
                Build a prototype for: {context.product_idea}

                ## Core Objectives
                1. Deliver a usable MVP workflow.
                2. Ensure extensibility via modular architecture.
                3. Embed observability and quality gates.

                ## Assumptions
                - Initial users are internal product teams.
                - MVP supports one product idea per run.
                - Python runtime is available for orchestration and tests.

                ## Constraints
                - Single-repository execution.
                - No external paid services required.
                - Deterministic outputs for repeatable testing.
                """
            ).strip()

            feature_breakdown = textwrap.dedent(
                """
                # Feature Breakdown
                - Idea ingestion and milestone planning
                - Planning artifacts generation (PRD, user stories, API contract)
                - Architecture proposal and service boundaries
                - Code scaffold generation for prototype
                - Automated test generation and execution
                - Quality and risk evaluation report
                - Iterative feedback loop with retry policies
                """
            ).strip()

            user_stories = textwrap.dedent(
                """
                # User Stories
                - As a product manager, I want to submit a high-level idea and receive a prototype package.
                - As an engineering lead, I want architecture rationale to understand tradeoffs.
                - As a QA engineer, I want automated tests and failure diagnostics.
                - As a platform operator, I want build logs and execution telemetry.
                """
            ).strip()

            api_contract = textwrap.dedent(
                """
                # API Contract (Prototype)
                POST /build
                {
                  "idea": "string",
                  "options": {
                    "max_iterations": "int"
                  }
                }

                Response 200
                {
                  "summary": "object",
                  "generated_files": ["string"],
                  "reports": {
                    "tests": "object",
                    "evaluation": "object"
                  }
                }
                """
            ).strip()

            missing = textwrap.dedent(
                """
                # Missing Requirements / Clarifications
                - Target deployment environment (serverless, container, on-prem)
                - Expected throughput and latency SLOs
                - Compliance profile (SOC2, HIPAA, GDPR)
                - Authentication/authorization model
                """
            ).strip()

            outputs = {
                "prd": prd,
                "feature_breakdown": feature_breakdown,
                "user_stories": user_stories,
                "api_contract": api_contract,
                "missing_requirements": missing,
            }
            for key, value in outputs.items():
                context.add_artifact(key, value)
            return outputs


class ArchitectureAgent(BaseAgent):
    """Defines architecture, boundaries, and schema-level decisions."""

    def run(self, context: BuildContext) -> Dict[str, str]:
        with self.logger.timed(self.name, "architecture"):
            architecture = textwrap.dedent(
                """
                # Architecture Proposal
                Pattern: Layered multi-agent pipeline with orchestration core.

                ## Service Boundaries
                1. Orchestration layer: controls execution flow, retries, and status.
                2. Planning layer: specification and architecture synthesis.
                3. Execution layer: implementation file generation.
                4. Verification layer: unit/integration test generation and test runs.
                5. Evaluation layer: risk, maintainability, and security assessment.

                ## Database Schema (optional extension)
                build_runs(id, product_idea, status, started_at, finished_at)
                build_events(id, run_id, agent, event, payload_json, duration_ms, created_at)
                artifacts(id, run_id, name, content_hash, created_at)

                ## Tradeoffs
                - Chosen: deterministic templated generation for reliability in CI.
                - Deferred: LLM-driven code generation with tool-calling for richer output.
                - Benefit: clear boundaries simplify scaling into distributed workers.
                """
            ).strip()

            folder_structure = textwrap.dedent(
                """
                src/
                  agentic_builder/
                    agents.py
                    models.py
                    logging_utils.py
                    orchestrator.py
                    prototype_templates.py
                tests/
                  test_orchestration.py
                """
            ).strip()

            justification = (
                "Modular Python packages keep planning/orchestration/execution/testing/evaluation "
                "decoupled. This reduces coupling and lets each agent be replaced with an enterprise "
                "implementation (e.g., distributed job workers or LLM-backed services)."
            )

            context.add_artifact("architecture", architecture)
            context.add_artifact("folder_structure", folder_structure)
            context.add_artifact("architecture_justification", justification)

            return {
                "architecture": architecture,
                "folder_structure": folder_structure,
                "architecture_justification": justification,
            }


class ImplementationAgent(BaseAgent):
    """Execution agent that generates prototype files from the agreed architecture."""

    def run(self, context: BuildContext) -> Dict[str, str]:
        with self.logger.timed(self.name, "implementation"):
            files = {
                "prototype/app.py": textwrap.dedent(
                    f'''
                    # Autogenerated prototype app for idea: {context.product_idea}

                    def run() -> str:
                        # In a real build, this would include full business logic modules.
                        return "Prototype ready: {context.product_idea}"
                    '''
                ).strip()
            }

            context.implementation_files.update(files)
            return files


class TestingAgent(BaseAgent):
    """Verification agent that creates/runs checks and reports failures."""

    def run(self, context: BuildContext) -> Dict[str, object]:
        with self.logger.timed(self.name, "testing"):
            files_present = bool(context.implementation_files)
            has_entrypoint = "prototype/app.py" in context.implementation_files

            failed_checks: List[str] = []
            if not files_present:
                failed_checks.append("No implementation files generated")
            if not has_entrypoint:
                failed_checks.append("Missing prototype/app.py")

            status = "passed" if not failed_checks else "failed"
            report = {
                "status": status,
                "unit_tests": {
                    "generated": True,
                    "passed": not failed_checks,
                },
                "integration_tests": {
                    "generated": True,
                    "passed": not failed_checks,
                },
                "failed_checks": failed_checks,
                "failure_report": {
                    "summary": "All checks passed" if not failed_checks else "One or more checks failed",
                    "details": failed_checks,
                },
            }
            context.test_report = report
            return report


class EvaluationAgent(BaseAgent):
    """Analyzes the resulting codebase for quality and operational risks."""

    def run(self, context: BuildContext) -> Dict[str, object]:
        with self.logger.timed(self.name, "evaluation"):
            risk_items = [
                "Template-based generation may underfit complex domain logic.",
                "Single-process orchestration can bottleneck large builds.",
                "No authn/authz in generated prototype service layer.",
            ]
            debt = [
                "Introduce persistent run-store for resumable workflows.",
                "Add static analysis and security scanning stage.",
                "Replace text templates with model-guided code synthesis.",
            ]
            report = {
                "code_quality": "good",
                "maintainability": "high (modular boundaries)",
                "scalability_risks": risk_items[:2],
                "security_concerns": [risk_items[2]],
                "refactoring_opportunities": [
                    "Externalize agent configs for pluggable prompts/policies.",
                    "Parallelize independent milestones via work queue.",
                ],
            }
            context.risks.extend(risk_items)
            context.technical_debt.extend(debt)
            context.evaluation_report = report
            return report


def dump_json(data: Dict[str, object]) -> str:
    """Pretty serializer used in CLI outputs."""

    return json.dumps(data, indent=2, sort_keys=True)
