#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
for harness in opencode claude codex; do
 target=$(mktemp -d)
 bash "$root/scripts/install.sh" --harness "$harness" --target "$target" --dry-run >/dev/null
 [[ ! -e $target/.jvm-migration/$harness.manifest ]]
 bash "$root/scripts/install.sh" --harness "$harness" --target "$target" >/dev/null
 [[ -s $target/.jvm-migration/$harness.manifest ]]
 bash "$root/scripts/install.sh" --harness "$harness" --target "$target" --action update >/dev/null
 first=$(find "$target" -name SKILL.md | head -1)
 [[ -n $first ]]
 echo local-change >> "$first"
 if bash "$root/scripts/install.sh" --harness "$harness" --target "$target" --action uninstall >/dev/null 2>&1; then echo 'FAIL: modification protection' >&2; exit 1; fi
 [[ -f $first ]]
 sed -i '$d' "$first"
 bash "$root/scripts/install.sh" --harness "$harness" --target "$target" --action uninstall >/dev/null
 [[ ! -e $target/.jvm-migration/$harness.manifest ]]
 rm -rf "$target"
 echo "PASS: $harness"
done
