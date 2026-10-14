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

    def test_registered_live_baselines_show_activity_without_parent_or_restart_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'v94';raw.mkdir()
            config={'experiment_root':str(exp),'development_checks':[{'id':'V94','path':str(raw),'phases':['live_a','live_b']}]}
            (raw/'live_a_running.json').write_text(json.dumps({'pid':12345}))
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                active=live_runs(config)
            self.assertEqual(len(active),1)
            self.assertEqual(active[0]['id'],'V94')
            self.assertEqual(active[0]['state'],'collecting')
            self.assertEqual(active[0]['planned_stages'],2)
            self.assertEqual([s['label'] for s in active[0]['stages']],['连续运行基线 A','连续运行基线 B'])
            self.assertEqual(active[0]['committed_stages'],0)
            self.assertNotIn('scientific_admission',active[0])
            (raw/'live_a_resource.json').write_text('{}')
            self.assertEqual(live_runs(config),[])

    def test_same_process_progress_does_not_promote_failed_endpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'v95';raw.mkdir();(raw/'live_control').mkdir()
            (raw/'same_process_restore').mkdir()
            (raw/'live_control_running.json').write_text(json.dumps({'pid':12345}))
            (raw/'live_control_resource.json').write_text('{}')
            (raw/'live_control/RESULT.json').write_text('{}')
            (raw/'same_process_restore_running.json').write_text(json.dumps({'pid':12345}))
            (raw/'same_process_restore/ERROR.json').write_text('{}')
            config={'experiment_root':str(exp),'development_checks':[{'id':'V95','path':str(raw),'phases':['live_control','same_process_restore']}]}
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)[0]
            self.assertEqual(result['committed_stages'],1)
            self.assertEqual([s['label'] for s in result['stages']],['不中断物理对照','同进程状态恢复对照'])
            self.assertFalse(result['stages'][1]['committed'])
            self.assertNotIn('physical_restart_admitted',result)
            (raw/'same_process_restore_resource.json').write_text('{}')
            self.assertEqual(live_runs(config),[])

    def test_video_pair_tracks_the_live_worker_and_retains_failed_write_condition(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'v97';raw.mkdir()
            (raw/'live').mkdir();(raw/'single_pose').mkdir()
            config={'experiment_root':str(exp),'development_checks':[{'id':'V97','path':str(raw),'phases':['live','single_pose']}]}
            atomic_json(raw/'live_running.json',{'pid':12345})
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                self.assertEqual(live_runs(config)[0]['committed_stages'],0)
            atomic_json(raw/'live_resource.json',{'exit_code':0})
            atomic_json(raw/'live/RESULT.json',{'status':'PASS_NATIVE_SINGLE_POSE_VIDEO_CONTROL'})
            atomic_json(raw/'single_pose_running.json',{'pid':12345})
            atomic_json(raw/'single_pose/ERROR.json',{'status':'FAIL_MATCHED_NEXT_STAGE_ENDPOINT'})
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                active=live_runs(config)[0]
            self.assertEqual(active['committed_stages'],1)
            self.assertFalse(active['stages'][1]['committed'])
            self.assertNotIn('scientific_admission',active)
            self.assertNotIn('physical_restart_admitted',active)
            atomic_json(raw/'single_pose_resource.json',{'exit_code':1})
            self.assertEqual(live_runs(config),[])

    def test_single_video_refusal_never_counts_as_a_committed_task(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'v96';raw.mkdir();(raw/'single_pose').mkdir()
            config={'experiment_root':str(exp),'development_checks':[{'id':'V96','path':str(raw),'phases':['single_pose']}]}
            atomic_json(raw/'single_pose_running.json',{'pid':12345})
            atomic_json(raw/'single_pose/ERROR.json',{'status':'REFUSED_PREINTERVENTION_SOURCE_IDENTITY'})
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                self.assertEqual(live_runs(config)[0]['committed_stages'],0)
            atomic_json(raw/'single_pose_resource.json',{'exit_code':1})
            self.assertEqual(live_runs(config),[])

    def test_balanced_repeats_track_declared_order_and_never_promote_failed_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'v98';raw.mkdir()
            phases=['r1_no_write','r1_read_only_sham','r1_single_pose_write','r2_read_only_sham',
                    'r2_single_pose_write','r2_no_write','r3_single_pose_write','r3_no_write','r3_read_only_sham']
            config={'experiment_root':str(exp),'development_checks':[{'id':'V98','path':str(raw),'phases':phases}]}
            for name in phases[:3]:
                (raw/name).mkdir();atomic_json(raw/(name+'_running.json'),{'pid':12345})
            for name in phases[:2]:
                atomic_json(raw/name/'RESULT.json',{'status':'PASS_NATIVE_REPEATED_TRANSPORT'})
                atomic_json(raw/(name+'_resource.json'),{'exit_code':0})
            atomic_json(raw/'r1_single_pose_write/ERROR.json',{'status':'FAIL_MATCHED_ENDPOINT'})
            with patch('pathlib.Path.read_bytes',return_value=str(raw).encode()):
                active=live_runs(config)[0]
            self.assertEqual(active['planned_stages'],9);self.assertEqual(active['committed_stages'],2)
            self.assertFalse(active['stages'][2]['committed']);self.assertIn('第3轮',active['stages'][6]['label'])
            self.assertEqual(active['stages'][2]['outcome'],'native_failed')
            self.assertNotIn('scientific_admission',active)
            atomic_json(raw/'r1_single_pose_write_resource.json',{'exit_code':1})
            self.assertEqual(live_runs(config),[])

    def test_native_outcome_extension_is_typed_and_cannot_promote_failure(self):
        data=copy.deepcopy(self.public);stage=data['latest']['stages'][0]
        stage['outcome']='native_pass';stage['committed']=True
        validate_public(data)
        for value in ['independent_pass','/mnt/private/log',None]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                broken=copy.deepcopy(data);broken['latest']['stages'][0]['outcome']=value;validate_public(broken)
        broken=copy.deepcopy(data);broken['latest']['stages'][0]['outcome']='native_failed'
        with self.assertRaises(ValueError):validate_public(broken)

    def test_namespace_working_root_requires_an_exact_registered_allowlist(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);exp=base/'archive';exp.mkdir();a=exp/'cohort';a.mkdir();working=base/'working';working.mkdir()
            atomic_json(working/'r1_no_write_running.json',{'pid':12345})
            phases=['r1_no_write','r1_read_only_sham','r1_single_pose_write','r2_read_only_sham','r2_single_pose_write','r2_no_write','r3_single_pose_write','r3_no_write','r3_read_only_sham']
            c={'experiment_root':str(exp),'development_checks':[{'id':'V98-R2','path':str(a),'working_path':str(working),'phases':phases}]}
            with self.assertRaises(ValueError):live_runs(c)
            c['working_root_allowlist']=[str(working)]
            with patch('pathlib.Path.read_bytes',return_value=str(working).encode()):self.assertEqual(live_runs(c)[0]['id'],'V98-R2')

    def test_single_cold_child_progress_uses_nested_output_without_granting_archive_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            exp=Path(temporary);raw=exp/'trial';raw.mkdir();(raw/'parent').mkdir()
            atomic_json(raw/'parent_running.json',{'pid':12345})
            atomic_json(raw/'parent_resource.json',{'exit_code':0})
            atomic_json(raw/'parent/RESULT.json',{'status':'BASELINE_COMMANDS_COMPLETED'})
            child=raw/'branches/no_fault/child_first';child.mkdir(parents=True)
            atomic_json(raw/'no_fault_first_running.json',{'pid':12345})
            config={'experiment_root':str(exp),'development_checks':[{'id':'V92','path':str(raw),'phases':['parent','no_fault_first']}]}
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)[0]
            self.assertEqual(result['planned_stages'],2)
            self.assertEqual(result['committed_stages'],1)
            self.assertFalse(result['stages'][1]['committed'])
            atomic_json(child/'RESULT.json',{'status':'BASELINE_COMMANDS_COMPLETED'})
            with patch('export_dashboard.Path.read_bytes',return_value=str(raw).encode()):
                result=live_runs(config)[0]
            self.assertEqual(result['committed_stages'],2)
            self.assertNotIn('physical_restart_admitted',result)

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
