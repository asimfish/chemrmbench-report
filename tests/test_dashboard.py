import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from dashboard_io import atomic_json, digest, read_json, validate_public, within
from export_dashboard import collect, stages, live_runs
from publish_dashboard import publish


class PublicBoundary(unittest.TestCase):
    def setUp(self):
        self.public = read_json(Path(__file__).resolve().parents[1] / 'data/collection.json')

    def test_current_snapshot_roundtrip(self):
        self.assertEqual(validate_public(self.public)['latest']['id'], 'V75')
        self.assertEqual(self.public['counts']['qualified_demonstrations'], 0)

    def test_private_fields_and_paths_are_rejected(self):
        for kind in ('unknown', 'nested', 'path'):
            with self.subTest(kind=kind):
                data = copy.deepcopy(self.public)
                if kind == 'unknown':
                    data['raw_prompt'] = 'hidden'
                elif kind == 'nested':
                    data['latest']['package'] = 'hidden'
                else:
                    data['evidence_notes'].append('/mnt/private/run')
                with self.assertRaises(ValueError):
                    validate_public(data)

    def test_development_refresh_cannot_grant_admission(self):
        data = copy.deepcopy(self.public)
        data['latest']['benchmark_complete'] = True
        with self.assertRaises(ValueError):
            validate_public(data)
        data = copy.deepcopy(self.public)
        data['counts']['qualified_demonstrations'] = 1
        with self.assertRaises(ValueError):
            validate_public(data)

    def test_duplicate_nonfinite_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'input.json'
            for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    read_json(path)
            (root / 'link').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                within(root / 'link', root)

    def test_gpu_failure_retains_evidence_without_idle_claim(self):
        latest = copy.deepcopy(self.public['latest'])
        counts = copy.deepcopy(self.public['counts'])
        with patch('export_dashboard.load_closed', return_value=(latest, counts, [], self.public['source_updated_at_utc'])), \
                patch('export_dashboard.gpu_sample', side_effect=OSError()), \
                patch('export_dashboard.live_runs', return_value=[]):
            data = collect({})
        self.assertEqual(data['gpus'], [])
        self.assertEqual(data['collector']['state'], 'degraded')
        self.assertEqual(data['latest']['completion_receipt_sha256'], latest['completion_receipt_sha256'])

    def test_only_contiguous_committed_stages_are_counted(self):
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary)
            root = raw / 'stages'
            root.mkdir()
            header = {'schema': 'chemrm-stage-evidence-v1', 'episode_id': 'synthetic-development',
                      'provenance': {'scope': 'DEVELOPMENT_ONLY'},
                      'training_admitted': False, 'simulation_restart_supported': False,
                      'plan': [{'id': 'a', 'start_tick': 0, 'end_tick': 120},
                               {'id': 'b', 'start_tick': 120, 'end_tick': 180}]}
            atomic_json(root / 'episode.json', header)
            for i, sid in enumerate(('a', 'b')):
                p = root / sid
                p.mkdir()
                m = header['plan'][i] | {'index': i, 'header_sha256': digest(root / 'episode.json'),
                                         'episode_id': header['episode_id']}
                atomic_json(p / 'manifest.json', m)
            atomic_json(root / 'a/COMMITTED.json', {'manifest_sha256': digest(root / 'a/manifest.json')})
            self.assertEqual([s['committed'] for s in stages(raw)], [True, False])
            (root / 'a/COMMITTED.json').unlink()
            atomic_json(root / 'b/COMMITTED.json', {'manifest_sha256': digest(root / 'b/manifest.json')})
            with self.assertRaises(ValueError):
                stages(raw)

    def test_child_refusal_and_retry_progress_preserve_failed_resource_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'trial';raw.mkdir();(raw/'parent').mkdir()
            atomic_json(raw/'parent_running.json',{'pid':12345})
            atomic_json(raw/'parent_resource.json',{'exit_code':0})
            atomic_json(raw/'parent/RESULT.json',{'status':'BASELINE_COMMANDS_COMPLETED'})
            atomic_json(raw/'child_expired_resource.json',{'exit_code':42})
            atomic_json(raw/'child_expired_resource_retry1_running.json',{'pid':12345})
            phases=['parent','child_expired_resource_retry1','child_retry']
            config={'experiment_root':str(exp),'development_checks':[{'id':'V87','path':str(raw),'phases':phases}]}
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)
            self.assertEqual(result[0]['planned_stages'],3)
            self.assertEqual(result[0]['committed_stages'],1)
            self.assertEqual(result[0]['state'],'collecting')
            # The original launch rejection cannot stand in for verified refusal.
            self.assertFalse(result[0]['stages'][1]['committed'])
            atomic_json(raw/'RETRY_GATE.json',{'status':'VERIFIED_EXPIRY_REFUSAL_PARENT_PRESERVED'})
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)
            self.assertEqual(result[0]['committed_stages'],2)
            self.assertEqual(result[0]['stages'][1]['label'],'过期提案拒绝')
            config['development_checks'][0]['phases']=['parent','unregistered']
            with self.assertRaisesRegex(ValueError,'unregistered'):
                live_runs(config)

    def test_stale_snapshot_is_not_republished(self):
        data = copy.deepcopy(self.public)
        data['sampled_at_utc'] = '2000-01-01T00:00:00+00:00'
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'snapshot.json'
            atomic_json(path, data)
            with patch('publish_dashboard.git') as git:
                with self.assertRaisesRegex(ValueError, 'stale'):
                    publish({'site_root': temporary, 'snapshot_path': str(path)})
                git.assert_not_called()

    def test_matched_branches_show_saved_failure_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'trial';raw.mkdir();(raw/'parent').mkdir()
            atomic_json(raw/'parent_running.json',{'pid':12345})
            atomic_json(raw/'parent_resource.json',{'exit_code':0})
            atomic_json(raw/'parent/RESULT.json',{'status':'BASELINE_COMMANDS_COMPLETED'})
            control=raw/'branches/no_fault/child_first';control.mkdir(parents=True)
            atomic_json(control/'RESULT.json',{'status':'BASELINE_COMMANDS_COMPLETED'})
            failed=raw/'branches/recovery/child_first';failed.mkdir(parents=True)
            atomic_json(failed/'task_clock_accounting.json',{'outcome':'FAILED','phase_callbacks':{'RESTORE':30}})
            atomic_json(raw/'recovery_retry_running.json',{'pid':12345})
            phases=['parent','no_fault_first','recovery_first','recovery_retry','expired_first']
            config={'experiment_root':str(exp),'development_checks':[{'id':'V91','path':str(raw),'phases':phases}]}
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)[0]
            self.assertEqual(result['planned_stages'],5)
            self.assertEqual(result['committed_stages'],3)
            self.assertEqual(result['stages'][2]['label'],'可行中断证据保存')
            self.assertFalse(result['stages'][3]['committed'])
            self.assertFalse(result['stages'][4]['committed'])
            # A failed branch that already sent actions cannot be displayed as
            # a zero-tail interruption/refusal boundary.
            atomic_json(failed/'task_clock_accounting.json',{'outcome':'FAILED','phase_callbacks':{'TAIL_COMMANDS':1}})
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)[0]
            self.assertFalse(result['stages'][2]['committed'])

    def test_dirty_checkout_cannot_be_staged_or_pushed(self):
        with tempfile.TemporaryDirectory() as temporary:
            from dashboard_io import utcnow
            data = copy.deepcopy(self.public)
            data['sampled_at_utc'] = utcnow()
            path = Path(temporary) / 'snapshot.json'
            atomic_json(path, data)
            with patch('publish_dashboard.git', side_effect=['main', ' M unrelated.txt']) as git:
                with self.assertRaisesRegex(ValueError, 'dirty'):
                    publish({'site_root': temporary, 'snapshot_path': str(path), 'pages_branch': 'main'})
                self.assertEqual([c.args[1:] for c in git.call_args_list],
                                 [('branch', '--show-current'), ('status', '--porcelain')])


if __name__ == '__main__':
    unittest.main()
