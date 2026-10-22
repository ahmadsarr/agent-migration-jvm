# Migration orchestration checkpoint

This reference travels with the installed skill. The toolkit checkout contains
`migration/templates/state.json`, the schema, and `scripts/goal_executor.py`;
the skill installer does not install those tools or initialize a checkpoint.

With authorization, initialize the target project's `migration/state.json` from
the toolkit template and adapt the goals to the actual project. Record the actual
Git HEAD and branch, the selected baseline and the authorized report destination.
A typical project keeps assessment, compatibility and plan documents in
`migration/`, goal reports in `migration/reports/`, and evidence in `migration/evidence/`.

Execute goals in order: audit -> decide -> plan -> apply -> validate. Before each
run reconcile the saved HEAD, branch, reports and evidence with the actual project.
A divergence requires review; do not silently overwrite the checkpoint or repeat
non-idempotent changes. An existing file does not establish authorization.

A goal can become COMPLETED only after its dependencies complete, every acceptance
criterion passes and its report has been durably persisted to an authorized destination.
Record missing executions as NOT_RUN. Both goal-level and acceptance-level evidence
fields are arrays of paths. The current checkpoint CLI accepts project-local files;
it checks recorded conditions and file existence, not the semantic validity of proofs.

Use [goal protocol](goal-protocol.md), [report template](report-template.md), and
[targeted regressions](targeted-regressions.md) to retain the reporting and
before/after validation requirements. Source edits, tests and reports must remain
within the authorized scope. A completed technical goal does not authorize merging
or deployment. No autonomous migration is established by a checkpoint alone.
