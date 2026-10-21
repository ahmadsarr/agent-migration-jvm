# Agent Migration JVM

Toolkit for planning and validating migrations from Java 11 to a compatible target JDK for Java, Scala and Apache Spark applications.

## Workflow
1. Audit existing runtime, dependencies, Spark, Scala and build tooling.
2. Determine a supported target JDK from verified compatibility evidence.
3. Plan small reversible changes.
4. Apply only approved changes.
5. Validate tests, Spark streaming recovery, performance and deployment.

See `skills/jvm-spark-migration/SKILL.md` and `commands/`.

Command files are prompt templates; slash-command registration depends on the coding assistant.
