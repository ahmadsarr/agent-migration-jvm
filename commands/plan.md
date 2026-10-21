# /migration:plan
Prepare incremental reversible migration batches. For each: rationale, prerequisite, affected files, risk, acceptance tests, rollback and approval gate. Keep dependency upgrades distinct from functional refactors.
Use the skill's targeted regression workflow to map critical dependency/JDK impacts to application behavior and existing assertions. Specify only the missing tests, deterministic fixtures and equivalent baseline/target runs; reuse sufficient coverage. Include unresolved contracts and unavailable environments as explicit gaps.
