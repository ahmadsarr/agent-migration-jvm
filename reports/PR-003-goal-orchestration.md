# PR 3 — Goal orchestration contract

## Goal
Define the durable state, evidence and authorization contract connecting audit, compatibility decision, planning, application and validation.

## Implemented
- JSON Schema for migration state
- Target-project state template with five goals
- Workflow and reconciliation rules
- Canonical skill updated with orchestration instructions

## Acceptance checks
| Check | Result | Evidence |
|---|---|---|
| Files persisted in feature branch | PASS | GitHub API writes |
| JSON Schema validation | NOT RUN | Requires execution |
| CLI adapter parity | NOT RUN | No generated adapters yet |
| Resume/reconciliation integration test | NOT RUN | Executor not implemented |
| Real migration workflow | NOT RUN | No target project selected |

## Risk
This MR defines the contract, **not an autonomous orchestrator**. State transitions and Git reconciliation require an implementation and tests.

## Next
Review contract and implement executor only after this MR is approved and merged.
