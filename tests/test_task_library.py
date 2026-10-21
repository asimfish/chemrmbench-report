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
        self.ssd_patch=patch.object(module,'SSD',self.root/'ssd');self.ssd_patch.start()
    def tearDown(self):self.ssd_patch.stop();self.patch.stop();self.temp.cleanup()
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
    def test_latest_t6_tracking_stop_is_distinct_from_startup_error_and_private_text(self):
        folder=self.root/'guidance8_t6';folder.mkdir()
        (folder/'qualification_report.json').write_text(json.dumps({'guidance':8,'passed':False,'attempts':[
            {'status':'error','task_actions_executed':1938,'passed':False,
             'error':'T6_PATH_TRACKING_BUDGET:pregrasp_refine:start_geometry_error_m=0.001383 needle_token'}]}))
        projection=module.current_t6_projection()
        self.assertEqual(projection['guidance'],8)
        self.assertEqual(projection['native_startup_errors'],0)
        self.assertEqual(projection['native_tracking_stops'],1)
        self.assertEqual(projection['maximum_start_tracking_error_mm'],1.383)
        self.assertNotIn('needle_token',json.dumps(projection))
    def test_guidance9_queued_control_round_does_not_reuse_prior_native_pass_or_error(self):
        prior=self.root/'guidance8_t6';prior.mkdir()
        (prior/'qualification_report.json').write_text(json.dumps({'guidance':8,'attempts':[
            {'passed':False,'error':'T6_PATH_TRACKING_BUDGET:private needle_token'}]}))
        latest=self.root/'ssd/guidance9_t6/round1';latest.mkdir(parents=True)
        (latest/'progress.json').write_text(json.dumps({'phase':'waiting_for_existing_GPU_queue','directory':'needle_token'}))
        value=module.current_t6_projection()
        self.assertEqual(value['guidance'],9);self.assertEqual(value['native_attempts'],0)
        self.assertEqual(value['native_tracking_stops'],0);self.assertEqual(value['prior_tracking_stops'],1)
        self.assertEqual(value['boundary_convergence_mm'],.5)
        self.assertFalse(value['native_all_passed']);self.assertNotIn('needle_token',json.dumps(value))

    def test_second_round_stop_loss_exports_only_bounded_boundary_metrics(self):
        folder=self.root/'ssd/guidance9_t6/round2';folder.mkdir(parents=True)
        (folder/'progress.json').write_text(json.dumps({'phase':'STOP_LOSS_TWO_ROUNDS_USED'}))
        (folder/'qualification_report.json').write_text(json.dumps({'attempts':[
            {'status':'error','passed':False,'task_actions_executed':8684,
             'error':'T6_BOUNDARY_CONVERGENCE:retreat:geometry_error_m=0.000039,tcp_error_m=0.004195,orientation_error_rad=0.000055 needle_token'}]}))
        value=module.current_t6_projection()
        self.assertTrue(value['stop_loss_reached']);self.assertEqual(value['control_iteration'],2)
        self.assertEqual(value['native_boundary_stops'],1)
        self.assertAlmostEqual(value['maximum_boundary_tcp_error_mm'],4.195)
        self.assertNotIn('needle_token',json.dumps(value))

    def test_verifier_audit_exports_counts_without_paths_or_hidden_details(self):
        root=self.root/'verifier_audit_guidance12';root.mkdir()
        (root/'audit.json').write_text(json.dumps({'secret':'needle_token','tasks':{
            'bottle_balance':{'rows':[{'seed':0,'old_new_agreement':True,'metadata_invariant':True,
                'directory':'/private/needle_token','measured_verdict':{'hidden_cue':2}}]}}}))
        value=module.release_projection()
        entry=next(t for t in value['verifier_audit'] if t['task_id']=='bottle_balance')
        self.assertEqual(entry['attempts'],1);self.assertEqual(entry['metadata_invariant'],1)
        self.assertEqual(value['formal_baseline_tasks'],['pick_place','open_cabinet','endpoint_stop'])
        self.assertNotIn('needle_token',json.dumps(value));self.assertNotIn('hidden_cue',json.dumps(value))

    def test_release_scope_keeps_t6_as_history_and_filters_private_table_fields(self):
        p=self.root/'release_v0_1';p.mkdir()
        (p/'public_main_table.json').write_text(json.dumps({'state':'candidate','secret':'needle_token',
            'tasks':[{'task_id':'pick_place','policies':{'expert':{'attempts':20,'successes':19,
                'expected_attempts':20,'complete':True,'success_wilson95':[.76,.99],
                'source_path':str(p),'failure_reasons':{'needle_token':1}}}}]}))
        data=module.collect_task_library()
        self.assertEqual(len(data['release']['active_tasks']),7)
        t6=next(t for t in data['tasks'] if t['id']=='timed_stirring')
        self.assertFalse(t6['release_in_v0_1']);self.assertEqual(t6['status'],'deferred')
        self.assertNotIn('needle_token',json.dumps(data));self.assertNotIn(str(p),json.dumps(data))

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
        self.assertTrue(press['superseded']);self.assertEqual(press['task_revision'],'T4-v1')
        for private in ['needle_token','cue_time',str(root)]:self.assertNotIn(private,json.dumps(value))

    def test_training_progress_never_exports_hostnames_or_private_paths(self):
        p=self.root/'remote_training/guidance7_training_expansion';p.mkdir(parents=True)
        (p/'progress.json').write_text(json.dumps({'private_path':str(p),
            'by_task_host_status_admission':[{'task_id':'pick_place','runtime_host':'needle_token',
                'status':'success','training_admitted':True,'attempts':4}]}))
        result=module.training_expansion_projection()
        self.assertEqual(result['received_and_validated_attempts'],4)
        self.assertFalse(result['main_table_eligible'])
        for private in ['needle_token',str(p)]:self.assertNotIn(private,json.dumps(result))

    def test_ssd_staging_is_separate_from_admitted_counts_and_exports_no_trial_truth(self):
        p=self.root/'ssd/t4_v2_twenty_seed';p.mkdir(parents=True)
        (p/'collection.json').write_text(json.dumps({'backend':'isaac','episodes_per_task':20}))
        (p/'manifest.jsonl').write_text(json.dumps({'status':'success','directory':str(p),'hidden_cue':'needle_token'})+'\n')
        value=module.collect_task_library()
        self.assertEqual(value['dataset_attempts'],0)
        self.assertEqual(value['ssd_staging']['cohorts'][0]['closed_attempts'],1)
        self.assertEqual(value['ssd_staging']['cohorts'][0]['mirrored_closed_attempts'],0)
        for private in ['needle_token',str(p)]:self.assertNotIn(private,json.dumps(value))

    def test_native_segments_are_deduplicated_and_revision_labels_stay_separate(self):
        for name,kind,seed,revision in [
            ('t7_public_retained_1000_1002','view',1000,None),
            ('t7_public_retained_1003','view',1003,None),
            ('step6_native_t7_paused_ssd','heldout_evaluation',1004,None),
            ('step6_native_t7_guidance10_remaining','heldout_evaluation',1026,None),
            ('step6_native_t4_paused','heldout_evaluation',1000,'T4-v1'),
            ('step6_native_t4_v2_paused_ssd','heldout_evaluation',1000,'T4-v2'),
            ('step6_native_t4_v2_guidance10_remaining','heldout_evaluation',1005,'T4-v2')]:
            p=self.root/name;p.mkdir()
            task='press' if revision else 'endpoint_stop'
            (p/'collection.json').write_text(json.dumps({'collection_kind':kind}))
            row={'task_id':task,'seed':seed,'expert_kind':'evaluation_public_heuristic',
                 'status':'success','hidden_answer':'needle_token','directory':str(p)}
            (p/'manifest.jsonl').write_text(json.dumps(row)+'\n')
        data=module.evaluation_projection()
        native=data['native_public_observation']
        self.assertEqual(next(r for r in native if r['task_id']=='endpoint_stop')['attempts'],4)
        press=[r for r in native if r['task_id']=='press']
        self.assertEqual({r['task_revision'] for r in press},{'T4-v1','T4-v2'})
        self.assertEqual(next(r for r in press if r['task_revision']=='T4-v2')['attempts'],2)
        self.assertEqual(sum(r['superseded'] for r in press),1)
        self.assertNotIn('needle_token',json.dumps(data));self.assertNotIn(str(self.root),json.dumps(data))

if __name__=='__main__':unittest.main()
