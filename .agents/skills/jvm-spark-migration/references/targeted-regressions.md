# Targeted regression tests for JVM migration

Use this workflow when a JDK migration requires a critical dependency upgrade or
changes behavior at an application boundary. A successful build is not proof that
the application's behavior is preserved. Work from the actual project and its
existing test framework; do not invent library versions, usages or test results.

## 1. Establish the migration batch and its impact

- Record the source and target JDKs, Git revisions, and exact old/new dependency
  versions, including relevant transitive dependencies. Keep unrelated upgrades
  in separate batches. If versions are unresolved, record that gap.
- Read version-specific official migration guides and release notes. Trace the
  changed dependencies to concrete call sites, configuration and application
  boundaries. Link the files and documentation that support each identified risk.
- Prioritize dependencies whose changes can affect persisted data, external
  contracts or critical workloads. Examples include serialization, JDBC drivers,
  Spark/Scala APIs, connectors, HTTP clients, date/time and concurrency libraries.
  This is a risk-based selection, not a requirement to test every dependency.
- If a runtime-only upgrade leaves dependency versions unchanged, still examine
  JDK-sensitive behavior in the usages exercised by the application.

## 2. Define the behavior to protect and inspect existing coverage

For each identified risk, record the application behavior, affected call site,
existing test and coverage gap in the [report template](regression-report-template.md).
State the expected behavior from an application requirement, public contract or
confirmed business rule. If the expectation is ambiguous, resolve it with the
owner before writing assertions or declaring PASS.

Inspect assertions and fixtures, not just test names or coverage percentages.
Reuse a test that already exercises the risk. Add or extend a test only when a
specific gap remains; record why no new test is needed for adequately covered risks.

Possible assertions depend on actual usage:
- serialization: field names, null handling, precision and compatibility with
  previously persisted data;
- collections and query results: multiplicity, pagination and ordering only where
  the application contract requires it;
- time: zones, daylight-saving boundaries and precision;
- connectors: retry behavior, timeouts, error translation and resource cleanup;
- Spark/streaming: join semantics, schema handling, state/checkpoint recovery and
  duplicate/loss behavior with representative input.

Do not turn incidental iteration order, timing or unspecified behavior into a
contract merely because an older version happened to exhibit it. Use deterministic
fixtures, an explicit clock/seed where needed and isolated test resources.

## 3. Add the missing tests within the approved scope

Propose the minimal test changes and required fixtures before editing. Existing
authorization for this scope remains valid; risky test execution still requires
the appropriate authorization. Keep regression tests reviewable separately from
the dependency/runtime update, preferably in an earlier commit.

Test the real changed boundary. Prefer an integration test when mocks would hide
the library behavior at risk, and reuse the project's existing tools. Do not add
a new testing framework without a demonstrated need. Never use production data,
live production services or production checkpoints as regression fixtures.

## 4. Run equivalent checks before and after the migration

Run the selected tests on the Java 11/source-dependency baseline, then on the
supported target JDK and migrated dependency versions. Keep fixtures, assertions
and configuration equivalent and record exact test selectors, JDKs, dependency
versions, revisions, exit codes and logs. Include checks of the relevant Spark
driver/executor runtime when applicable; the developer machine JDK alone is not enough.

If the dependency was already upgraded, recover a reproducible baseline in an
isolated checkout without resetting the user's work. If identical test code cannot
compile against both APIs, document the minimal version-specific test adapters
while retaining equivalent behavioral assertions and fixtures. A baseline failure
must be explained or fixed before claiming a migration regression or equivalence.

Unavailable environments or skipped/disabled tests are NOT_RUN, not PASS. Exit
code zero alone does not prove that the requested tests were discovered and ran.
Do not normalize differences away unless the application contract permits them.
Any intended behavior change needs its rationale and approval recorded separately.

## 5. Close the validation goal with evidence

Persist the impact map, test changes and before/after results in an authorized
report destination. Each identified critical risk must have a relevant executed
check and evidence; unresolved risks or missing mandatory runs prevent a Go decision.
Reference evidence from the validation goal using the existing schema's arrays:
`acceptance[].evidence` and `goals[].evidence` are arrays of paths or references,
never a single string. Use PASS / FAIL / NOT_RUN in checkpoint acceptance results.

This workflow guides the coding assistant to inspect, add and run project tests.
It does not itself execute tests or infer business contracts. Only mark the goal
COMPLETED after its acceptance criteria and durable-report requirements pass.
