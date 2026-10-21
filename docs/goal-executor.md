# Goal executor — Feature 4

The initial executor is **a conservative checkpoint validator**, not an autonomous migration engine. It never runs builds, edits source code, invokes an LLM, generates evidence or approves a migration. Harness installation remains manual.

Requires Python 3.9+ and Git. From this toolkit checkout, point to an already initialized target project with `migration/state.json`:

```bash
python3 scripts/goal_executor.py --project /path/to/project status
python3 scripts/goal_executor.py --project /path/to/project complete --goal GOAL-001
python3 -m unittest discover -s tests -p 'test_goal_executor.py'
```

A completion attempt is refused unless:
- saved HEAD and branch match actual Git state;
- dependencies are complete;
- the goal is READY or VALIDATING;
- report persistence is explicitly authorized;
- every acceptance check is PASS and at least one check exists;
- a nonempty report and all local evidence paths exist within the project.

A successful completion updates the state file via an atomic replacement. This does not establish crash-safe multi-file transactions, evidence integrity, a signed approval system or a full JSON Schema validator. A preexisting COMPLETED goal is rechecked at every invocation. External report destinations are not yet supported by this CLI.

The operator or an authorized agent must create reports and record acceptance evidence **before** calling complete. Never mark checks PASS without execution evidence. Report generation, reconciliation workflows and goal execution are subsequent increments.
