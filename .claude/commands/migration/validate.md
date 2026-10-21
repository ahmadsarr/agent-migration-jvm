---
name: migration-validate
description: Validate Java 11 versus target JDK behavior and runtime.
disable-model-invocation: true
---
Use the jvm-spark-migration skill instructions and references in this repository.

Execute only safe available tests. Compare build, Spark batch and streaming, serialization, restart, performance and deployment. Mark missing checks NOT RUN. Report evidence and Go/No-Go.
For each critical risk in the batch's targeted regression report, verify the selected test actually ran with equivalent fixtures and assertions in both environments. Require execution evidence, investigate differences and retain NOT_RUN for missing runs. Unresolved critical gaps prevent Go; checkpoint evidence fields remain arrays.

If arguments are provided, treat them as the target repository/path or requested migration batch: $ARGUMENTS
