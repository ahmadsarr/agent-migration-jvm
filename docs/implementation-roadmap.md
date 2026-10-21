# Skill foundation: JVM / Spark migration

This repository uses the Agent Skills SKILL.md convention. The first phase establishes a verifiable, read-only audit entry point.

## Scope
- Java 11 to a documented compatible target JDK.
- Java / Scala / Apache Spark, including driver and executor environments.
- Build and deployment compatibility.

## Non-goals for phase 1
- No automatic source code migration.
- No dependency upgrades.
- No production deployment.
- No autonomous agent execution.

## Acceptance criteria
1. A discoverable SKILL.md exists under .agents/skills/jvm-spark-migration/ and .claude/skills/jvm-spark-migration/.
2. The skill requires an actual repository audit before recommending a JDK.
3. Version compatibility claims require official evidence.
4. All edits and risky operations require explicit approval.
5. Java 11 baseline and streaming recovery are part of the validation design.

## Follow-up pull requests
- PR 2: audit command and evidence schema
- PR 3: compatibility matrix and sources
- PR 4: planning and change-application gates
- PR 5: validation, rollback and reviewer instructions

> Existing files on master are initial scaffolding. This PR documents and reviews the foundation; subsequent PRs will refine implementations individually.
