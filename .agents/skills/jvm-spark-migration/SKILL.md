---
name: jvm-spark-migration
description: Audit and guide Java 11 upgrades to Java 17, 21 or 25 for Java, Spring/Spring Boot, Scala and Apache Spark applications. Use for JVM compatibility, migration planning, build changes, Spark runtime checks and regression validation; not for unrelated refactoring.
---
# JVM / Spring / Spark migration
Use this skill when migrating an existing Java 11 application (plain Java, Spring/Spring Boot or Spark/Scala) to a supported target JDK. Apply only the framework checks relevant to the detected application.
## Operating rules
1. First inspect the actual repository; do not guess versions or compatibility.
2. Collect Java, Scala, Spark, Maven/SBT/Gradle, connectors, plugins, transitive dependencies, JVM flags, Docker images, CI and driver/executor runtime details.
3. Read [compatibility reference](references/compatibility.md) and verify exact versions against official documentation. Do not treat a candidate JDK as supported until proven.
4. Establish a Java 11 baseline: build, tests, representative Spark batch/streaming workloads, latency, throughput, memory, GC and restart behavior where applicable.
5. Separate Java runtime upgrade, Spark/Scala upgrades, connector upgrades and unrelated refactoring into independent changes.
6. Use read-only inspection before proposing changes. Source/project edits, risky tests, production actions and rollback require explicit approval. Writing a report to an authorized report destination is a separate permission and does not count as modifying audited source files.
7. Review checkpoint compatibility, serialization, Spark driver/executor versions and Kafka delivery semantics where applicable.
8. Report evidence for each result: command, exit status, logs, environment and comparison against baseline. Never claim checks were run unless they were.
## Stages
- **Audit**: inventory and unresolved facts.
- **Compatibility**: supported target JDK, version matrix and blockers.
- **Plan**: minimal, reversible batches and validation gates.
- **Apply**: one approved batch on a separate branch, no unrelated edits.
- **Validate**: regression tests, integration, streaming recovery, performance and Go/No-Go.
Use [validation reference](references/validation.md) for acceptance criteria.
## Spring and Spring Boot
When Spring is detected, read [Spring migration](references/spring-migration.md).
Audit the actual framework/BOM, Security, Data/ORM and Cloud versions. Distinguish
a JDK-only upgrade from a framework major upgrade, verify the supported combination,
and select targeted startup, HTTP, security, persistence and serialization checks.
Spring-only applications do not require Spark or Scala validation.

## Targeted regression coverage
For each migration batch affecting critical dependencies or JDK-sensitive behavior,
use [targeted regressions](references/targeted-regressions.md). Trace actual usages,
inspect existing coverage and add or extend tests only for identified behavioral
gaps within the approved scope. Capture equivalent baseline and target results,
then persist the impact map and evidence using the
[regression report template](references/regression-report-template.md).
Missing mandatory runs and unresolved critical risks prevent Go; compilation alone
cannot close the validation goal. Preserve the evidence-array checkpoint format.
## Outputs
Persist reports to an explicitly authorized report destination (dedicated reports directory or external artifact store). Do not write to the audited repository during a read-only audit unless that destination has been separately authorized. Always distinguish observed facts, documented support and assumptions.

## Goal-driven execution contract
A migration is a directed sequence of measurable goals. Each goal must declare: stable ID, objective, dependencies, preconditions, authorized actions, verifiable acceptance criteria, evidence, report path, report_write_authorized, rollback and approval gate.
State transitions: PENDING -> READY -> RUNNING -> VALIDATING -> COMPLETED. Other states: BLOCKED, FAILED, WAITING_APPROVAL. Only mark COMPLETED after all acceptance criteria pass AND the report is persisted.
At the start of each run, inspect prior reports and Git history, reconcile state, and select the next READY goal. Never blindly repeat destructive operations. Keep automation within authorized scope; request approval for edits, risky tests, merge, deployment and rollback.
Every attempted goal MUST generate a Markdown report, including failures and blockers, containing: goal ID, objective, status, environment, actions, changed files, executed commands and results, acceptance checks, evidence links, risks, next goal and PR URL if any. Mark unexecuted checks NOT RUN. If persistence is not authorized or fails, mark BLOCKED and present the report for an approved destination; do not write to the audited repository. Do not fabricate results.
For repository changes, create a dedicated branch and reviewable PR with its report. Do not merge without explicit approval. A technical goal passing does not imply PR approval.
Use [goal protocol](references/goal-protocol.md) and [report template](references/report-template.md). Generate a final consolidated migration report only when all required goals and approval gates are satisfied.
