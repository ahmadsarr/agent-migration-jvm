#!/usr/bin/env bash
set -euo pipefail
usage(){ echo 'Usage: install.sh --harness opencode|claude|codex [--scope project|global] [--target DIR] [--action install|update|uninstall|status] [--dry-run]' >&2; }
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
[[ -f $root/VERSION ]] || { echo 'Missing toolkit VERSION' >&2; exit 2; }
toolkit_version=$(cat "$root/VERSION")
[[ $toolkit_version =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || { echo 'Invalid toolkit VERSION (expected MAJOR.MINOR.PATCH)' >&2; exit 2; }
if [[ $# == 1 && $1 == --version ]]; then echo "$toolkit_version"; exit 0; fi
harness='' target='' scope='project' action='install' dry=0
while (($#)); do
 case "$1" in
 --harness|--target|--scope|--action) (($#>=2)) || { usage; exit 2; }; case "$1" in --harness) harness=$2;; --target) target=$2;; --scope) scope=$2;; --action) action=$2;; esac; shift 2;;
 --dry-run) dry=1; shift;; *) usage; exit 2;; esac
done
[[ $harness == opencode || $harness == claude || $harness == codex ]] || { usage; exit 2; }
[[ $action == install || $action == update || $action == uninstall || $action == status ]] || { usage; exit 2; }
[[ $scope == project || $scope == global ]] || { usage; exit 2; }
command -v sha256sum >/dev/null || { echo 'sha256sum required' >&2; exit 2; }
if [[ $scope == project ]]; then
 target=${target:-$PWD}
 [[ -d $target && ! -L $target ]] || { echo 'Target directory does not exist' >&2; exit 2; }
 target=$(cd "$target" && pwd -P)
 case "$harness" in
  opencode) prefix='.opencode';;
  claude) prefix='.claude';;
  codex) prefix='.agents';;
 esac
 manifest_rel=".jvm-migration/$harness.manifest"
 display_target=$target
else
 [[ -z $target ]] || { echo '--target cannot be combined with --scope global' >&2; exit 2; }
 [[ ${HOME:-} == /* && -d $HOME ]] || { echo 'Global installation requires an absolute existing HOME' >&2; exit 2; }
 case "$harness" in
  opencode) config_root="${XDG_CONFIG_HOME:-$HOME/.config}/opencode";;
  claude) config_root="${CLAUDE_CONFIG_DIR:-$HOME/.claude}";;
  codex) config_root="$HOME/.agents";;
 esac
 # Keep global paths lexical so preflight can reject symlinked ancestors.
 [[ $config_root == /* && $config_root != *'..'* && $config_root != *$'\n'* && $config_root != *$'\t'* ]] || { echo 'Invalid global configuration path' >&2; exit 2; }
 config_root=${config_root%/}
 [[ $config_root != '' && $config_root != / ]] || { echo 'Global configuration cannot be filesystem root' >&2; exit 2; }
 target='/'
 prefix=${config_root#/}
 manifest_rel="$prefix/.jvm-migration/$harness.manifest"
 display_target=$config_root
fi
manifest="$target/$manifest_rel"
check_ancestors() {
  local path="$target" component
  local -a parts
  IFS='/' read -r -a parts <<< "$1"
  for component in "${parts[@]}"; do
    path="$path/$component"
    if [[ -L "$path" ]]; then echo "Symlink conflict: $path" >&2; return 1; fi
  done
}

declare -a sources=() dests=() hashes=() previous_paths=() previous_hashes=()
map_dir(){ local src=$1 prefix=$2 file rel; [[ -d $root/$src ]] || { echo "Missing source $src" >&2; exit 2; }; while IFS= read -r -d '' file; do rel=${file#"$root/$src/"}; sources+=("$file"); dests+=("$prefix/$rel"); hashes+=("$(sha256sum "$file" | cut -d' ' -f1)"); done < <(find "$root/$src" -type f -print0 | sort -z); }
case "$harness" in
 opencode) map_dir skills/jvm-spark-migration "$prefix/skills/jvm-spark-migration"; map_dir commands "$prefix/commands";;
 claude) map_dir .claude/skills/jvm-spark-migration "$prefix/skills/jvm-spark-migration"; map_dir .claude/commands "$prefix/commands"; map_dir .claude/agents "$prefix/agents";;
 codex) map_dir .agents/skills/jvm-spark-migration "$prefix/skills/jvm-spark-migration";;
esac
version_rel="$prefix/skills/jvm-spark-migration/TOOLKIT_VERSION"
sources+=("$root/VERSION")
dests+=("$version_rel")
hashes+=("$(sha256sum "$root/VERSION" | cut -d' ' -f1)")
if [[ -f $manifest ]]; then
 while IFS=$'\t' read -r hash path; do [[ $hash =~ ^[a-f0-9]{64}$ && $path != /* && $path != *'..'* && $path == "$prefix/"* ]] || { echo 'Invalid manifest' >&2; exit 2; }; previous_hashes+=("$hash"); previous_paths+=("$path"); done < "$manifest"
fi
old_hash(){ local i; REPLY=''; for i in "${!previous_paths[@]}"; do if [[ ${previous_paths[i]} == "$1" ]]; then REPLY=${previous_hashes[i]}; return; fi; done; }
conflict=0
for i in "${!dests[@]}"; do
 path=${dests[i]}; check_ancestors "$path" || { conflict=1; continue; }; [[ ! -L $target/$path ]] || { echo "Symlink conflict: $path" >&2; conflict=1; continue; }
 old_hash "$path"; old=$REPLY
 if [[ -e $target/$path ]]; then
  actual=$(sha256sum "$target/$path" | cut -d' ' -f1)
  if [[ -z $old || $actual != "$old" ]]; then echo "Conflict (unmanaged or modified): $path" >&2; conflict=1; fi
 elif [[ -n $old && $action != install ]]; then echo "Conflict (locally deleted): $path" >&2; conflict=1
 fi
done
check_ancestors "$manifest_rel" || conflict=1
if [[ $action == install && -f $manifest ]]; then echo 'Already installed: use --action update' >&2; conflict=1; fi
if [[ $action != install && ! -f $manifest ]]; then echo 'No installation manifest' >&2; conflict=1; fi
if [[ $action == uninstall || $action == update || $action == status ]]; then
 for i in "${!previous_paths[@]}"; do
  path=${previous_paths[i]}; check_ancestors "$path" || { conflict=1; continue; }; [[ -f $target/$path && ! -L $target/$path ]] && actual=$(sha256sum "$target/$path" | cut -d' ' -f1) || actual='MISSING'
  if [[ $actual != "${previous_hashes[i]}" ]]; then echo "Conflict (modified or missing): $path" >&2; conflict=1; fi
 done
fi
if [[ $action == status ]]; then
 echo "Toolkit source version: $toolkit_version"
 if [[ -f $manifest ]]; then
  old_hash "$version_rel"
  if [[ -n $REPLY && -f $target/$version_rel && ! -L $target/$version_rel ]]; then
   echo "Installed version: $(cat "$target/$version_rel")"
  else
   echo 'Installed version: UNKNOWN (legacy installation or missing version marker)'
  fi
  echo "Scope: $scope; assistant: $harness; location: $display_target"
 fi
 ((conflict==0)) || { echo 'Installation has conflicts; version information is not an integrity guarantee.' >&2; exit 3; }
 exit 0
fi
((conflict==0)) || { echo 'Aborted before writing any file.' >&2; exit 3; }
if ((dry)); then
 echo "DRY RUN: $action for $harness ($scope) at $display_target; toolkit $toolkit_version"
 for path in "${dests[@]}"; do [[ $action == uninstall ]] || echo "Would install: $path"; done
 if [[ $action == uninstall ]]; then for path in "${previous_paths[@]}"; do echo "Would remove: $path"; done; fi
 exit 0
fi
backup=$(mktemp -d)
committed=0
rollback() {
  local code=$? path
  trap - EXIT INT TERM
  if ((committed==0)); then
    for path in "${dests[@]}" "${previous_paths[@]}"; do
      if [[ -f "$backup/old/$path" ]]; then
        mkdir -p "$(dirname "$target/$path")"
        cp -- "$backup/old/$path" "$target/$path" || true
      else
        rm -f -- "$target/$path" || true
      fi
    done
    if [[ -f "$backup/manifest" ]]; then
      cp -- "$backup/manifest" "$manifest" || true
    else
      rm -f -- "$manifest" || true
    fi
  fi
  rm -rf -- "$backup"
  exit "$code"
}
trap rollback EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
for path in "${dests[@]}" "${previous_paths[@]}"; do
  if [[ -f "$target/$path" && ! -f "$backup/old/$path" ]]; then
    mkdir -p "$(dirname "$backup/old/$path")"
    cp -- "$target/$path" "$backup/old/$path"
  fi
done
[[ ! -f "$manifest" ]] || cp -- "$manifest" "$backup/manifest"
mkdir -p "$(dirname "$manifest")"
if [[ $action == uninstall ]]; then
 for path in "${previous_paths[@]}"; do rm -- "$target/$path"; done
 rm -- "$manifest"; committed=1; echo "Uninstalled $harness"; exit 0
fi
if [[ $action == update ]]; then
 for path in "${previous_paths[@]}"; do found=0; for current in "${dests[@]}"; do [[ $path == "$current" ]] && found=1; done; ((found)) || rm -- "$target/$path"; done
fi
for i in "${!dests[@]}"; do mkdir -p "$(dirname "$target/${dests[i]}")"; cp -- "${sources[i]}" "$target/${dests[i]}"; done
: > "$manifest"
for i in "${!dests[@]}"; do printf '%s\t%s\n' "${hashes[i]}" "${dests[i]}" >> "$manifest"; done
committed=1
echo "$action complete for $harness ($scope) at $display_target; toolkit $toolkit_version"
