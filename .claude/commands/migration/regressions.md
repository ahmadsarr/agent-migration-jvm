---
name: migration-regressions
description: Add only missing regression tests for critical JVM migration impacts and compare baseline and target behavior.
disable-model-invocation: true
---
Use the installed jvm-spark-migration skill and its `references/targeted-regressions.md` workflow.

For the selected migration batch, trace changed critical dependencies and JDK-sensitive usages to application behavior. Inspect existing assertions and fixtures, reuse sufficient tests, and propose only the missing regression tests. With authorization, implement them using the project's test framework and run equivalent checks on Java 11/source dependencies and the supported target JDK/migrated dependencies.

Preserve explicit application contracts; do not assert incidental ordering or other unspecified behavior. Use `references/regression-report-template.md` for the impact map and execution evidence. Persist only to an authorized destination, mark missing runs NOT_RUN and keep checkpoint evidence as arrays. Unresolved critical gaps prevent a Go decision; follow the skill's completion gates.

Treat arguments as the target project or migration batch: $ARGUMENTS
