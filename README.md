# Agent Migration JVM

Toolkit for planning and validating migrations from Java 11 to a compatible target JDK for Java, Scala and Apache Spark applications.

## Workflow
1. Audit existing runtime, dependencies, Spark, Scala and build tooling.
2. Determine a supported target JDK from verified compatibility evidence.
3. Plan small reversible changes and identify behavioral risks in critical dependencies.
4. Reuse existing tests, add only approved missing regression tests, and capture the Java 11 baseline.
5. Apply only approved migration changes.
6. Compare baseline/target behavior and validate Spark streaming recovery, performance and deployment where relevant.

Canonical skill: `skills/jvm-spark-migration/SKILL.md` (mirrored for Codex and Claude Code). All copies share the goal execution and mandatory reporting contract. See `commands/` for generic templates and `.claude/commands/` for Claude-specific commands.

Command files are prompt templates; slash-command registration depends on the coding assistant.

## Targeted regression tests
Use the `regressions` command template for a selected migration batch. The
[targeted regression workflow](skills/jvm-spark-migration/references/targeted-regressions.md)
connects actual library/JDK impacts to existing coverage, missing tests and
before/after execution evidence. The coding assistant performs this work in the
target application using its existing test framework and authorized scope.
The toolkit supplies instructions and a report template; it does not automatically
generate or run tests without the coding assistant and a target project.
