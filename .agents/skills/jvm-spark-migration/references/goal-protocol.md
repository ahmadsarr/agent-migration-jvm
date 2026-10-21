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
report_path: <authorized-report-destination>/GOAL-001.md
report_write_authorized: true # only after the destination is explicitly approved; independent of source edit permission
rollback: Not applicable (read-only)
approval_required: false
status: PENDING
```
## State transitions
PENDING -> READY when prerequisites met; READY -> RUNNING on start; RUNNING -> VALIDATING after actions; VALIDATING -> COMPLETED only after verified criteria and persisted report. Use BLOCKED for missing permissions, evidence or report persistence; FAILED for a verified execution failure; WAITING_APPROVAL for a human gate.
Report persistence authorization is independent from source edit approval. Read-only audit means no source/project edits; write only to an authorized report destination (including an external artifact store). If no destination is authorized, present the report and mark BLOCKED until approved. A report is mandatory for every attempted goal, including blocked/failed goals. Never assert completion before the report write is confirmed.
## Safety
Do not edit, deploy, merge or rollback without explicit authorization. Store execution evidence; separate observed, documented and assumed facts. Resume only idempotent operations after reconciling actual repository state.
