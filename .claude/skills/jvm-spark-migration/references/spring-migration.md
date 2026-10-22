# Spring / Spring Boot JVM migration profile

Apply this profile when Spring Framework or Spring Boot is detected. Spark and
Scala are optional: do not impose Spark validation on a Spring-only application.
Keep the existing migration stages, authorization scope and evidence requirements.

## Audit and compatibility

- Inspect Maven parents/BOMs, effective dependencies or Gradle dependency reports:
  exact Spring Boot, Framework, Security, Data, Cloud and Hibernate versions;
  starters, overridden managed versions and relevant transitives.
- Identify Boot versus plain Framework, MVC versus WebFlux, embedded server versus
  external servlet container, packaging, active profiles and configuration binding.
- Record build JDK, compiler release/toolchain, runtime/container JDK, Maven/Gradle
  wrapper, test plugins, bytecode agents, annotation processors and instrumentation.
- Inventory actual uses of HTTP/JSON, security filters, authentication, validation,
  persistence, transactions, messaging, scheduling and Actuator. Do not expose secrets.
- Build a version matrix with current/candidate versions, official version-specific
  sources, runtime/build constraints, blockers and unknowns. Check Spring Cloud's
  release-train compatibility if present. A Java minimum is not a supported maximum.
- Distinguish a JDK-only migration from a Boot/Framework major upgrade. Do not
  upgrade Spring merely because the JDK changes. Conversely, do not select a target
  JDK unsupported by the current Spring stack or build tools.
- For a Boot 2 to 3 path, consult the official migration guide: Boot 3 requires
  Java 17 or later and moves to Framework 6 / Jakarta EE APIs. Verify the exact
  target release's requirements; this is not blanket support for every newer JDK.
  For other major transitions, consult that transition's versioned guide separately.
- For plain Framework, verify its version, dependency management and deployment
  container directly; do not assume Boot's BOM or auto-configuration exists.

## Reversible batches

1. Capture a source-JDK baseline with the current dependencies, configuration and
   representative data. Reuse adequate existing tests; add only identified gaps.
2. Choose a supported intermediate combination when necessary. Separate the JDK,
   build tooling and framework transitions where compatibility permits. If changes
   must be coupled, document why and validate that batch as a unit.
3. For a Jakarta transition, trace only affected EE APIs and dependencies. Never
   globally replace `javax.*`: Java SE packages such as `javax.sql` and
   `javax.crypto` remain valid. Check third-party libraries and servlet containers.
4. Review Security configuration, property renames, removed APIs, request matching,
   ORM/query behavior and serialization against the actual target release notes.
   Do not disable security, validation or tests to make the upgrade pass.
5. Run equivalent source/target checks and persist evidence before Go/No-Go.
   Keep schema/data changes separate where possible. Reverting a JAR does not
   reverse schema or message-format changes; document recovery constraints.

## Targeted acceptance checks

Select only applicable checks from observed usage and actual gaps. A startup
smoke test or successful compilation alone does not validate application behavior.

| Area | Behavioral contracts to inspect and compare |
|---|---|
| Context/configuration | Application starts with representative profiles; expected beans and property binding; no production credentials required |
| MVC/WebFlux | Representative routes, methods, status codes, headers, error responses and validation; blocking/reactive behavior where used |
| JSON | Field names, null handling, dates/time zones and backward-compatible payloads |
| Security | Allowed and denied requests, unauthenticated versus forbidden responses, role rules, CORS/CSRF/session or token behavior as specified |
| Persistence | Real query results, paging, explicit ordering, nulls, transaction rollback, lazy-loading and schema compatibility with the relevant database |
| Messaging/batch | Serialization, acknowledgments, retries, idempotency and restart behavior where applicable |
| Operations | Health/readiness, graceful shutdown, metrics relied on by operations and representative performance |

Use the application's framework (for example existing Spring test slices,
MockMvc/WebTestClient or integration tests) and isolated services where available.
Do not substitute an in-memory database for a production-dialect regression
without explaining the coverage gap. Do not introduce Testcontainers or another
framework if existing infrastructure already covers the contract.

For every selected risk, record the existing assertion, any justified test change,
exact versions and commands, executed/skipped counts, exit codes and source/target
logs in the targeted regression report. Preserve `NOT_RUN` for unavailable checks.
Unresolved mandatory gaps prevent Go; checkpoint evidence fields remain arrays.

## Official starting points

Follow version selectors and record the exact page/release consulted in the report.
These links are research entry points, not a static compatibility guarantee.

- [Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html)
- [Boot 3.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Framework versions](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-Versions)
- [Security migration](https://docs.spring.io/spring-security/reference/migration/index.html)
- [Spring Cloud compatibility](https://spring.io/projects/spring-cloud#overview)
