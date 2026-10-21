# Targeted JVM regression workflow — implementation report

- Goal ID: TOOLKIT-REGRESSION-001
- Objective: guide the coding assistant to add only missing tests for concrete
  critical dependency/JDK migration risks and retain before/after evidence.
- Branch: `feature/05-targeted-jvm-regressions`
- Base: `master` at `eb7564df73e57bf874767998872adb9f479ec6e8`
- Status: implementation and local distribution checks completed; ready for review.
- Environment: managed Linux workspace, Python 3.12, Bash, Git and jsonschema 4.26.

## Changes and actions
- Added a targeted-regressions workflow and report template to the canonical,
  Codex and Claude skills. The workflow traces actual usages, inspects assertions,
  reuses sufficient coverage and adds tests only for demonstrated gaps.
- Added generic and Claude regression command templates; connected planning and
  validation commands and all three skill entry points to the workflow.
- Added NOT_RUN starter criteria to the state template's plan and validation
  goals and baseline-test preparation to the apply actions. The schema is unchanged.
- Extended installer CI path filters to include modified skill and command content.
- Prepared this change independently of the still-open goal-executor PR #4.

## Verification and evidence
| Check / command | Result | Evidence |
|---|---|---|
| `bash -n scripts/install.sh tests/install-test.sh` | PASS | Exit 0 in local workspace |
| `bash tests/install-test.sh` | PASS | PASS for opencode, claude and codex; install/update/local-edit protection/uninstall exercised |
| Draft202012Validator schema check and state-template validation | PASS | Both completed without validation errors |
| Fresh installation into temporary projects for all three harnesses | PASS | Installed guides/templates matched canonical bytes; new relative guide links resolved; regression commands existed for OpenCode/Claude |
| `git diff --check` | PASS | No whitespace errors |
| ShellCheck | NOT_RUN | Tool not installed in local workspace |
| Command invocation in the three coding-assistant CLIs | NOT_RUN | No harness CLI invocation performed |
| Actual Java 11/target JDK application regression runs | NOT_RUN | No target application supplied; no application tests or results fabricated |

## Acceptance criteria
- PASS: the workflow requires a concrete risk-to-behavior-to-test mapping and reuse
  of adequate existing tests.
- PASS: equivalent baseline/target assertions and fixtures, actual test execution
  counts and evidence are required; unavailable runs remain NOT_RUN.
- PASS: each installer distributes the new workflow and report template, with
  command templates supplied where the installer supports commands.
- PASS: the updated state template remains compatible with the existing schema.

## Limits and recovery
These are executable-agent instructions and templates, not an automatic test
generator or runner. Their effectiveness on a real project and actual CLI discovery
remain to be validated. Existing checkpoint files are not automatically changed.
The existing executor is outside this change; no completion guarantees are claimed
beyond its separately reviewed implementation. Remove/revert this change to recover
the previous toolkit instructions; installed copies use the existing installer
update/uninstall workflow and its local-modification protection.

## Next goal and approval
Review the proposed change, then exercise the workflow on a selected JVM migration
batch with actual dependency versions and application tests. Merge approval is
pending; this report does not approve a target application's migration.
