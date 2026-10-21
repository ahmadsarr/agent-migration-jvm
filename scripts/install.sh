#!/usr/bin/env sh
set -eu
usage() {
  echo "Usage: sh scripts/install.sh --harness opencode|claude|codex --target PATH [--force]" >&2
}
harness="" target="" force=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --harness) [ "$#" -ge 2 ] || { usage; exit 2; }; harness=$2; shift 2;;
    --target) [ "$#" -ge 2 ] || { usage; exit 2; }; target=$2; shift 2;;
    --force) force=1; shift;;
    *) usage; exit 2;;
  esac
done
[ -n "$target" ] && [ -n "$harness" ] || { usage; exit 2; }
case "$harness" in opencode|claude|codex) ;; *) usage; exit 2;; esac
[ -d "$target" ] || { echo "Target directory does not exist: $target" >&2; exit 2; }
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$script_dir/.." && pwd)
copy_file() {
  src=$1 dest=$2
  [ -f "$src" ] || { echo "Missing source: $src" >&2; exit 1; }
  if [ -e "$dest" ] && [ "$force" -ne 1 ]; then
    echo "Refusing to overwrite: $dest (use --force)" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dest")"
  cp "$src" "$dest"
  echo "Installed: $dest"
}
# Portable directory copy: copy files one by one so overwrites are explicit.
copy_dir() {
  src=$1 dest=$2
  [ -d "$src" ] || { echo "Missing source directory: $src" >&2; exit 1; }
  find "$src" -type f | while IFS= read -r file; do
    rel=${file#"$src"/}
    copy_file "$file" "$dest/$rel"
  done
}
case "$harness" in
  opencode)
    copy_dir "$root/skills/jvm-spark-migration" "$target/.opencode/skills/jvm-spark-migration"
    copy_dir "$root/commands" "$target/.opencode/commands"
    ;;
  claude)
    copy_dir "$root/.claude/skills/jvm-spark-migration" "$target/.claude/skills/jvm-spark-migration"
    copy_dir "$root/.claude/commands" "$target/.claude/commands"
    copy_dir "$root/.claude/agents" "$target/.claude/agents"
    ;;
  codex)
    copy_dir "$root/.agents/skills/jvm-spark-migration" "$target/.agents/skills/jvm-spark-migration"
    ;;
esac
echo "Installation complete for $harness. Verify discovery in the selected CLI."
