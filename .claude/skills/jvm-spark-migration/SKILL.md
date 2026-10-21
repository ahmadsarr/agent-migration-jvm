---
name: jvm-spark-migration
description: Audit and guide Java 11 upgrades to Java 17, 21 or 25 for Java, Scala and Apache Spark applications. Use for JVM compatibility, migration planning, build changes, Spark runtime checks and regression validation; not for unrelated refactoring.
---
# JVM / Spark migration
Use this skill when migrating an existing Java 11 Spark/Scala application to a supported target JDK.
## Operating rules
1. First inspect the actual repository; do not guess versions or compatibility.
2. Collect Java, Scala, Spark, Maven/SBT/Gradle, connectors, plugins, transitive dependencies, JVM flags, Docker images, CI and driver/executor runtime details.
3. Read [compatibility reference](references/compatibility.md) and verify exact versions against official documentation. Do not treat a candidate JDK as supported until proven.
4. Establish a Java 11 baseline: build, tests, representative Spark batch/streaming workloads, latency, throughput, memory, GC and restart behavior where applicable.
5. Separate Java runtime upgrade, Spark/Scala upgrades, connector upgrades and unrelated refactoring into independent changes.
6. Use read-only inspection before proposing changes. Obtain explicit approval before edits, running risky tests, production actions or rollback.
7. Review checkpoint compatibility, serialization, Spark driver/executor versions and Kafka delivery semantics where applicable.
8. Report evidence for each result: command, exit status, logs, environment and comparison against baseline. Never claim checks were run unless they were.
## Stages
- **Audit**: inventory and unresolved facts.
- **Compatibility**: supported target JDK, version matrix and blockers.
- **Plan**: minimal, reversible batches and validation gates.
- **Apply**: one approved batch on a separate branch, no unrelated edits.
- **Validate**: regression tests, integration, streaming recovery, performance and Go/No-Go.
Use [validation reference](references/validation.md) for acceptance criteria.
## Outputs
Create or update assessment, plan and validation reports in the target repository only when approved. Always distinguish observed facts, documented support and assumptions.

## Goal-driven execution contract
A migration is a directed sequence of measurable goals. Each goal must declare: stable ID, objective, dependencies, preconditions, authorized actions, verifiable acceptance criteria, evidence, report path, rollback and approval gate.
State transitions: PENDING -> READY -> RUNNING -> VALIDATING -> COMPLETED. Other states: BLOCKED, FAILED, WAITING_APPROVAL. Only mark COMPLETED after all acceptance criteria pass AND the report is persisted.
At the start of each run, inspect prior reports and Git history, reconcile state, and select the next READY goal. Never blindly repeat destructive operations. Keep automation within authorized scope; request approval for edits, risky tests, merge, deployment and rollback.
Every attempted goal MUST generate a Markdown report, including failures and blockers, containing: goal ID, objective, status, environment, actions, changed files, executed commands and results, acceptance checks, evidence links, risks, next goal and PR URL if any. Mark unexecuted checks NOT RUN. If persistence fails, mark BLOCKED and retain the report for recovery. Do not fabricate results.
For repository changes, create a dedicated branch and reviewable PR with its report. Do not merge without explicit approval. A technical goal passing does not imply PR approval.
Use [goal protocol](references/goal-protocol.md) and [report template](references/report-template.md). Generate a final consolidated migration report only when all required goals and approval gates are satisfied.
