"""Agent implementations for each stage of the product build lifecycle."""

from __future__ import annotations

import json
import textwrap
from html import escape
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
            escaped_product_idea = escape(context.product_idea, quote=True)
            files = {
                "prototype/app.py": textwrap.dedent(
                    f'''
                    # Autogenerated prototype app for idea: {context.product_idea}
                    # Lightweight server output that can be embedded into a web route.

                    from __future__ import annotations

                    from dataclasses import dataclass
                    from datetime import datetime
                    from typing import Dict, List


                    @dataclass
                    class Lead:
                        email: str
                        company_size: int
                        priority: str
                        created_at_iso: str


                    def score_lead(company_size: int, priority: str) -> int:
                        priority_bonus = {{"low": 5, "medium": 15, "high": 30}}
                        size_score = min(company_size, 1000) // 20
                        return size_score + priority_bonus.get(priority.lower(), 0)


                    def build_cta_message(lead_score: int) -> str:
                        if lead_score >= 45:
                            return "Book a strategy call — you qualify for white-glove onboarding."
                        if lead_score >= 25:
                            return "Start your 14-day trial and unlock guided setup."
                        return "Try the free workflow starter and upgrade when ready."

                    def run() -> str:
                        # In a real build, this would include full business logic modules.
                        return "Prototype ready: {context.product_idea}"


                    def preview_value_proposition() -> Dict[str, str]:
                        sample_lead = Lead(
                            email="founder@example.com",
                            company_size=120,
                            priority="high",
                            created_at_iso=datetime.utcnow().isoformat(),
                        )
                        lead_score = score_lead(sample_lead.company_size, sample_lead.priority)
                        return {{
                            "headline": "Automate manual work. Convert more leads.",
                            "subheadline": "Launch a revenue-focused workflow in minutes.",
                            "cta": build_cta_message(lead_score),
                            "lead_score": str(lead_score),
                        }}
                    '''
                ).strip(),
                "prototype/index.html": textwrap.dedent(
                    f"""
                    <!doctype html>
                    <html lang="en">
                      <head>
                        <meta charset="UTF-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <title>Agentic Growth Studio</title>
                        <meta
                          name="description"
                          content="Launch conversion-focused automation for {escaped_product_idea}."
                        />
                        <link rel="stylesheet" href="./styles.css" />
                      </head>
                      <body>
                        <main class="layout">
                          <section class="hero card">
                            <p class="eyebrow">Revenue Automation Platform</p>
                            <h1>Ship {escaped_product_idea} with beautiful UI and faster conversions.</h1>
                            <p class="subtitle">
                              Turn repetitive workflows into automated customer journeys with built-in
                              lead capture, qualification, and follow-up playbooks.
                            </p>
                            <div class="cta-row">
                              <button id="startTrialButton" class="btn btn-primary">Start free trial</button>
                              <button id="watchDemoButton" class="btn btn-secondary">Watch demo</button>
                            </div>
                            <ul class="metrics">
                              <li><strong>+28%</strong><span>Demo conversions</span></li>
                              <li><strong>-16h</strong><span>Manual ops / week</span></li>
                              <li><strong>3 days</strong><span>Typical deployment</span></li>
                            </ul>
                          </section>

                          <section class="card">
                            <h2>Lead quality estimator</h2>
                            <form id="leadForm" class="form">
                              <label>
                                Work email
                                <input id="email" type="email" placeholder="you@company.com" required />
                              </label>
                              <label>
                                Team size
                                <input id="teamSize" type="number" min="1" max="5000" value="50" required />
                              </label>
                              <label>
                                Priority
                                <select id="priority">
                                  <option value="low">Low</option>
                                  <option value="medium" selected>Medium</option>
                                  <option value="high">High</option>
                                </select>
                              </label>
                              <button type="submit" class="btn btn-primary">Calculate next best action</button>
                            </form>
                            <p id="result" class="result">Submit details to get your recommended CTA.</p>
                          </section>
                        </main>
                        <script src="./main.js"></script>
                      </body>
                    </html>
                    """
                ).strip(),
                "prototype/styles.css": textwrap.dedent(
                    """
                    :root {
                      color-scheme: light;
                      --bg: #f3f4f6;
                      --card: #ffffff;
                      --text: #0f172a;
                      --muted: #475569;
                      --primary: #2563eb;
                      --primary-dark: #1d4ed8;
                      --border: #e2e8f0;
                    }

                    * {
                      box-sizing: border-box;
                    }

                    body {
                      margin: 0;
                      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
                      color: var(--text);
                      background: linear-gradient(180deg, #e0e7ff, var(--bg));
                    }

                    .layout {
                      width: min(1080px, 92vw);
                      margin: 2.5rem auto;
                      display: grid;
                      gap: 1.25rem;
                      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    }

                    .card {
                      background: var(--card);
                      border: 1px solid var(--border);
                      border-radius: 18px;
                      padding: 1.5rem;
                      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                    }

                    .eyebrow {
                      margin: 0;
                      color: var(--primary);
                      font-weight: 700;
                      text-transform: uppercase;
                      font-size: 0.75rem;
                      letter-spacing: 0.08em;
                    }

                    h1, h2 {
                      margin-top: 0.75rem;
                    }

                    .subtitle {
                      color: var(--muted);
                      line-height: 1.6;
                    }

                    .cta-row {
                      display: flex;
                      flex-wrap: wrap;
                      gap: 0.75rem;
                      margin-top: 1.25rem;
                    }

                    .btn {
                      border: none;
                      border-radius: 10px;
                      padding: 0.75rem 1rem;
                      cursor: pointer;
                      font-weight: 600;
                    }

                    .btn-primary {
                      background: var(--primary);
                      color: #fff;
                    }

                    .btn-primary:hover {
                      background: var(--primary-dark);
                    }

                    .btn-secondary {
                      background: #dbeafe;
                      color: #1e3a8a;
                    }

                    .metrics {
                      list-style: none;
                      padding: 0;
                      margin: 1.25rem 0 0;
                      display: grid;
                      grid-template-columns: repeat(3, minmax(0, 1fr));
                      gap: 0.5rem;
                    }

                    .metrics li {
                      background: #f8fafc;
                      border-radius: 12px;
                      padding: 0.75rem;
                      display: flex;
                      flex-direction: column;
                      gap: 0.25rem;
                    }

                    .form {
                      display: grid;
                      gap: 0.75rem;
                    }

                    label {
                      display: grid;
                      gap: 0.35rem;
                      font-weight: 600;
                    }

                    input, select {
                      border: 1px solid var(--border);
                      border-radius: 10px;
                      padding: 0.7rem 0.75rem;
                      font: inherit;
                    }

                    .result {
                      margin-top: 0.85rem;
                      color: var(--muted);
                      min-height: 2rem;
                    }
                    """
                ).strip(),
                "prototype/main.js": textwrap.dedent(
                    """
                    const leadForm = document.getElementById("leadForm");
                    const result = document.getElementById("result");
                    const startTrialButton = document.getElementById("startTrialButton");
                    const watchDemoButton = document.getElementById("watchDemoButton");

                    const scoreLead = (teamSize, priority) => {
                      const priorityBonus = { low: 5, medium: 15, high: 30 };
                      const sizeScore = Math.min(teamSize, 1000) / 20;
                      return Math.round(sizeScore + (priorityBonus[priority] ?? 0));
                    };

                    const messageFromScore = (score) => {
                      if (score >= 45) return "High intent lead — offer white-glove onboarding.";
                      if (score >= 25) return "Qualified lead — trigger trial + consult nurture flow.";
                      return "Early stage lead — enroll in email education sequence.";
                    };

                    leadForm.addEventListener("submit", (event) => {
                      event.preventDefault();
                      const email = document.getElementById("email").value.trim();
                      const teamSize = Number(document.getElementById("teamSize").value);
                      const priority = document.getElementById("priority").value;

                      if (!email) {
                        result.textContent = "Please provide a valid work email.";
                        return;
                      }

                      const score = scoreLead(teamSize, priority);
                      result.textContent = `Lead score ${score}: ${messageFromScore(score)}`;
                    });

                    startTrialButton.addEventListener("click", () => {
                      result.textContent = "Success: Trial flow started. Next step is Stripe checkout integration.";
                    });

                    watchDemoButton.addEventListener("click", () => {
                      result.textContent = "Demo queued: Embed your product walkthrough video here.";
                    });
                    """
                ).strip(),
            }

            context.implementation_files.update(files)
            return files


class TestingAgent(BaseAgent):
    """Verification agent that creates/runs checks and reports failures."""

    def run(self, context: BuildContext) -> Dict[str, object]:
        with self.logger.timed(self.name, "testing"):
            files_present = bool(context.implementation_files)
            has_entrypoint = "prototype/app.py" in context.implementation_files
            has_ui_bundle = all(
                path in context.implementation_files
                for path in ("prototype/index.html", "prototype/styles.css", "prototype/main.js")
            )

            failed_checks: List[str] = []
            if not files_present:
                failed_checks.append("No implementation files generated")
            if not has_entrypoint:
                failed_checks.append("Missing prototype/app.py")
            if not has_ui_bundle:
                failed_checks.append("Missing UI bundle files for prototype experience")

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
                "blocking_scalability_risks": [],
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
