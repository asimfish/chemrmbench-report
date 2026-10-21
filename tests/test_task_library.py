import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import task_library as module


class RuntimeProjection(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.patch=patch.object(module,'ROOT',self.root);self.patch.start()
    def tearDown(self):self.patch.stop();self.temp.cleanup()
    def collection(self,name,statuses,warning=False,planned=None):
        root=self.root/name;root.mkdir()
        (root/'collection.json').write_text(json.dumps({'backend':'isaac','tasks':['pour'],
            'seed0':0,'episodes_per_task':len(statuses) if planned is None else planned}))
        rows=[]
        for seed,status in enumerate(statuses):
            episode=root/'pour'/f'seed_{seed:06d}';episode.mkdir(parents=True)
            (episode/'task.json').write_text('{"hidden_cue":2,"secret":"needle_token"}')
            (episode/'verdict.json').write_text(json.dumps({'safe_success':status=='success','metrics':{'stage_count':8}}))
            log=root/f'seed_{seed}_worker.log';log.write_text('failed to cook GPU-compatible mesh: needle_token HIDDEN_CUE_INDEX=2\n' if warning else '')
            rows.append({'task_id':'pour','seed':seed,'variant':'default','directory':str(episode),
                'status':status,'wall_time_s':1.,'worker_log':str(log),'failure_reasons':[]})
        (root/'manifest.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        return root
    def task(self):return next(r for r in module.collect_task_library()['tasks'] if r['id']=='pour')
    def test_legacy_gpu_error_rejects_success_without_exporting_private_log(self):
        root=self.collection('old',['success'],warning=True)
        data=module.collect_task_library();task=next(t for t in data['tasks'] if t['id']=='pour')
        self.assertEqual(task['successes'],0);self.assertEqual(task['status_counts'],{'error':1})
        self.assertEqual(task['trials'][0]['measured_status'],'success')
        self.assertEqual(json.loads((root/'manifest.jsonl').read_text())['status'],'success')
        for private in ['needle_token','HIDDEN_CUE_INDEX',str(self.root)]:self.assertNotIn(private,json.dumps(data))
    def test_active_repaired_collection_takes_priority_over_old_failure_ratio(self):
        self.collection('active',['fail'],planned=2)
        self.assertEqual(self.task()['status'],'collecting')
    def test_fixed_cohort_is_separate_from_cumulative_historical_attempts(self):
        self.collection('fixed',['success']*16+['fail']*4)
        self.collection('older',['success']*3,warning=True)
        (self.root/'T3_BATCH_REPORT.json').write_text(json.dumps({'seeds':list(range(20)),
            'successes':16,'failures':4,'errors':0,'acceptance_passed':True,
            'unsupported_gpu_geometry_warning_count':0}))
        task=self.task();self.assertEqual(task['dataset_attempts'],23)
        self.assertEqual(task['successes'],16);self.assertEqual(task['status'],'batch_collected')
        self.assertEqual(task['primary_cohort']['successes'],16)
    def test_unavailable_or_external_particle_log_cannot_grant_admission(self):
        root=self.collection('unknown',['success'])
        path=root/'manifest.jsonl';row=json.loads(path.read_text());row['worker_log']='/etc/hostname'
        path.write_text(json.dumps(row)+'\n');task=self.task()
        self.assertEqual(task['successes'],0)
        self.assertIn('particle_runtime_unverified',task['trials'][0]['failure_reasons'])

    def test_ablation_never_inflates_main_dataset_and_unknown_wall_remains_null(self):
        root=self.collection('ablation',['fail'])
        path=root/'manifest.jsonl';row=json.loads(path.read_text());row.update(expert_kind='ablation_no_timing',wall_time_s=None)
        path.write_text(json.dumps(row)+'\n');task=self.task()
        self.assertEqual(task['dataset_attempts'],0)
        self.assertEqual(task['ablation_attempts'],1)
        self.assertEqual(task['ablation_status_counts'],{'fail':1})

    def test_recovered_subset_view_is_not_an_additional_attempt(self):
        root=self.collection('recovered',['success'])
        path=root/'collection.json';config=json.loads(path.read_text());config['collection_kind']='recovered_subset_view';path.write_text(json.dumps(config))
        self.assertEqual(self.task()['dataset_attempts'],0)

    def test_heldout_evaluation_cannot_inflate_development_or_qualification(self):
        root=self.collection('heldout',['success'])
        path=root/'manifest.jsonl';row=json.loads(path.read_text())
        row['collection_purpose']='heldout_evaluation';path.write_text(json.dumps(row)+'\n')
        task=self.task()
        self.assertEqual(task['dataset_attempts'],0)
        self.assertEqual(task['qualification_attempts'],0)
        self.assertEqual(task['evaluation_attempts'],1)

    def test_task_scope_notes_are_public_and_explicit(self):
        tasks={t['id']:t for t in module.collect_task_library()['tasks']}
        self.assertIn('prepress_ready_3mm',tasks['press']['initial_posture_note'])
        self.assertIn('不带温度探头',tasks['timed_stirring']['fixture_note'])
        self.assertIn('站位A',tasks['delayed_cue_memory']['observation_note'])

    def test_t6_native_qualification_stays_separate_from_cpu_and_private_details(self):
        (self.root/'T6_LOCAL_PANEL_CONTACT_DECISION.json').write_text(json.dumps({'approved_by':'explicit user reply','private_path':'needle_token'}))
        directory=self.root/'t6_guidance6_approved_panel_preflight';directory.mkdir()
        (directory/'preflight.json').write_text(json.dumps({'passed':True,'results':[{'passed':True,'minimum_lower_bound_m':.012}]}))
        (self.root/'T6_GUIDANCE6_QUALIFICATION_REPORT.json').write_text(json.dumps({'passed':False,
            'attempts':[{'passed':False,'raw_global_robot_peak_n':30.,'directory':'needle_token'}]}))
        value=module.t6_qualification_projection()
        self.assertTrue(value['whole_scene_transit_screen_passed'])
        self.assertFalse(value['all_native_qualifications_passed'])
        self.assertEqual(value['native_passed'],0)
        self.assertEqual(value['maximum_raw_global_force_n'],30.)
        self.assertNotIn('needle_token',json.dumps(value))

    def test_superseded_press_cannot_count_towards_active_revision(self):
        root=self.collection('t4_twenty_seed_r2',['success']*20)
        config=json.loads((root/'collection.json').read_text());config['tasks']=['press']
        (root/'collection.json').write_text(json.dumps(config))
        rows=[json.loads(s) for s in (root/'manifest.jsonl').read_text().splitlines()]
        for row in rows:row['task_id']='press'
        (root/'manifest.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        task=next(t for t in module.collect_task_library()['tasks'] if t['id']=='press')
        self.assertEqual(task['dataset_attempts'],0)
        self.assertEqual(task['task_revision'],'T4-v2')
        self.assertEqual(task['superseded_history']['main_successes'],20)
        self.assertEqual(task['status'],'planned')

    def test_evaluation_projection_exports_counts_without_split_answers_or_paths(self):
        root=self.root/'step6_f0_paused';root.mkdir()
        (root/'metrics.json').write_text(json.dumps({'hidden_cue':'needle_token','policies':{
            'public_heuristic':{'tasks':{'press':{'attempts':50,'successes':50,'cue_time':4.}}}}}))
        value=module.evaluation_projection()
        press=next(r for r in value['f0_cpu_contracts'] if r['task_id']=='press')
        self.assertEqual(press['public_heuristic'],{'attempts':50,'successes':50})
        for private in ['needle_token','cue_time',str(root)]:self.assertNotIn(private,json.dumps(value))

if __name__=='__main__':unittest.main()
