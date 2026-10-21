---
name: migration-plan
description: Plan reversible JVM migration batches with acceptance gates.
disable-model-invocation: true
---
Use the jvm-spark-migration skill instructions and references in this repository.

Use audit and compatibility results. Define minimal batches, affected files, dependencies, tests, rollback and explicit approval gates. Do not modify code.
Use the skill's targeted regression workflow to map critical dependency/JDK impacts to application behavior and existing assertions. Specify only missing tests, deterministic fixtures and equivalent baseline/target runs. Reuse sufficient coverage and record unresolved contracts as gaps.

If arguments are provided, treat them as the target repository/path or requested migration batch: $ARGUMENTS
