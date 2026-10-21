---
name: migration-rollback
description: Prepare a safe JVM migration rollback.
disable-model-invocation: true
---
Use the jvm-spark-migration skill instructions and references in this repository.

Identify commit/image/config reversal, data and checkpoint risks. Present a rollback plan first; never execute destructive actions without explicit confirmation.

If arguments are provided, treat them as the target repository/path or requested migration batch: $ARGUMENTS
