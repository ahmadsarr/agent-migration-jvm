# Spec Kit through OpenCode

The wrapper runs official Spec Kit commands with `opencode run`. Use it in the
toolkit checkout to develop the toolkit, or point it at an application checkout.
It selects the feature explicitly and records each invocation for review.

## Install

The wrapper needs Python 3.9+. Install [uv](https://docs.astral.sh/uv/) and
[OpenCode](https://opencode.ai/docs/), configure its model provider, then install
the supported Spec Kit version:

```bash
uv tool install --python 3.12 'specify-cli==1.2.2'
specify version --json
opencode --version
```

Ensure both commands are on PATH. The wrapper checks Spec Kit 1.2.2 during `init`.
Existing scaffolding must use that version's command format. OpenCode uses its
configured model unless you pass `--model provider/model` before the subcommand.
Provider configuration and OpenCode permissions remain yours to configure; the
wrapper does not enable `--auto` or grant permissions. Headless requests requiring
interaction may fail or time out; inspect their logs and use interactive OpenCode
to resolve them.

## Initialize and prepare

Run on a dedicated branch in a clean checkout. The examples below develop the
toolkit itself. Replace `project_dir` with an absolute application path to work on
an application, and supply inputs describing that application's migration.
The wrapper does not install JVM tooling or the migration skill into another
project; use the [toolkit installer](../README.md#use-with-opencode) for the skill.

```bash
toolkit_dir="$PWD"  # run from the agent-migration-jvm checkout
project_dir="$toolkit_dir"
runner="$toolkit_dir/scripts/speckit_opencode.py"

python3 "$runner" --project "$project_dir" --dry-run init
python3 "$runner" --project "$project_dir" init
python3 "$runner" --project "$project_dir" run constitution \
  --input-file "$toolkit_dir/examples/speckit/constitution.md"
```

Review the generated `.specify/memory/constitution.md`, then adapt the example
specification and technical plan inputs to your actual feature:

```bash
python3 "$runner" --project "$project_dir" prepare \
  --feature specs/006-regression-evidence \
  --spec-file "$toolkit_dir/examples/speckit/specification.md" \
  --plan-file "$toolkit_dir/examples/speckit/plan.md"
```

`prepare` runs `speckit.specify`, `speckit.plan`, `speckit.tasks`, then
`speckit.analyze`. It stops before implementation. Read `spec.md`, `plan.md`,
`tasks.md` in the feature directory and the analysis output in the execution logs.
This command requires a new feature: it refuses to replay over existing artifacts.

Initialization merges Spec Kit scaffolding into the project using official
`specify init --here --integration opencode --script py --non-interactive
--ignore-agent-tools --force`. Preflight refuses an existing `.specify` directory
or Spec Kit command files. Existing toolkit commands such as `/audit` can coexist
with `/speckit.specify`. Manage an already initialized Spec Kit installation
separately; the wrapper does not upgrade it.

## Resume, implement and validate

For an interrupted preparation, resolve the error and invoke just the required
stage. For example, after reviewing or clarifying the specification:

```bash
python3 "$runner" --project "$project_dir" run plan \
  --feature specs/006-regression-evidence \
  --input-file "$toolkit_dir/examples/speckit/plan.md"
python3 "$runner" --project "$project_dir" run tasks --feature specs/006-regression-evidence
python3 "$runner" --project "$project_dir" run analyze --feature specs/006-regression-evidence
python3 "$runner" --project "$project_dir" run implement --feature specs/006-regression-evidence
python3 "$runner" --project "$project_dir" run converge --feature specs/006-regression-evidence
```

Review the analysis before invoking `implement`. Use `converge` for Spec Kit's
subsequent convergence pass; inspect actual test evidence and remaining findings.
Every `run` is an independent OpenCode invocation. `constitution`, `specify` and
`plan` require `--input-file`; other stages accept it optionally for extra context.

The wrapper blocks downstream steps while the specification contains
`[NEEDS CLARIFICATION ...]`. To answer questions interactively, launch OpenCode
with the same feature selected and use `/speckit.clarify`:

```bash
cd "$project_dir"
SPECIFY_FEATURE_DIRECTORY=specs/006-regression-evidence opencode
```

The wrapper explicitly sets `SPECIFY_FEATURE_DIRECTORY` for each feature command,
overriding an inherited selection. Feature paths must be inside the project's
`specs/` directory. Global options (`--project`, `--model`, `--timeout`, `--dry-run`)
precede `init`, `prepare` or `run`. `--timeout` defaults to 900 seconds per command.
`--dry-run` checks initial prerequisites and prints arguments without executing
tools or writing files; it cannot simulate artifacts from later stages.

## Reports and limits

New reports include `toolkit_version`, identifying the wrapper checkout, separately
from `spec_kit_version`. Run `python3 scripts/speckit_opencode.py --version` to
inspect it; see [toolkit versioning](versioning.md).

Each execution prints its report location under
`.jvm-migration/speckit-runs/<timestamp>-<id>/`. It contains `report.json`, per-stage
`stdout.jsonl` (plain `stdout.log` for init), and `stderr.log`. Reports include
arguments, exit codes, Git HEAD when available, and artifact hashes before/after.
Inputs and model outputs can contain project data; review logs before sharing or
committing them.

Nonzero exits, OpenCode error events (even with exit code zero), malformed/empty
events, missing artifacts and timeouts fail the run and stop the sequence.
Exit codes are 0 for returned commands, 2 for errors, and 130 for interruption.
`RETURNED_REVIEW_REQUIRED` means commands returned and required files exist. It
does not prove semantic correctness, successful tests, or migration completion.
The wrapper never advances `migration/state.json`; checkpoint evidence remains
subject to the existing migration workflow. Prompt instructions guide the agent
but are not a sandbox: OpenCode's configured permissions govern edits and tools.

## Validation and upstream references

```bash
python3 -m unittest discover -s tests -p 'test_speckit_opencode.py' -v
```

Tests use a fake OpenCode executable to check orchestration and failures without
a model provider. Real Spec Kit 1.2.2 initialization was also smoke-tested; live
OpenCode model execution and application migration tests have not been run here.

- [Spec Kit v1.2.2](https://github.com/github/spec-kit/tree/v1.2.2)
- [Spec Kit OpenCode integration](https://github.com/github/spec-kit/blob/v1.2.2/src/specify_cli/integrations/opencode/__init__.py)
- [OpenCode run CLI](https://opencode.ai/docs/cli/#run)
