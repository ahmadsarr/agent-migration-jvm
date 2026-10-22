import contextlib
import io
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from scripts.sync_skills import MIRRORS, SOURCE, sync


class SyncSkillsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / SOURCE
        self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('# Canonical\n')
        (self.source / 'references').mkdir()
        (self.source / 'references/a.md').write_text('reference\n')

    def run_sync(self, check=False):
        with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            result = sync(self.root, check)
        return result, output.getvalue()

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def test_generate_and_repeat_are_identical(self):
        self.assertEqual(self.run_sync()[0], 0)
        first = self.snapshot()
        self.assertEqual(self.run_sync()[0], 0)
        self.assertEqual(self.snapshot(), first)
        self.assertEqual(self.run_sync(check=True)[0], 0)
        for mirror in MIRRORS:
            self.assertEqual((self.root / mirror / 'references/a.md').read_text(), 'reference\n')

    def test_check_reports_missing_modified_extra_without_writes(self):
        self.run_sync()
        mirror = self.root / MIRRORS[0]
        (mirror / 'SKILL.md').write_text('drift\n')
        (mirror / 'references/a.md').unlink()
        (mirror / 'stale.md').write_text('stale\n')
        before = self.snapshot()
        code, output = self.run_sync(check=True)
        self.assertEqual(code, 1)
        self.assertIn('changed:', output)
        self.assertIn('missing:', output)
        self.assertIn('extra:', output)
        self.assertIn('--- .agents/', output)
        self.assertEqual(before, self.snapshot())
        self.run_sync()
        self.assertEqual(self.run_sync(check=True)[0], 0)
        self.assertFalse((mirror / 'stale.md').exists())

    def test_missing_mirror_check_does_not_create_it(self):
        before = self.snapshot()
        self.assertEqual(self.run_sync(check=True)[0], 1)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / '.agents').exists())

    def test_empty_source_refused_and_unrelated_skills_preserved(self):
        self.run_sync()
        other = self.root / '.agents/skills/another-skill/SKILL.md'
        other.parent.mkdir()
        other.write_text('keep\n')
        (self.source / 'SKILL.md').unlink()
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.run_sync()
        self.assertEqual(before, self.snapshot())
        (self.source / 'SKILL.md').write_text('new\n')
        self.run_sync()
        self.assertEqual(other.read_text(), 'keep\n')

    def test_symlink_preflight_prevents_partial_update(self):
        self.run_sync()
        first = self.root / MIRRORS[0] / 'SKILL.md'
        first.write_text('drift\n')
        second = self.root / MIRRORS[1] / 'references/a.md'
        second.unlink()
        second.symlink_to(self.source / 'references/a.md')
        with self.assertRaises(ValueError):
            self.run_sync()
        self.assertEqual(first.read_text(), 'drift\n')
        self.assertEqual((self.source / 'references/a.md').read_text(), 'reference\n')

    def test_file_directory_shape_change(self):
        self.run_sync()
        (self.source / 'references/a.md').unlink()
        (self.source / 'references').rmdir()
        (self.source / 'references').write_text('now a file\n')
        self.run_sync()
        self.assertEqual(self.run_sync(check=True)[0], 0)
        (self.source / 'references').unlink()
        (self.source / 'references').mkdir()
        (self.source / 'references/new.md').write_text('new\n')
        self.run_sync()
        self.assertEqual(self.run_sync(check=True)[0], 0)

    def test_installed_skill_links_resolve_for_every_assistant(self):
        repo = Path(__file__).resolve().parents[1]
        for harness, prefix in [('opencode', '.opencode'), ('claude', '.claude'), ('codex', '.agents')]:
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as target:
                subprocess.run(['bash', str(repo / 'scripts/install.sh'), '--harness', harness,
                                '--target', target], check=True, capture_output=True)
                skill = Path(target) / prefix / 'skills/jvm-spark-migration'
                for file in skill.rglob('*.md'):
                    for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                        if '://' not in link and not link.startswith('#'):
                            self.assertTrue((file.parent / link.split('#')[0]).is_file(), (file, link))


if __name__ == '__main__':
    unittest.main()
