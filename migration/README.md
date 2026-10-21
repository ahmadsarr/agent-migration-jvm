# Goal orchestration contract

This directory contains **templates and schemas**, not a migration execution. Copy `migration/templates/state.json` into the target project's `migration/state.json` only with authorization.

## Target project layout

```
migration/
  state.json
  assessment.md
  compatibility.md
  plan.md
  reports/
  evidence/
```

## Workflow
1. **Audit**: record detected versions, exact sources and unknowns in assessment.md.
2. **Decide**: document target JDK candidates and Spark/Scala compatibility evidence in compatibility.md.
3. **Plan**: split changes into independently reversible batches with acceptance criteria in plan.md.
4. **Apply**: implement only a specifically approved batch on a dedicated branch.
5. **Validate**: compare against Java 11 baseline and record evidence-backed Go/No-Go.

## State and safety
- Before each run, compare `repository.head` and branch against Git, inspect report files and referenced evidence. A mismatch is a **reconciliation request**, never silent trust or silent overwrite.
- A goal becomes COMPLETED only when all criteria are PASS and its report exists in an authorized durable destination.
- Reports are allowed independently from source edits. A read-only audit may persist reports only to an authorized report destination, including an external artifact store.
- Missing authorization means WAITING_APPROVAL or BLOCKED; never infer authorization from an existing file.
- Evidence entries are file paths or immutable links with enough context to reproduce a check. Mark unexecuted checks NOT_RUN.
- State updates must follow successful report persistence; never mark COMPLETED first.
- The state file is a **checkpoint**, not an executor. CLI/tool adapters and runtime tests are required before claiming autonomous execution.

## Canonical source and harness adapters
The canonical skill is `skills/jvm-spark-migration/SKILL.md`. Harness copies must be generated or checked against it. Harness-specific commands and agents may add tool invocation syntax but must not change goal semantics or approval gates.
