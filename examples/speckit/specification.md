Improve the toolkit's reporting of behavioral risks after critical JVM dependency
changes. A maintainer should be able to see, for each concrete risk, the observed
behavioral contract, existing test coverage, any missing targeted test, and the
baseline/target evidence. Reuse existing regression templates and avoid duplicate
tests. Missing environments must appear as NOT_RUN, never as passing validation.
Inspect current capabilities before proposing changes. Do not choose a target JDK
or migrate an external application as part of this feature.
