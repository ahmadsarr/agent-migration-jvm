# /migration:audit
Read-only assessment. Inventory JDK, Spark, Scala, build system, dependencies, plugins, Spark connectors, serializers, runtime JVMs, CI and deployment. Use jdeps/jdeprscan and dependency tooling where available, explaining limitations. Report findings, evidence and unknowns. Do not edit files.

For Spring applications, load the skill's `references/spring-migration.md` profile and inventory Boot/Framework, BOM overrides, Security, Data/ORM, Cloud, web stack, profiles and deployment container. Spark/Scala checks apply only if present.
