---
name: migration-audit
description: Inspect a Java 11 Spark Scala application without editing files.
disable-model-invocation: true
---
Use the jvm-spark-migration skill instructions and references in this repository.

Inspect repository and runtime configuration. Produce an evidence-based inventory, baseline gaps and unknowns. Read-only. Never infer versions.

If arguments are provided, treat them as the target repository/path or requested migration batch: $ARGUMENTS

For Spring applications, load the skill's `references/spring-migration.md` profile and inventory Boot/Framework, BOM overrides, Security, Data/ORM, Cloud, web stack, profiles and deployment container. Spark/Scala checks apply only if present.
