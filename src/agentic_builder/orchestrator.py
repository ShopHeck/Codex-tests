"""Orchestration logic for autonomous multi-agent product prototype builds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .agents import ArchitectureAgent, EvaluationAgent, ImplementationAgent, SpecificationAgent, TestingAgent
from .logging_utils import BuildLogger
from .models import BuildContext, Milestone, TaskStatus


@dataclass
class BuildConfig:
    max_iterations: int = 3
    max_retries_per_milestone: int = 2


class OrchestratorAgent:
    """Coordinates the full planning->implementation->verification lifecycle."""

    def __init__(self, config: BuildConfig | None = None):
        self.config = config or BuildConfig()

    def _plan_milestones(self, context: BuildContext) -> List[Milestone]:
        milestones = [
            Milestone("planning", "Generate requirements and feature plan", max_retries=self.config.max_retries_per_milestone),
            Milestone("architecture", "Define technical architecture and boundaries", max_retries=self.config.max_retries_per_milestone),
            Milestone("implementation", "Generate working prototype files", max_retries=self.config.max_retries_per_milestone),
            Milestone("testing", "Generate and execute validations", max_retries=self.config.max_retries_per_milestone),
            Milestone("evaluation", "Assess quality, risk, and debt", max_retries=self.config.max_retries_per_milestone),
        ]
        context.milestones = milestones
        return milestones

    def build(self, product_idea: str) -> BuildContext:
        context = BuildContext(product_idea=product_idea)
        logger = BuildLogger(context)

        spec_agent = SpecificationAgent("SpecificationAgent", logger)
        arch_agent = ArchitectureAgent("ArchitectureAgent", logger)
        impl_agent = ImplementationAgent("ImplementationAgent", logger)
        test_agent = TestingAgent("TestingAgent", logger)
        eval_agent = EvaluationAgent("EvaluationAgent", logger)

        self._plan_milestones(context)

        for iteration in range(1, self.config.max_iterations + 1):
            iteration_record: Dict[str, object] = {"iteration": iteration, "steps": []}

            # Planning milestone
            planning = context.milestones[0]
            planning.status = TaskStatus.IN_PROGRESS
            planning.attempts += 1
            spec_agent.run(context)
            planning.status = TaskStatus.SUCCESS
            iteration_record["steps"].append({"milestone": planning.name, "status": planning.status.value})

            # Architecture milestone
            architecture = context.milestones[1]
            architecture.status = TaskStatus.IN_PROGRESS
            architecture.attempts += 1
            arch_agent.run(context)
            architecture.status = TaskStatus.SUCCESS
            iteration_record["steps"].append({"milestone": architecture.name, "status": architecture.status.value})

            # Implementation milestone
            implementation = context.milestones[2]
            implementation.status = TaskStatus.IN_PROGRESS
            implementation.attempts += 1
            impl_agent.run(context)
            implementation.status = TaskStatus.SUCCESS
            iteration_record["steps"].append({"milestone": implementation.name, "status": implementation.status.value})

            # Testing milestone with failure feedback loop
            testing = context.milestones[3]
            testing.status = TaskStatus.IN_PROGRESS
            testing.attempts += 1
            test_report = test_agent.run(context)

            if test_report["status"] != "passed":
                testing.status = TaskStatus.FAILED
                testing.notes.extend(test_report.get("failed_checks", []))
                iteration_record["steps"].append(
                    {
                        "milestone": testing.name,
                        "status": testing.status.value,
                        "failed_checks": test_report.get("failed_checks", []),
                    }
                )
                if iteration < self.config.max_iterations:
                    implementation.status = TaskStatus.RETRYING
                    implementation.notes.append("Retry triggered by failing tests")
                    context.iteration_logs.append(iteration_record)
                    continue
                raise RuntimeError("Build failed after exhausting retries during testing")

            testing.status = TaskStatus.SUCCESS
            iteration_record["steps"].append({"milestone": testing.name, "status": testing.status.value})

            # Evaluation milestone; architecture issues can bounce to planning in next loop
            evaluation = context.milestones[4]
            evaluation.status = TaskStatus.IN_PROGRESS
            evaluation.attempts += 1
            evaluation_report = eval_agent.run(context)
            evaluation.status = TaskStatus.SUCCESS
            iteration_record["steps"].append({"milestone": evaluation.name, "status": evaluation.status.value})

            severe_arch_risk = any("bottleneck" in r for r in evaluation_report.get("scalability_risks", []))
            if severe_arch_risk and iteration < self.config.max_iterations:
                architecture.status = TaskStatus.RETRYING
                architecture.notes.append("Revisit architecture for scalability bottleneck")
                iteration_record["steps"].append(
                    {
                        "milestone": architecture.name,
                        "status": architecture.status.value,
                        "reason": "Scalability risk detected",
                    }
                )
                context.iteration_logs.append(iteration_record)
                continue

            context.iteration_logs.append(iteration_record)
            break

        return context
