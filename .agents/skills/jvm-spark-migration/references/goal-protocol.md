# Goal protocol
## Example goal definition (illustrative YAML)
```yaml
id: GOAL-001
objective: Inventory the current Java 11 Spark/Scala environment with evidence
dependencies: []
preconditions:
  - Repository accessible
actions:
  - Inspect build, dependency and deployment configuration (read-only)
acceptance_criteria:
  - Java, Scala, Spark and build versions recorded or explicitly unknown
  - Driver and executor JDKs recorded or explicitly unknown
  - Evidence paths provided for each observed fact
evidence: []
report_path: migration/reports/GOAL-001.md
rollback: Not applicable (read-only)
approval_required: false
status: PENDING
```
## State transitions
PENDING -> READY when prerequisites met; READY -> RUNNING on start; RUNNING -> VALIDATING after actions; VALIDATING -> COMPLETED only after verified criteria and persisted report. Use BLOCKED for missing permissions, evidence or report persistence; FAILED for a verified execution failure; WAITING_APPROVAL for a human gate.
A report is mandatory for every attempted goal, including blocked/failed goals. Never assert completion before the report write is confirmed.
## Safety
Do not edit, deploy, merge or rollback without explicit authorization. Store execution evidence; separate observed, documented and assumed facts. Resume only idempotent operations after reconciling actual repository state.
