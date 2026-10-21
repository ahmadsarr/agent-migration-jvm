# PR 2 — Harness installer report

## Objective
Install the existing migration skill and command definitions into selected coding harness project directories.

## Changes
- `scripts/install.sh`: POSIX shell installer with `--harness`, `--target`, and opt-in `--force`.
- `docs/harness-installation.md`: usage, destination mapping and limitations.

## Verification
| Check | Result | Evidence |
|---|---|---|
| GitHub file creation | PASS | GitHub API acknowledged both writes |
| POSIX shell syntax check | NOT RUN | No local shell execution |
| OpenCode skill discovery | NOT RUN | No OpenCode CLI |
| Claude skill discovery | NOT RUN | No Claude Code CLI |
| Codex skill discovery | NOT RUN | No Codex CLI |

## Risks
- OpenCode command templates need harness-specific verification.
- Installer is not transactional: a mid-run error can leave partial copies.
- No automated shell test suite yet.

## Decision
Ready for code review, **not yet validated for production use**.
