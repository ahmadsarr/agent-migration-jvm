# Harness installer — MR #2
Requires Bash, sha256sum, find and coreutils. See [installation scopes](harness-installation.md) for project/current-directory and user-global installation. Existing explicit `--target` invocations remain supported.

```bash
bash scripts/install.sh --harness opencode --target /path/to/project --dry-run
bash scripts/install.sh --harness opencode --target /path/to/project
bash scripts/install.sh --harness opencode --target /path/to/project --action update
bash scripts/install.sh --harness opencode --target /path/to/project --action uninstall
bash tests/install-test.sh
```
Replace `opencode` with `claude` or `codex`.

Destinations:
- OpenCode: `.opencode/skills/jvm-spark-migration/` and `.opencode/commands/`.
- Claude Code: `.claude/skills/`, `.claude/commands/`, `.claude/agents/`.
- Codex: `.agents/skills/jvm-spark-migration/`.

A preflight scans conflicts before any write. The `.jvm-migration/<harness>.manifest` records relative installed paths and SHA-256 checksums. Updates and uninstall refuse modified or missing managed files. No `--force` option is provided. `--dry-run` previews actions without writing.

Limitations: this is not a transactional installer; I/O errors during copying can still leave a partial installation. Symlinked ancestor directories and concurrent changes require additional hardening. CLI discovery and slash command behavior must be tested against installed CLI versions; file presence alone does not prove discovery.
