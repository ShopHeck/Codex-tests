from __future__ import annotations

import unittest

from src.agentic_builder import BuildConfig, OrchestratorAgent, render_build_summary


class OrchestratorTests(unittest.TestCase):
    def test_end_to_end_build_generates_required_outputs(self) -> None:
        orchestrator = OrchestratorAgent(BuildConfig(max_iterations=3, max_retries_per_milestone=1))
        context = orchestrator.build("Smart expense triage assistant")
        summary = render_build_summary(context)

        self.assertIn("prototype/app.py", summary["final_working_prototype"])
        self.assertEqual(summary["test_results_summary"]["status"], "passed")
        self.assertTrue(summary["risk_assessment"])
        self.assertTrue(summary["technical_debt_report"])
        self.assertTrue(summary["next_iteration_roadmap"])

    def test_specification_artifacts_exist(self) -> None:
        orchestrator = OrchestratorAgent()
        context = orchestrator.build("Customer success insights dashboard")

        self.assertIn("prd", context.artifacts)
        self.assertIn("feature_breakdown", context.artifacts)
        self.assertIn("user_stories", context.artifacts)
        self.assertIn("api_contract", context.artifacts)
        self.assertIn("missing_requirements", context.artifacts)

    def test_successful_build_stops_without_unnecessary_architecture_retries(self) -> None:
        orchestrator = OrchestratorAgent(BuildConfig(max_iterations=4, max_retries_per_milestone=1))
        context = orchestrator.build("Automated release notes writer")

        self.assertEqual(len(context.iteration_logs), 1)
        architecture_step = context.iteration_logs[0]["steps"][1]
        self.assertEqual(architecture_step["milestone"], "architecture")
        self.assertEqual(architecture_step["status"], "success")


if __name__ == "__main__":
    unittest.main()
