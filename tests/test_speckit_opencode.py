import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.speckit_opencode import STAGES, TOOLKIT_VERSION


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/speckit_opencode.py"
FAKE = r'''
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
stage = args[args.index('--command') + 1].split('.')[-1]
root = Path.cwd()
with open(os.environ['FAKE_LEDGER'], 'a') as log:
    log.write(json.dumps({'args': args, 'cwd': str(root), 'feature': os.environ.get('SPECIFY_FEATURE_DIRECTORY')})+'\n')
mode = os.environ.get('FAKE_MODE', '') if stage == os.environ.get('FAKE_STAGE', stage) else ''
if mode == 'nonzero':
    sys.exit(7)
if mode == 'error':
    print(json.dumps({'type': 'error', 'error': {'message': 'provider failure'}}))
    sys.exit(0)
if mode == 'timeout':
    time.sleep(30)
if mode == 'badjson':
    print('not JSON')
    sys.exit(0)
if mode == 'empty':
    sys.exit(0)
feature = root / os.environ.get('SPECIFY_FEATURE_DIRECTORY', 'specs/unused')
if mode != 'missing':
    if stage == 'constitution':
        target = root / '.specify/memory/constitution.md'
    elif stage in ('specify', 'plan', 'tasks'):
        target = feature / {'specify': 'spec.md', 'plan': 'plan.md', 'tasks': 'tasks.md'}[stage]
    else:
        target = None
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('# '+stage+'\n'+('[NEEDS CLARIFICATION: contract]' if mode == 'clarification' else 'Reviewed content'))
print(json.dumps({'type': 'text', 'part': {'text': 'stage returned'}}))
'''


class SpecKitOpenCodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "application with spaces"
        self.project.mkdir()
        commands = self.project / ".opencode/commands"
        commands.mkdir(parents=True)
        for stage in STAGES:
            (commands / ("speckit." + stage + ".md")).write_text("Run " + stage)
        constitution = self.project / ".specify/memory/constitution.md"
        constitution.parent.mkdir(parents=True)
        constitution.write_text("# Approved project principles\nPreserve behavior.")
        self.bin = self.base / "bin"
        self.bin.mkdir()
        fake = self.bin / "opencode"
        fake.write_text("#!" + sys.executable + "\n" + FAKE)
        fake.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update(PATH=str(self.bin)+os.pathsep+self.env['PATH'], FAKE_LEDGER=str(self.base/'calls.jsonl'))
        self.spec = self.base / "spec input.md"
        self.spec.write_text("Preserve the application's critical library behavior.")
        self.plan = self.base / "plan input.md"
        self.plan.write_text("Reuse tests and add only missing assertions.")
        self.feature = "specs/006-regressions"

    def invoke(self, *args, global_args=()):
        return subprocess.run([sys.executable, str(SCRIPT), '--project', str(self.project),
                               *global_args, *args], env=self.env, capture_output=True, text=True, timeout=10)

    def prepare(self, **kwargs):
        return self.invoke('prepare', '--feature', self.feature, '--spec-file', str(self.spec),
                           '--plan-file', str(self.plan), **kwargs)

    def reports(self):
        return [json.loads(p.read_text()) for p in self.project.glob('.jvm-migration/speckit-runs/*/report.json')]

    def calls(self):
        p = self.base/'calls.jsonl'
        return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []

    def test_prepare_routes_commands_and_feature_without_implementation(self):
        self.env['SPECIFY_FEATURE_DIRECTORY'] = 'specs/unrelated'
        p = self.prepare(global_args=('--model', 'provider/model'))
        self.assertEqual(p.returncode, 0, p.stderr)
        calls = self.calls()
        self.assertEqual([c['args'][2] for c in calls], ['speckit.'+s for s in ('specify','plan','tasks','analyze')])
        for call in calls:
            self.assertEqual(call['cwd'], str(self.project))
            self.assertEqual(call['feature'], self.feature)
            self.assertIn('provider/model', call['args'])
            self.assertNotIn('--auto', call['args'])
        report = self.reports()[0]
        self.assertEqual(report['status'], 'RETURNED_REVIEW_REQUIRED')
        self.assertEqual(report['toolkit_version'], TOOLKIT_VERSION)
        self.assertTrue(report['review_required'])
        self.assertEqual(len(report['steps']), 4)
        self.assertIn(self.feature+'/tasks.md', report['steps'][2]['artifacts_after'])

    def test_dry_run_does_not_launch_or_write(self):
        p = self.prepare(global_args=('--dry-run',))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(json.loads(p.stdout)['commands']), 4)
        self.assertEqual(self.calls(), [])
        self.assertFalse((self.project/'.jvm-migration').exists())
        self.assertFalse((self.project/'specs').exists())

    def test_input_is_one_argument_not_shell_code(self):
        marker = self.base/'should-not-exist'
        text = '-x "quoted"\n$(touch '+str(marker)+') `echo nope`'
        self.spec.write_text(text)
        p = self.prepare()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(self.calls()[0]['args'][-1].endswith(text))
        self.assertFalse(marker.exists())

    def test_provider_error_event_even_with_zero_exit_stops_pipeline(self):
        self.env.update(FAKE_MODE='error', FAKE_STAGE='plan')
        p = self.prepare()
        self.assertEqual(p.returncode, 2)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(self.reports()[0]['status'], 'FAILED')

    def test_process_failure_stops_pipeline(self):
        self.env.update(FAKE_MODE='nonzero', FAKE_STAGE='plan')
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(self.reports()[0]['steps'][-1]['exit_code'], 7)

    def test_missing_artifact_is_not_success(self):
        self.env.update(FAKE_MODE='missing')
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.reports()[0]['status'], 'FAILED')

    def test_malformed_and_empty_output_are_not_success(self):
        for mode in ('badjson', 'empty'):
            with self.subTest(mode=mode):
                self.env['FAKE_MODE'] = mode
                p = self.invoke('run','constitution','--input-file',str(self.spec))
                self.assertEqual(p.returncode, 2)
        self.assertTrue(all(r['status']=='FAILED' for r in self.reports()))

    def test_timeout_is_reported_and_stops(self):
        self.env.update(FAKE_MODE='timeout')
        p = self.prepare(global_args=('--timeout','0.2'))
        self.assertEqual(p.returncode, 2)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.reports()[0]['status'], 'FAILED')

    def test_existing_feature_is_not_automatically_replayed(self):
        target=self.project/self.feature/'spec.md'
        target.parent.mkdir(parents=True)
        target.write_text('Keep this specification')
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(self.calls(), [])
        self.assertEqual(target.read_text(), 'Keep this specification')

    def test_prerequisites_are_checked_before_launch(self):
        p=self.invoke('run','implement','--feature',self.feature)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_explicit_implementation_uses_selected_feature(self):
        feature=self.project/self.feature
        feature.mkdir(parents=True)
        for name in ('spec.md','plan.md','tasks.md'):
            (feature/name).write_text('# Reviewed '+name)
        p=self.invoke('run','implement','--feature',self.feature)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.calls()[0]['args'][2], 'speckit.implement')

    def test_clarifications_stop_before_planning(self):
        self.env.update(FAKE_MODE='clarification',FAKE_STAGE='specify')
        p=self.prepare()
        self.assertEqual(p.returncode, 2)
        self.assertIn('NEEDS CLARIFICATION',p.stderr)
        self.assertEqual(len(self.calls()),1)

    def test_constitution_template_is_rejected(self):
        (self.project/'.specify/memory/constitution.md').write_text('# [PROJECT_NAME] Constitution')
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_feature_and_log_symlink_escape_rejected(self):
        outside=self.base/'outside'
        outside.mkdir()
        (self.project/'specs').symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.prepare().returncode, 2)
        (self.project/'specs').unlink()
        (self.project/'.jvm-migration').symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_traversal_feature_rejected(self):
        self.feature='specs/../../outside'
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_init_refuses_existing_scaffolding(self):
        p=self.invoke('init')
        self.assertEqual(p.returncode, 2)
        self.assertIn('already exists',p.stderr)

    def test_init_dry_run_uses_supported_spec_kit_flags(self):
        fresh=self.base/'fresh'
        fresh.mkdir()
        self.project=fresh
        p=self.invoke('init',global_args=('--dry-run',))
        self.assertEqual(p.returncode,0,p.stderr)
        command=json.loads(p.stdout)['commands'][0]
        self.assertEqual(command[:5],['specify','init','--here','--integration','opencode'])
        self.assertIn('--non-interactive',command)
        self.assertEqual(list(fresh.iterdir()),[])


if __name__ == '__main__':
    unittest.main()
