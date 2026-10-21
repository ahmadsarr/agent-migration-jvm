# Targeted JVM regression report — <batch / goal ID>

Status: NOT_RUN

## Scope and authorization
- Batch / goal ID:
- Source revision and JDK:
- Target revision and JDK:
- Dependency changes (exact old/new versions, including relevant transitives):
- Test edits and execution authorization:
- Authorized report destination:

## Impact and coverage
| Risk ID | Dependency / JDK change | Call site and source evidence | Expected application behavior and authority | Existing test / assertions | Gap and selected test change, or reuse rationale |
|---|---|---|---|---|---|

## Test changes
- Files and test selectors:
- Fixtures, isolated services and configuration:
- New or extended tests and the risk each protects:
- Any baseline/target adapter differences and equivalence rationale:

## Before / after execution
Record one pair per selected check. Log paths or immutable references must resolve
to the actual run. Keep an unexecuted check NOT_RUN and leave its exit code unset.

| Risk ID / test selector | Environment (baseline / target) | Revision, JDK and dependency versions | Exact command | Discovered / executed / skipped counts | Exit code | PASS / FAIL / NOT_RUN | Evidence |
|---|---|---|---|---|---|---|---|

## Differences and remaining gaps
- Observed behavior changes and their impact:
- Intentional differences, contract rationale and approval reference:
- Baseline failures, unavailable environments and unexecuted checks:
- Uncovered critical risks and next action:

## Decision
- GO / NO_GO (default NO_GO until mandatory checks and report persistence pass):
- Evidence-backed rationale:
- Rollback prerequisites:
- Branch / PR and next goal:

## Checkpoint linkage
Record the report path and one acceptance result per required check in the existing
validation goal. Evidence fields are arrays, for example:
`{"criterion":"RISK-001 contract preserved","result":"NOT_RUN","evidence":[]}`.
Do not populate PASS or evidence paths until execution and persistence are verified.
