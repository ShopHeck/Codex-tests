# Agentic Product Builder

A production-style multi-agent system that takes a high-level product idea and autonomously plans, designs, implements, tests, and evaluates a prototype.

## System Overview

### Agents and Responsibilities

1. **Orchestrator Agent** (`OrchestratorAgent`)
   - Accepts product idea input.
   - Breaks work into milestones.
   - Coordinates downstream agents.
   - Tracks status per milestone.
   - Handles retries and iterative loop control.

2. **Specification Agent** (`SpecificationAgent`)
   - Generates PRD, feature breakdown, user stories, API contract.
   - Records assumptions and constraints.
   - Flags missing requirements.

3. **Architecture Agent** (`ArchitectureAgent`)
   - Proposes architecture and folder structure.
   - Defines service boundaries.
   - Provides optional database schema.
   - Justifies architectural tradeoffs.

4. **Implementation Agent** (`ImplementationAgent`)
   - Produces prototype implementation files.
   - Follows architecture decisions.
   - Keeps modular file outputs.

5. **Testing Agent** (`TestingAgent`)
   - Performs verification checks equivalent to unit/integration validations.
   - Detects failures and emits structured failure reports.

6. **Evaluation Agent** (`EvaluationAgent`)
   - Scores code quality and maintainability.
   - Flags scalability and security risks.
   - Recommends refactoring opportunities.

## Architecture Requirements Mapping

- **Planning logic**: `SpecificationAgent`, `ArchitectureAgent`
- **Orchestration logic**: `OrchestratorAgent`
- **Implementation layer**: `ImplementationAgent`
- **Testing layer**: `TestingAgent`
- **Evaluation layer**: `EvaluationAgent`

The orchestration loop runs iterative cycles and can bounce between stages:
- failing tests return to implementation
- severe architecture risks can return to planning/architecture

## Observability and Logging

Structured logs capture:
- major decisions and events
- execution durations
- failure states

All logs are recorded as structured `AgentLogEntry` items in the shared `BuildContext`.

## How to Run

```bash
python -m src.main
```

## Example Output Bundle

The final report includes:
- final working prototype files
- test results summary
- risk assessment
- technical debt report
- suggested next iteration roadmap
- structured build summary (milestones, logs, artifacts)

## How This Scales to Enterprise Pipelines

This design scales by replacing in-process agents with distributed workers:

1. **Queue-backed execution**
   - Put milestones on Kafka/SQS/NATS queues.
   - Autoscale workers independently for planning, coding, testing.

2. **State persistence & replay**
   - Persist `BuildContext` to Postgres + object storage.
   - Allow pausing/resuming failed runs and full audit replay.

3. **Policy gates & governance**
   - Add org-wide security/compliance checks as mandatory gating agents.
   - Route approvals to humans for high-risk outputs.

4. **Model and tool routing**
   - Use smaller models for planning and larger models for code/eval.
   - Control cost and latency with dynamic routing policies.

5. **Parallel milestone fan-out**
   - Run independent feature workstreams concurrently.
   - Merge artifacts through a dependency-aware orchestrator graph (DAG).

## 3 High-Value Build Ideas for this System

1. **Internal Workflow App Generator**
   - Input: team ops pain point.
   - Output: lightweight internal web tool prototype + tests + risk scan.

2. **API Modernization Copilot**
   - Input: legacy endpoint spec.
   - Output: modernized service scaffold, contract tests, migration plan.

3. **Compliance-Ready Feature Factory**
   - Input: feature request + compliance profile.
   - Output: implementation + security controls + audit-ready docs.
