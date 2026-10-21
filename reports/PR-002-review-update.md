# PR #2 — Installer review report
## Goal
Install JVM migration instructions into OpenCode, Claude Code or Codex projects, with safe preflight, dry-run and lifecycle management.
## Changes
- Bash installer with conflict preflight before writes
- `--dry-run`, `--action install|update|uninstall`
- SHA-256 manifest and modified-file protection
- Test script for installation, update, modified-file refusal and uninstall
## Evidence
| Check | Status | Evidence |
|---|---|---|
| Shell syntax | PASS (local sandbox) | `bash -n scripts/install.sh` |
| OpenCode fixture installation lifecycle | PASS (local sandbox) | `tests/install-test.sh` |
| Claude Code fixture installation lifecycle | PASS (local sandbox) | `tests/install-test.sh` |
| Codex fixture installation lifecycle | PASS (local sandbox) | `tests/install-test.sh` |
| Real CLI skill/command discovery | NOT RUN | No CLI environment validated |
| Full repository fixture run | NOT RUN | Local test used representative dummy files |
## Remaining risks
- Installation is preflighted but not transactional against I/O failure or concurrent filesystem changes.
- CLI discovery still requires an actual CLI smoke test.
- Script relies on Bash and GNU coreutils; it is not POSIX sh portable.
## Decision
Ready for review, **not yet complete** against all reviewer criteria.
