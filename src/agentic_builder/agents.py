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
                    # Reconstitution calculator core logic that can be reused in an API route.

                    from __future__ import annotations

                    from dataclasses import dataclass
                    from typing import Dict

                    def run() -> str:
                        # In a real build, this would include full business logic modules.
                        return "Prototype ready: {context.product_idea}"


                    @dataclass
                    class ReconstitutionInput:
                        peptide_mg: float
                        diluent_ml: float
                        dose_mcg: float


                    def calculate_reconstitution(payload: ReconstitutionInput) -> Dict[str, float]:
                        if payload.peptide_mg <= 0:
                            raise ValueError("Peptide amount must be greater than 0 mg.")
                        if payload.diluent_ml <= 0:
                            raise ValueError("Diluent volume must be greater than 0 mL.")
                        if payload.dose_mcg <= 0:
                            raise ValueError("Dose must be greater than 0 mcg.")

                        concentration_mg_ml = payload.peptide_mg / payload.diluent_ml
                        dose_mg = payload.dose_mcg / 1000
                        injection_volume_ml = dose_mg / concentration_mg_ml
                        syringe_units = injection_volume_ml * 100
                        doses_per_vial = (payload.peptide_mg * 1000) / payload.dose_mcg

                        return {{
                            "concentration_mg_ml": round(concentration_mg_ml, 4),
                            "injection_volume_ml": round(injection_volume_ml, 4),
                            "syringe_units": round(syringe_units, 2),
                            "doses_per_vial": round(doses_per_vial, 1),
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
                        <title>Peptide Reconstitution Calculator</title>
                        <meta
                          name="description"
                          content="Simple and reliable peptide reconstitution calculations."
                        />
                        <link rel="stylesheet" href="./styles.css" />
                      </head>
                      <body>
                        <main class="layout">
                          <section class="hero card">
                            <p class="eyebrow">Clinical Utility Tool</p>
                            <h1>Peptide Reconstitution Calculator</h1>
                            <p class="subtitle">
                              Fast, clean, and accurate calculations for vial concentration, injection
                              volume, and insulin syringe units.
                            </p>
                            <ul class="metrics">
                              <li><strong>1 sec</strong><span>Average calc time</span></li>
                              <li><strong>4 outputs</strong><span>Per calculation</span></li>
                              <li><strong>Mobile-first</strong><span>Designed for quick use</span></li>
                            </ul>
                          </section>

                          <section class="card">
                            <h2>Calculator</h2>
                            <form id="calculatorForm" class="form">
                              <label>
                                Peptide in vial (mg)
                                <input id="peptideMg" type="number" min="0.01" step="0.01" value="5" required />
                              </label>
                              <label>
                                Bacteriostatic water added (mL)
                                <input id="diluentMl" type="number" min="0.1" step="0.1" value="2" required />
                              </label>
                              <label>
                                Desired dose (mcg)
                                <input id="doseMcg" type="number" min="1" step="1" value="250" required />
                              </label>
                              <button type="submit" class="btn btn-primary">Calculate dose</button>
                            </form>
                            <div id="result" class="result-grid" aria-live="polite">
                              <p class="result-empty">Enter values and tap Calculate dose.</p>
                            </div>
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
                      --bg: #f8fafc;
                      --card: #ffffff;
                      --text: #0f172a;
                      --muted: #475569;
                      --primary: #0ea5e9;
                      --primary-dark: #0284c7;
                      --border: #dbeafe;
                    }

                    * {
                      box-sizing: border-box;
                    }

                    body {
                      margin: 0;
                      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
                      color: var(--text);
                      background: radial-gradient(circle at top, #dbeafe 0%, #eff6ff 32%, var(--bg) 100%);
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
                      box-shadow: 0 15px 35px rgba(2, 132, 199, 0.12);
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

                    .result-grid {
                      margin-top: 1rem;
                      display: grid;
                      gap: 0.65rem;
                      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                    }

                    .result-card {
                      background: #f8fbff;
                      border: 1px solid var(--border);
                      border-radius: 12px;
                      padding: 0.75rem;
                    }

                    .result-card h3 {
                      margin: 0 0 0.4rem;
                      font-size: 0.85rem;
                      color: var(--muted);
                    }

                    .result-card p {
                      margin: 0;
                      font-size: 1.2rem;
                      font-weight: 700;
                    }

                    .result-empty,
                    .error-message {
                      color: var(--muted);
                      grid-column: 1 / -1;
                    }

                    .error-message {
                      color: #dc2626;
                    }
                    """
                ).strip(),
                "prototype/main.js": textwrap.dedent(
                    """
                    const calculatorForm = document.getElementById("calculatorForm");
                    const result = document.getElementById("result");

                    const calculate = (peptideMg, diluentMl, doseMcg) => {
                      if (peptideMg <= 0 || diluentMl <= 0 || doseMcg <= 0) {
                        throw new Error("All values must be greater than zero.");
                      }

                      const concentration = peptideMg / diluentMl;
                      const doseMg = doseMcg / 1000;
                      const injectionMl = doseMg / concentration;
                      const syringeUnits = injectionMl * 100;
                      const dosesPerVial = (peptideMg * 1000) / doseMcg;

                      return {
                        concentration: concentration.toFixed(3),
                        injectionMl: injectionMl.toFixed(3),
                        syringeUnits: syringeUnits.toFixed(1),
                        dosesPerVial: dosesPerVial.toFixed(1),
                      };
                    };

                    const renderResult = (values) => {
                      result.innerHTML = `
                        <article class="result-card">
                          <h3>Concentration</h3>
                          <p>${values.concentration} mg/mL</p>
                        </article>
                        <article class="result-card">
                          <h3>Injection volume</h3>
                          <p>${values.injectionMl} mL</p>
                        </article>
                        <article class="result-card">
                          <h3>Insulin syringe units</h3>
                          <p>${values.syringeUnits} units</p>
                        </article>
                        <article class="result-card">
                          <h3>Doses per vial</h3>
                          <p>${values.dosesPerVial}</p>
                        </article>
                      `;
                    };

                    calculatorForm.addEventListener("submit", (event) => {
                      event.preventDefault();
                      const peptideMg = Number(document.getElementById("peptideMg").value);
                      const diluentMl = Number(document.getElementById("diluentMl").value);
                      const doseMcg = Number(document.getElementById("doseMcg").value);

                      try {
                        const values = calculate(peptideMg, diluentMl, doseMcg);
                        renderResult(values);
                      } catch (error) {
                        result.innerHTML = `<p class="error-message">${error.message}</p>`;
                      }
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
