"""Installer scope tests isolated from the real user's configuration."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

INSTALLER = Path(__file__).resolve().parents[1] / 'scripts/install.sh'


class InstallScopeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='installer scope ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'user'
        self.project = self.root / 'project'
        self.home.mkdir()
        self.project.mkdir()
        self.env = dict(os.environ, HOME=str(self.home))
        self.env.pop('XDG_CONFIG_HOME', None)
        self.env.pop('CLAUDE_CONFIG_DIR', None)

    def run_installer(self, harness='opencode', *args, success=True):
        result = subprocess.run(['bash', str(INSTALLER), '--harness', harness, *args],
                                cwd=self.project, env=self.env, text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_global_lifecycle_and_local_modification_protection(self):
        for harness, folder in [('opencode', '.config/opencode'), ('claude', '.claude'), ('codex', '.agents')]:
            with self.subTest(harness=harness):
                base = self.home / folder
                self.run_installer(harness, '--scope', 'global', '--dry-run')
                self.assertFalse(base.exists())
                self.run_installer(harness, '--scope', 'global')
                skill = base / 'skills/jvm-spark-migration/SKILL.md'
                original = skill.read_bytes()
                self.assertTrue((base / '.jvm-migration' / (harness + '.manifest')).is_file())
                self.assertTrue((skill.parent / 'references/spring-migration.md').is_file())
                self.run_installer(harness, '--scope', 'global', '--action', 'update')
                skill.write_bytes(original + b'local change\n')
                for action in ('update', 'uninstall'):
                    self.run_installer(harness, '--scope', 'global', '--action', action, success=False)
                    self.assertEqual(skill.read_bytes(), original + b'local change\n')
                skill.write_bytes(original)
                keep = base / 'unrelated.txt'
                keep.write_text('keep')
                self.run_installer(harness, '--scope', 'global', '--action', 'uninstall')
                self.assertFalse(skill.exists())
                self.assertEqual(keep.read_text(), 'keep')
                self.assertFalse(any(self.project.iterdir()))

    def test_default_current_project_and_global_are_independent(self):
        self.run_installer()
        local = self.project / '.opencode/skills/jvm-spark-migration/SKILL.md'
        self.assertTrue(local.exists())
        self.run_installer('opencode', '--scope', 'global')
        global_skill = self.home / '.config/opencode/skills/jvm-spark-migration/SKILL.md'
        self.run_installer('opencode', '--scope', 'project', '--action', 'uninstall')
        self.assertFalse(local.exists())
        self.assertTrue(global_skill.exists())
        self.run_installer('opencode', '--scope', 'global', '--action', 'uninstall')

    def test_custom_config_paths_outside_home(self):
        self.env['XDG_CONFIG_HOME'] = str(self.root / 'xdg config')
        self.env['CLAUDE_CONFIG_DIR'] = str(self.root / 'claude config')
        for harness, base in [('opencode', self.root / 'xdg config/opencode'),
                              ('claude', self.root / 'claude config')]:
            self.run_installer(harness, '--scope', 'global')
            self.assertTrue((base / 'skills/jvm-spark-migration/SKILL.md').exists())
            self.run_installer(harness, '--scope', 'global', '--action', 'uninstall')

    def test_reject_ambiguous_scope_and_invalid_path(self):
        self.run_installer('opencode', '--scope', 'global', '--target', str(self.project), success=False)
        self.run_installer('opencode', '--scope', 'system', success=False)
        self.env['XDG_CONFIG_HOME'] = 'relative'
        self.run_installer('opencode', '--scope', 'global', success=False)
        self.assertFalse(any(self.home.iterdir()))
        self.assertFalse(any(self.project.iterdir()))

    def test_global_symlink_ancestor_refused_without_writes(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.home / '.config').symlink_to(outside, target_is_directory=True)
        self.run_installer('opencode', '--scope', 'global', success=False)
        self.assertFalse(any(outside.iterdir()))

    def test_manifest_cannot_escape_selected_configuration(self):
        self.run_installer('opencode', '--scope', 'global')
        victim = self.root / 'unrelated.txt'
        victim.write_text('preserve')
        import hashlib
        digest = hashlib.sha256(victim.read_bytes()).hexdigest()
        manifest = self.home / '.config/opencode/.jvm-migration/opencode.manifest'
        with manifest.open('a') as stream:
            stream.write(digest + '\t' + str(victim).lstrip('/') + '\n')
        self.run_installer('opencode', '--scope', 'global', '--action', 'uninstall', success=False)
        self.assertEqual(victim.read_text(), 'preserve')

    def test_unmanaged_global_conflict_preserved(self):
        command = self.home / '.config/opencode/commands/audit.md'
        command.parent.mkdir(parents=True)
        command.write_text('user command')
        self.run_installer('opencode', '--scope', 'global', success=False)
        self.assertEqual(command.read_text(), 'user command')
        self.assertFalse((self.home / '.config/opencode/skills').exists())


if __name__ == '__main__':
    unittest.main()
