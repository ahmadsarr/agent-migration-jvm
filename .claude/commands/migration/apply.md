---
name: migration-apply
description: Implement one explicitly approved migration batch.
disable-model-invocation: true
---
Use the jvm-spark-migration skill instructions and references in this repository.

Require an approved batch and clean or understood Git state. Work on a separate branch. Show intended edits, change only the approved scope and run relevant checks. Stop on unexpected failures.

If arguments are provided, treat them as the target repository/path or requested migration batch: $ARGUMENTS
