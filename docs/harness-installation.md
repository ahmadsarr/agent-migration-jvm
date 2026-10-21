# Harness installation (phase 2)

This is a portable POSIX shell installer for repository-local setup. It does **not** install the CLI itself.

```sh
sh scripts/install.sh --harness opencode --target /path/to/application
sh scripts/install.sh --harness claude --target /path/to/application
sh scripts/install.sh --harness codex --target /path/to/application
```

Use `--force` only when intentionally replacing previously installed files. Default behavior refuses overwrites.

| Harness | Skill location | Commands | Agents |
|---|---|---|---|
| OpenCode | `.opencode/skills/jvm-spark-migration/` | `.opencode/commands/` | Not installed |
| Claude Code | `.claude/skills/jvm-spark-migration/` | `.claude/commands/` | `.claude/agents/` |
| Codex | `.agents/skills/jvm-spark-migration/` | Not installed | Not installed |

OpenCode command templates are generic Markdown instructions copied from `commands/`; exact invocation behavior must be verified in an installed OpenCode version. No CLI smoke tests have been executed.

The installer does not modify the application's source code, but writes harness configuration into the target project. It does not configure report persistence authorization. That must be separately approved for the goal workflow.
