# Agent Migration JVM

A reusable, evidence-driven migration toolkit for **Java 11 → a verified supported JDK** (potential candidates include Java 17, 21 and 25), including Java, Scala and Apache Spark applications.

> **Status:** Skills, prompt commands, compatibility guidance, reports and a goal-state schema exist. The goal executor, automatic Git reconciliation and end-to-end CLI discovery are **not yet implemented or validated**. This is not a one-click production migration tool.

## What it does

The workflow answers three questions at every checkpoint: **Where are we? What evidence supports that status? What action is authorized next?**

| Stage | Deliverable | Gate |
|---|---|---|
| Audit | `migration/assessment.md`: detected versions, sources, unknowns | Evidence captured; no unauthorized source edits |
| Decide | `migration/compatibility.md`: candidate JDKs, Spark/Scala constraints, documented support | Compatibility claims verified |
| Plan | `migration/plan.md`: reversible batches, acceptance tests and rollback | Batch scope reviewed |
| Apply | Minimal diff on a dedicated branch | Explicit approval for that batch |
| Validate | Evidence-backed comparison against Java 11 baseline and Go/No-Go | Tests and report persisted |

The JDK version is **not selected in advance**. Check exact Spark, Scala, connectors, build plugins, runtime images and driver/executor requirements against authoritative sources.

## Manual harness installation (operator-run only)

**The operator installs the toolkit manually in a terminal, before launching an agent.** The agent must not invoke the installer, self-install, change harness configuration or silently update/uninstall its own skill. This separates environment provisioning from migration execution.

Requirements: a checkout of this repository, Bash, `sha256sum`, `find` and standard GNU utilities. Replace `/path/to/application` with an existing project directory.

```bash
git clone https://github.com/ahmadsarr/agent-migration-jvm.git
cd agent-migration-jvm

# Preview first: no changes
bash scripts/install.sh --harness opencode --target /path/to/application --dry-run

# Explicit operator action to install
bash scripts/install.sh --harness opencode --target /path/to/application
```

Select exactly one harness, or install them separately:

| Harness | Operator command | Destination |
|---|---|---|
| OpenCode | `bash scripts/install.sh --harness opencode --target /path/to/application` | `.opencode/skills/`, `.opencode/commands/` |
| Claude Code | `bash scripts/install.sh --harness claude --target /path/to/application` | `.claude/skills/`, `.claude/commands/`, `.claude/agents/` |
| Codex | `bash scripts/install.sh --harness codex --target /path/to/application` | `.agents/skills/` |

The operator also runs maintenance manually:

```bash
bash scripts/install.sh --harness opencode --target /path/to/application --action update --dry-run
bash scripts/install.sh --harness opencode --target /path/to/application --action update
bash scripts/install.sh --harness opencode --target /path/to/application --action uninstall --dry-run
bash scripts/install.sh --harness opencode --target /path/to/application --action uninstall
```

The installer checks for conflicting files before writing and tracks managed files and SHA-256 checksums in `.jvm-migration/<harness>.manifest`. Modified local files are protected. Review the preview and any reported conflicts; **do not instruct the agent to bypass them**. Filesystem failures and concurrent modifications still require care; CLI discovery has not been verified in all three real CLIs. See [installer details](docs/harness-installer-v2.md).

## Goal state, reports and evidence

The **target application** (not this toolkit repository) uses:

```text
migration/
  state.json
  assessment.md
  compatibility.md
  plan.md
  reports/
  evidence/
```

- `state.json` is a checkpoint of goals, dependencies, status, authorizations, report references and acceptance checks—not an authoritative record of what Git actually contains.
- Every attempted goal generates a report, including blocked or failed goals.
- `COMPLETED` requires a nonempty report reference, at least one acceptance check and all checks `PASS`. The future executor must also confirm the report exists and evidence is valid.
- Report persistence authorization is **separate** from authorization to edit source code. A read-only audit can write only to an explicitly approved report destination.
- Before continuing, compare saved state with Git HEAD/branch, reports and evidence. Stop on discrepancies; do not silently repair or advance state.
- An agent may propose actions and work within granted permissions, but **must not merge, deploy, roll back or expand an approved batch without explicit approval**.

See [goal orchestration contract](migration/README.md), [state schema](migration/schema/state.schema.json) and [state template](migration/templates/state.json). The template is an example, not evidence of a completed migration.

## Repository structure

```text
skills/jvm-spark-migration/     Canonical skill and migration instructions
.agents/skills/                Codex skill adapter
.claude/skills/                Claude Code skill adapter
.claude/commands/              Claude Code prompt commands
.claude/agents/                Claude Code subagent definitions
commands/                     Generic command prompts (also installed for OpenCode)
scripts/install.sh            Operator-run harness installer
tests/                        Installer checks
migration/schema/             Goal state JSON Schema
migration/templates/          Example initial state
reports/                      Toolkit development PR reports
```

Harness copies should preserve the canonical goal and authorization semantics; adapter parity is not yet automatically enforced.

## Development and validation

```bash
bash -n scripts/install.sh tests/install-test.sh
bash tests/install-test.sh
```

These tests exercise file installation behavior; they do not prove the skill was discovered or executed by OpenCode, Claude Code or Codex. Check actual CLI discovery separately before relying on the toolkit.

## Contribution workflow

Work on **one feature branch and one reviewable PR at a time**. Each PR includes a Markdown report with changes, commands actually executed, evidence, acceptance status, known gaps and next steps. Never merge without review and explicit approval.
