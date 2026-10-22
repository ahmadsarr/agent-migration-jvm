#!/usr/bin/env python3
"""Generate exact skill mirrors, or report drift without writing (--check)."""
import argparse
import difflib
from pathlib import Path
import sys

SOURCE = Path('skills/jvm-spark-migration')
MIRRORS = (Path('.agents/skills/jvm-spark-migration'),
           Path('.claude/skills/jvm-spark-migration'))


def inventory(root, relative):
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Symlink is not supported: ' + str(path))
        if path.exists() and not path.is_dir():
            raise ValueError('Expected directory: ' + str(path))
    files = {}
    if path.exists():
        for item in sorted(path.rglob('*')):
            if item.is_symlink():
                raise ValueError('Symlink is not supported: ' + str(item))
            if item.is_file():
                files[item.relative_to(path)] = item.read_bytes()
            elif not item.is_dir():
                raise ValueError('Unsupported filesystem entry: ' + str(item))
    return files


def sync(root, check=False):
    expected = inventory(root, SOURCE)
    if not expected.get(Path('SKILL.md')):
        raise ValueError('Canonical SKILL.md is missing or empty; refusing to generate mirrors')
    # Preflight both destinations before changing either one.
    actual = {mirror: inventory(root, mirror) for mirror in MIRRORS}
    drift = False
    for mirror, files in actual.items():
        for name in sorted(expected.keys() | files.keys()):
            before, after = files.get(name), expected.get(name)
            if before == after:
                continue
            drift = True
            label = 'extra' if after is None else 'missing' if before is None else 'changed'
            print(f'{label}: {mirror / name}')
            if check:
                try:
                    lines = difflib.unified_diff(
                        (before or b'').decode('utf-8').splitlines(keepends=True),
                        (after or b'').decode('utf-8').splitlines(keepends=True),
                        fromfile=str(mirror / name), tofile=str(SOURCE / name))
                    for line in lines:
                        print(line, end='' if line.endswith('\n') else '\n')
                except UnicodeDecodeError:
                    print('Binary content differs')
        if not check:
            destination = root / mirror
            # Remove only stale files/directories inside this generated skill.
            # Pruning first also handles file-to-directory changes in the source.
            for name in files.keys() - expected.keys():
                (destination / name).unlink()
            if destination.exists():
                for directory in sorted(destination.rglob('*'), key=lambda p: len(p.parts), reverse=True):
                    if directory.is_dir() and not any(directory.iterdir()):
                        directory.rmdir()
            for name, content in expected.items():
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if files.get(name) != content:
                    target.write_bytes(content)
    if check and drift:
        print('Skill mirrors are stale. Run: python3 scripts/sync_skills.py', file=sys.stderr)
        return 1
    print('Skill mirrors match the canonical source.' if check else 'Skill mirrors generated.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Show diffs and exit 1 on drift; never write')
    args = parser.parse_args()
    try:
        return sync(Path(__file__).resolve().parents[1], args.check)
    except (ValueError, OSError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
