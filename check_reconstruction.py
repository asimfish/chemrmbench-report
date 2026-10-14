"""Public history subset: media identity + explicit reconstruction claim boundaries."""
import hashlib
import json
from pathlib import Path
import re
import math

root=Path(__file__).resolve().parent
data=json.loads((root/'data/reconstruction.json').read_text())
assert data['schema']=='chemrm-preserved-scenes-v1'
assert len(data['scenes'])==6
assert data['history_message_count']==40496
rebuild=data['reconstruction']
for key in ['whole_scene_resume_pass','cold_restart_tested','full_long_chain_tested',
            'liquid_restart_tested','scientific_admission']:
    assert rebuild[key] is False,key
assert rebuild['settled_tracked_bodies']<rebuild['checkpoint_bodies']
assert rebuild['pestle_orientation_drift_deg']>rebuild['original_orientation_limit_deg']
count=0
for scene in data['scenes']:
    assert scene['scientific_admission'] is False
    assert len(scene['views'])==5
    for view in scene['views']:
        for field,extension in [('video','mp4'),('poster','jpg')]:
            value=view[field]
            assert re.fullmatch(r'assets/history/[a-z0-9_-]+\.'+extension,value),value
            p=root/value
            assert p.is_file() and p.resolve().is_relative_to((root/'assets/history').resolve())
            assert hashlib.sha256(p.read_bytes()).hexdigest()==view[field+'_sha256'],value
        assert view['fps']==12 and view['frames']>0
        assert abs(view['frames']/view['fps']-view['duration_s'])<.1
        count+=1
raw=json.dumps(data,ensure_ascii=False)
assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',raw)
native=data.get('native_probe',{})
if native.get('status')=='PASS_SCOPED_RELEASED_RIGID_RECONSTRUCTION':
    assert native['scientific_admission'] is False
    assert native['full_long_task_pass'] is native['bottle_task_pass'] is native['liquid_restart_pass'] is False
    assert native['graceful_sdk_cleanup_pass'] is False
    assert native['cpu_contract_tests']==16 and native['stage_regression_tests']==8
    assert native['receipt']=='artifacts/reconstruction-v78.json'
    receipt_path=root/native['receipt']
    assert hashlib.sha256(receipt_path.read_bytes()).hexdigest()==native['receipt_sha256']
    receipt=json.loads(receipt_path.read_text())
    assert native['same_process']==receipt['phases']['parent']
    assert native['fresh_process']==receipt['phases']['child']
    for phase in receipt['phases'].values():
        assert phase['status']=='PASS_SCOPED_NATIVE_RELEASED_RESTORE'
        assert phase['rigid_objects']==56 and phase['articulations']==9
        assert phase['transient_ticks']==30 and phase['full_registry_each_tick'] is True
        assert phase['initial_observed_velocity_pass'] is True
        assert phase['maximum_position_error_mm']<=1 and phase['maximum_orientation_error_deg']<=.5
        assert phase['maximum_joint_error_rad']<=.0001
        assert phase['skill_scope']=='EMPTY_GRIPPER_CLOSE_OPEN_NO_OBJECT_TASK'
        assert phase['skill_completed'] is True
        assert phase['native_clock_continuous_across_rebuild'] is False
        assert phase['controlled_exit_without_sdk_cleanup'] is True
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(receipt))
    retry=native.get('child_retry')
    if retry:
        assert retry['status']=='PASS_NATIVE_FAILED_CHILD_RETRY'
        assert retry['parent_stage_prefix_preserved'] is retry['parent_checkpoint_preserved'] is True
        assert retry['sealed_parent_stages']==1
        assert retry['scientific_admission'] is retry['full_chemical_long_task_pass'] is False
        assert retry['receipt']=='artifacts/reconstruction-v78-failed-child.json'
        path=root/retry['receipt']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==retry['receipt_sha256']
        detail=json.loads(path.read_text())
        assert detail['parent_stage_prefix_preserved'] is detail['parent_checkpoint_preserved'] is True
        assert detail['phases']['crash']['actual_exit_code']==1
        assert detail['phases']['crash']['actual_failed_skill_steps']==240
        assert detail['phases']['retry']['actual_exit_code']==0
        assert detail['phases']['retry']['actual_completed_skill_steps']==480
        assert detail['full_chemical_long_task_pass'] is detail['graceful_sdk_cleanup_pass'] is False
        assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))
bottle=data.get('bottle_probe')
if bottle:
    assert bottle['status']=='PASS_SCOPED_NATIVE_BOTTLE_PAIR'
    for key in ['scientific_admission','full_benchmark_pass','mid_task_restart_tested','event_memory_evaluated']:
        assert bottle[key] is False,key
    assert bottle['receipt']=='artifacts/bottle-v79.json'
    path=root/bottle['receipt']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==bottle['receipt_sha256']
    detail=json.loads(path.read_text())
    assert detail['phases']==bottle['phases'] and detail['restore']==bottle['restore']
    assert detail['qualified_training_episodes']==detail['astra_model_calls']==0
    for key in ['scientific_admission','training_admission','full_benchmark_pass',
                'mid_task_restart_tested','chemistry_event_verified','event_memory_evaluated',
                'native_clock_continuous_across_rebuild','graceful_sdk_cleanup_pass']:
        assert detail[key] is False,key
    assert detail['pinned_files_verified']==108 and detail['original_helpers_verified']==4
    assert detail['contract_tests_passed']==36
    r=bottle['restore']
    assert r['rigid_objects']==56 and r['articulations']==9 and r['transient_ticks']==30
    assert r['full_registry_each_tick'] is r['all_transient_gates_pass'] is True
    assert r['maximum_position_error_mm']<=1 and r['maximum_orientation_error_deg']<=.5
    assert r['maximum_joint_error_rad']<=.0001
    for phase in ['parent','child']:
        p=bottle['phases'][phase]
        assert p['status']=='PASS_SCOPED_NATIVE_BOTTLE_MECHANISM'
        assert p['commands']==13427 and p['committed_stages']==8 and p['native_rgbd_snapshots']==15
        assert p['state_writes_during_task']==p['penetration_ticks']==0
        assert p['final_return_error_mm']<1 and p['transport_bilateral_contact_fraction']>.99
        assert p['maximum_relative_displacement_mm']<2
        assert len(bottle['frames'][phase])==15
        for frame in bottle['frames'][phase]:
            value=frame['image']
            assert re.fullmatch(r'assets/native-v79/'+phase+r'-[0-9]{5}\.jpg',value)
            assert hashlib.sha256((root/value).read_bytes()).hexdigest()==frame['image_sha256']
        assert p['controlled_exit_without_sdk_cleanup'] is p['owned_process_group_empty'] is True
    assert bottle['phases']['parent']['native_epoch']!=bottle['phases']['child']['native_epoch']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))
mid=data.get('mid_task_probe')
if mid:
    assert mid['status']=='PASS_SCOPED_NATIVE_MID_TASK_BOTTLE_RESUME'
    assert mid['receipt']=='artifacts/bottle-v80-mid-task.json'
    path=root/mid['receipt'];assert hashlib.sha256(path.read_bytes()).hexdigest()==mid['receipt_sha256']
    detail=json.loads(path.read_text())
    for key in ['scientific_admission','training_admission','full_benchmark_pass',
                'event_memory_evaluated','chemical_event_verified','agent_context_restored',
                'native_clock_continuous_across_rebuild','mid_carry_restart_pass',
                'liquid_restart_pass','graceful_sdk_cleanup_pass']:
        assert detail[key] is False,key
    assert detail['pinned_files_verified']==109 and detail['contract_tests_passed']==38
    assert detail['reexecuted_prefix_commands']==0 and detail['astra_model_calls']==0
    assert detail['restored_command_cursor']==7920 and detail['tail_commands']==5507
    assert detail['completed_prefix_stages']==5 and detail['resumed_tail_stages']==3
    assert detail['parent_prefix_preserved'] is detail['parent_checkpoint_preserved'] is detail['controller_context_restored'] is True
    assert detail['release']['status']=='PASS_RELEASED_BOTTLE_BOUNDARY'
    assert detail['release']['loaded_finger_contacts']==0 and detail['release']['sampled_dwell_s']==.5
    assert detail['restore']==mid['restore'] and detail['phases']==mid['phases']
    r=detail['restore'];assert r['all_transient_gates_pass'] is r['full_registry_each_tick'] is True
    assert r['rigid_objects']==56 and r['articulations']==9 and r['transient_ticks']==30
    assert r['maximum_position_error_mm']<=1 and r['maximum_orientation_error_deg']<=.5 and r['maximum_joint_error_rad']<=.0001
    assert detail['phases']['parent']['commands']==7920 and detail['phases']['child']['commands']==5507
    assert detail['phases']['child']['maximum_relative_displacement_mm']<=20
    assert detail['phases']['child']['placement_error_mm']<1
    for frame in mid['frames']:
        value=frame['image'];assert re.fullmatch(r'assets/native-v80/(parent|child)-[0-9]{5}\.jpg',value)
        assert hashlib.sha256((root/value).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))
memory=data.get('memory_probe')
if memory:
    assert memory['status']=='PASS_SCOPED_PRESERVED_OBSERVATION_MEMORY_READOUT'
    assert memory['receipt']=='artifacts/memory-v82.json'
    path=root/memory['receipt'];assert hashlib.sha256(path.read_bytes()).hexdigest()==memory['receipt_sha256']
    detail=json.loads(path.read_text())
    assert detail['readout_cases']==memory['readout_cases']
    assert detail['new_native_trials']==memory['new_native_trials']==0
    assert detail['model_calls']==memory['model_calls']==5
    assert detail['known_billed_tokens']==memory['known_billed_tokens']==56018
    assert detail['cleared_identical_input_called_once'] is detail['current_image_identical_across_readouts'] is True
    assert detail['semantic_memory_bound_to_physical_checkpoint'] is detail['parent_checkpoint_preserved'] is True
    assert detail['old_images_attached_to_resumed_readouts'] is detail['physical_policy_execution_observed'] is False
    assert detail['operation_timing_measured_this_run'] is detail['scientific_admission'] is detail['training_admission'] is False
    assert detail['formal_event_memory_admission'] is False
    assert detail['requested_model']=='gpt-6-astra' and detail['backend_model_id'] is None
    assert detail['cleared_decision']==memory['cleared_decision']=='wait'
    assert [x['selected_deadline_s'] for x in detail['readout_cases']]==[10,16]
    for x in detail['readout_cases']:
        assert x['remembered_public_observation_s']==x['past_public_observation_s']
        assert x['physical_execution_observed'] is False
    assert len(memory['frames'])==3
    for frame in memory['frames']:
        value=frame['image'];assert re.fullmatch(r'assets/native-v82/(past-early|past-late|current)\.jpg',value)
        assert hashlib.sha256((root/value).read_bytes()).hexdigest()==frame['image_sha256']
    assert memory['frames'][-1]['image_sha256']==detail['public_current_image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))
agent=data.get('native_memory_probe')
if agent:
    assert agent['status']=='PASS_SCOPED_NATIVE_AGENT_MEMORY_TIMED_CONTACT'
    assert agent['receipt']=='artifacts/memory-v83-native.json'
    path=root/agent['receipt'];assert hashlib.sha256(path.read_bytes()).hexdigest()==agent['receipt_sha256']
    detail=json.loads(path.read_text())
    assert detail['pinned_files_verified']==113 and detail['contract_tests_passed']==85
    assert detail['model_calls']==agent['model_calls']==3 and detail['known_billed_tokens']==33399
    assert detail['new_native_parent_episodes']==detail['new_native_child_episodes']==1
    assert detail['tail_commands']==agent['tail_commands']==5507 and detail['reexecuted_prefix_commands']==0
    assert detail['parent_checkpoint_preserved'] is detail['parent_prefix_preserved'] is True
    assert detail['agent_semantic_memory_restored'] is detail['physical_policy_execution_observed'] is True
    assert detail['hidden_model_state_restored'] is detail['old_images_attached_to_resumed_readouts'] is False
    assert detail['current_image_identical_across_readouts'] is True
    assert detail['cleared_decision']==agent['cleared_decision']=='wait'
    assert detail['retained_decision']=='schedule'
    assert detail['desired_contact_after_resume_s']==agent['desired_contact_after_resume_s']==16
    assert detail['contact_after_resume_bounds_s']==agent['contact_after_resume_bounds_s']
    assert detail['error_interval_ms']==agent['error_interval_ms']
    assert detail['requested_deadline_pass'] and all(abs(v)<=20 for v in detail['error_interval_ms'])
    assert detail['simulation_paused_for_inference'] is agent['simulation_paused_for_inference'] is True
    assert detail['host_readout_elapsed_s']==agent['host_readout_elapsed_s']
    assert detail['phases']['child']['placement_error_mm']==agent['placement_error_mm']<1
    assert detail['phases']['parent']['commands']==7920 and detail['phases']['child']['commands']==5507
    assert detail['restore']['all_transient_gates_pass'] is detail['restore']['full_registry_each_tick'] is True
    for key in ['scientific_admission','training_admission','formal_event_memory_admission','full_benchmark_pass',
                'chemical_event_verified','independently_calibrated_contact','native_clock_continuous_across_rebuild',
                'mid_carry_restart_pass','liquid_restart_pass','graceful_sdk_cleanup_pass']:
        assert detail[key] is False,key
    assert detail['qualified_training_episodes']==0
    assert len(agent['frames'])==3
    for frame in agent['frames']:
        value=frame['image'];assert re.fullmatch(r'assets/native-v83/(cue|current|finished)\.jpg',value)
        assert hashlib.sha256((root/value).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))
for kind,versions in [('native_memory_conditions',(83,84)),('continuous_timing_probes',(85,86))]:
    pilots=data[kind];assert [p['id'] for p in pilots]==['V'+str(v) for v in versions]
    for p,v in zip(pilots,versions):
        path=root/p['receipt'];assert hashlib.sha256(path.read_bytes()).hexdigest()==p['receipt_sha256']
        detail=json.loads(path.read_text())
        assert p['scientific_admission'] is p['formal_event_memory_admission'] is False
        assert detail['scientific_admission'] is detail['training_admission'] is detail['formal_event_memory_admission'] is False
        for key in ('contact_after_resume_bounds_s','error_interval_ms','desired_contact_after_resume_s','simulation_paused_for_inference','host_readout_elapsed_s'):
            assert p[key]==detail[key],key
        assert detail['parent_prefix_preserved'] and detail['parent_checkpoint_preserved']
        assert detail['restored_command_cursor']==7920 and detail['tail_commands']==5507 and detail['reexecuted_prefix_commands']==0
        assert detail['phases']['child']['placement_error_mm']==p['placement_error_mm']<1
        assert detail['restore']['all_transient_gates_pass'] and detail['restore']['full_registry_each_tick']
        assert detail['native_clock_continuous_across_rebuild'] is detail['chemical_event_verified'] is False
        assert len(p['frames'])==3
        for frame in p['frames']:
            assert re.fullmatch(r'assets/native-v'+str(v)+r'/(cue|current|finished)\.jpg',frame['image'])
            assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
        assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|ssh\s',json.dumps(detail))
        if v<85:
            assert detail['simulation_paused_for_inference'] and detail['requested_deadline_pass']
        else:
            assert detail['pinned_files_verified']==114 and detail['contract_tests_passed']==94
            assert not detail['simulation_paused_for_inference'] and not detail['real_time_speed_assumed']
            assert detail['cleared_readout_mode']=='OFFLINE_AFTER_NATIVE_SHUTDOWN'
            assert p['physical_bottle_mechanics_pass'] is True
            for key in ('native_readout_elapsed_s','physical_callbacks_during_readout','remaining_wait_ticks','readout_ticks_spent_once'):
                assert p[key]==detail[key]
            assert abs(p['native_readout_elapsed_s']-p['physical_callbacks_during_readout']/240)<1e-5
            assert abs(p['actual_skill_start_after_resume_s']-(p['native_readout_elapsed_s']+p['remaining_wait_ticks']/240))<1e-5
            if v==85:
                assert detail['requested_deadline_pass'] and detail['readout_ticks_spent_once']
                assert p['physical_callbacks_during_readout']+p['remaining_wait_ticks']==1159
            else:
                assert detail['status']=='FAIL_SCOPED_NATIVE_AGENT_CONTACT_DEADLINE'
                assert not detail['requested_deadline_pass'] and not detail['readout_ticks_spent_once']
                assert detail['native_delay_explains_timing_error'] and detail['accounted_executor_would_refuse']
                assert p['remaining_wait_ticks']==1159 and all(abs(e)<20 for e in detail['error_minus_readout_ms'])
                assert min(p['error_interval_ms'])>1000
p=data['expiry_recovery_probe'];path=root/p['receipt']
assert hashlib.sha256(path.read_bytes()).hexdigest()==p['receipt_sha256'];r=json.loads(path.read_text())
for key in p:
    if key not in ('receipt','receipt_sha256','frames'):assert p[key]==r[key],key
assert r['status']=='PASS_SCOPED_NATIVE_EXPIRY_REFUSAL_AND_NEW_ATTEMPT_RETRY'
assert r['expired_proposal_refused'] and r['refused_attempt_task_success'] is False
assert r['failed_tail_commands']==r['parent_recollection_commands']==0 and r['retry_tail_commands']==5507
assert r['parent_files_preserved']==45 and r['parent_checkpoint_preserved'] and r['parent_prefix_preserved']
assert r['retry_is_new_attempt'] and r['uninterrupted_chemical_deadline'] is False
assert r['failed_clock_id']!=r['retry_clock_id']
assert r['injected_native_ticks']==1440 and r['injected_delay_s']==6 and r['actual_model_native_ticks']==58
assert r['initial_resource_gate_failure_preserved'] and not r['resource_failure_entered_native_sim']
assert r['model_calls']==4 and r['known_billed_tokens']==44816 and r['retry_contact_deadline_pass']
assert r['scientific_admission'] is r['training_admission'] is r['formal_event_memory_admission'] is False
for f in p['frames']:
    assert re.fullmatch(r'assets/native-v87/(cue|refused|finished)\.jpg',f['image'])
    assert hashlib.sha256((root/f['image']).read_bytes()).hexdigest()==f['image_sha256']
assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|ssh\s',json.dumps(r))


# Original-event scope is separate from the historical new-origin cases.
original=data.get('original_event_clock_probe')
if original:
    assert original['status']=='PASS_SCOPED_NATIVE_ORIGINAL_EVENT_DEADLINE_RECOVERY'
    for key in ('scientific_admission','training_admission','formal_M1_admission','full_benchmark_pass','original_deadline_reset'):
        assert original[key] is False,key
    assert original['clock_policy']=='PAUSED_BETWEEN_OWNED_PROCESSES_NATIVE_ONLY'
    assert original['receipt']=='artifacts/event-clock-v90.json'
    path=root/original['receipt'];assert hashlib.sha256(path.read_bytes()).hexdigest()==original['receipt_sha256']
    detail=json.loads(path.read_text())
    assert detail['original_deadline_pass'] is True
    assert detail['all_restore_native_steps_debited'] is detail['retry_task_origin_includes_failed_elapsed'] is True
    assert detail['matched_control_native_trials']==0 and detail['causal_memory_benefit_identified'] is False
    assert detail['chemical_event_verified'] is detail['wall_real_time_claim'] is detail['native_clock_continuous_across_rebuild'] is False
    a=original['original_event_a_task_bounds_s'];b=original['event_b_task_bounds_s'];gap=original['original_requested_gap_s']
    calculated=[(b[0]-a[1]-gap)*1000,(b[1]-a[0]-gap)*1000]
    assert all(math.isclose(x,y,abs_tol=1e-8,rel_tol=0) for x,y in zip(calculated,original['original_error_interval_ms']))
    assert all(abs(x)<=20 for x in calculated)
    attempts=original['attempts'];first=attempts['interrupted'];retry=attempts['retry']
    assert first['outcome']=='FAILED' and retry['outcome']=='COMPLETED'
    assert first['task_end_s']==retry['task_origin_s']
    assert first['phase_callbacks']['RESTORE']==retry['phase_callbacks']['RESTORE']==30
    assert first['phase_callbacks']['INJECTED_REVERSIBLE_INTERRUPTION']==480
    assert original['failed_tail_commands']==0 and original['retry_tail_commands']==5507
    assert first['native_clock_id']!=retry['native_clock_id']
    assert retry['phase_callbacks']['TAIL_COMMANDS']==5507
    assert original['parent_files_preserved']==detail['parent_files_preserved']==71
    assert original['retry_return_error_mm']==detail['phases']['child_retry']['placement_error_mm']<1
    assert original['known_billed_tokens']==detail['known_billed_tokens']==44853
    assert detail['opaque_actor_workspaces_verified'] is True and detail['undocumented_provider_context_attested'] is False
    assert len(original['frames'])==3
    for frame in original['frames']:
        assert re.fullmatch(r'assets/native-v90/(cue|interrupted|finished)\.jpg',frame['image'])
        assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(detail))

matched=data['matched_event_clock_probe']
assert matched['status']=='PASS_SCOPED_MATCHED_ORIGINAL_EVENT_NATIVE_CONTRACT'
assert matched['scientific_admission'] is matched['training_admission'] is matched['formal_M1_admission'] is False
assert matched['native_model_calls']==0 and matched['model_calls']==2 and matched['known_billed_tokens']==22400
assert matched['controlled_delivery_ticks_per_child']==240 and matched['controlled_delivery_is_measured_model_latency'] is False
assert matched['no_fault_control']=='COLD_CONTINUATION_NOT_CONTINUOUSLY_RUNNING_PARENT'
assert matched['original_deadline_reset'] is matched['causal_memory_benefit_identified'] is False
assert matched['parent_files_preserved']==71 and matched['pinned_files_verified']==121
assert matched['receipt']=='artifacts/event-clock-v91-matched.json'
assert hashlib.sha256((root/matched['receipt']).read_bytes()).hexdigest()==matched['receipt_sha256']
assert hashlib.sha256((root/matched['timeline']).read_bytes()).hexdigest()==matched['timeline_sha256']
assert len(matched['restore'])==4 and all(v['transient_samples']==30 and v['entities_each_sample']==65 for v in matched['restore'].values())
a=matched['original_event_a_task_bounds_s'];gap=matched['original_requested_gap_s']
for branch in ('no_fault','recovery'):
    b=matched['branches'][branch];lo,hi=b['event_b_task_bounds_s']
    error=[(lo-a[1]-gap)*1000,(hi-a[0]-gap)*1000]
    assert all(math.isclose(x,y,abs_tol=1e-8,rel_tol=0) for x,y in zip(error,b['error_interval_ms']))
    assert b['status']=='PASS_ORIGINAL_EVENT_INTERVAL' and b['tail_commands']==5507 and b['return_error_mm']<1
expired=matched['branches']['expired']
assert expired['tail_commands']==0 and expired['refusal_task_time_s']>matched['start_window_task_bounds_s'][1]
assert matched['attempts']['recovery_first']['task_end_s']==matched['attempts']['recovery_retry']['task_origin_s']
for frame in matched['frames']:
    assert re.fullmatch(r'assets/native-v91/(cue|control|retry)\.jpg',frame['image'])
    assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
scope=json.loads((root/matched['protocol_scope_addendum']).read_text())
assert hashlib.sha256((root/matched['protocol_scope_addendum']).read_bytes()).hexdigest()==matched['protocol_scope_addendum_sha256']
assert scope['consumed_sources_and_protocol_unchanged'] is True
assert scope['actual_prior_calls']==2 and scope['child_model_calls']==0
assert scope['source_pins_sha256']==matched['source_pins_sha256']
assert scope['authoritative_fields']['controlled_delivery_ticks']==240
assert set(scope['inactive_inherited_keys'])=={'readout_mode','simulation_paused_for_model_readouts','cleared_readout_mode'}
assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(scope))
coverage=data['stage_checkpoint_coverage']
assert coverage['committed_evidence_stages']==8 and len(coverage['stages'])==8
assert coverage['full_world_task_checkpoint_boundaries']==coverage['native_restart_verified_task_boundaries']==1
assert coverage['full_long_chain_restart_accepted'] is coverage['midcarry_restart_accepted'] is coverage['liquid_restart_accepted'] is False
assert coverage['verified_cold_restore_attempts']==4
assert sum(s['full_world_checkpoint_sealed'] for s in coverage['stages'])==1
assert sum(s['native_restart_verified'] for s in coverage['stages'])==1
assert coverage['stages'][4]['stage']=='place_release' and coverage['stages'][4]['native_restart_verified'] is True
assert hashlib.sha256((root/coverage['receipt']).read_bytes()).hexdigest()==coverage['receipt_sha256']
for value in (json.loads((root/matched['receipt']).read_text()),json.loads((root/coverage['receipt']).read_text())):
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(value))

archive=data.get('stage_state_archive_probe')
if archive:
    assert archive['status']=='PASS_SCOPED_FULL_REGISTERED_STAGE_STATE_NATIVE_ARCHIVE'
    assert archive['committed_evidence_stages']==archive['full_registered_stage_archives']==len(archive['stages'])==8
    assert archive['entities_per_archive']==65
    assert archive['full_world_task_checkpoint_boundaries']==archive['native_restart_verified_task_boundaries']==1
    assert archive['verified_cold_restore_attempts']==1 and archive['parent_files_preserved']==91
    assert archive['model_calls']==2 and archive['known_billed_tokens']<=32768
    assert archive['total_allocated_gpu_hours_upper_bound']<.24166666666666667
    assert archive['agent_context_and_task_timer_rebound'] is archive['saved_state_reconstruction_equivalence_claimed'] is False
    assert archive['full_long_chain_restart_accepted'] is archive['midcarry_restart_accepted'] is archive['liquid_restart_accepted'] is False
    assert archive['scientific_admission'] is archive['formal_M1_admission'] is archive['training_admission'] is False
    assert archive['receipt']=='artifacts/stage-state-v92.json'
    assert hashlib.sha256((root/archive['receipt']).read_bytes()).hexdigest()==archive['receipt_sha256']
    assert all(-20<=v<=20 for v in archive['original_event_error_interval_ms'])
    assert archive['final_return_error_mm']<1
    assert sum(s['full_world_checkpoint_sealed'] for s in archive['stages'])==1
    assert sum(s['native_restart_verified'] for s in archive['stages'])==1
    expected=[('approach',2400),('grasp',3840),('lift',4560),('transport',6480),('place_release',7920),('regrasp',9600),('return',12707),('retreat',13427)]
    assert [(s['stage'],s['source_end_command']) for s in archive['stages']]==expected
    for s in archive['stages']:
        assert s['full_registered_state_archived'] and s['registered_entities']==65
        assert s['physics_callbacks_during_persistence']==0 and s['exact_live_roundtrip']
        assert s['source_command_cursor']==s['source_end_command']==s['frame']['source_command_cursor']
        assert re.fullmatch(r'assets/native-v92/'+s['stage']+r'\.jpg',s['frame']['image'])
        assert hashlib.sha256((root/s['frame']['image']).read_bytes()).hexdigest()==s['frame']['image_sha256']
        assert re.fullmatch(r'[a-f0-9]{64}',s['state_sha256'])
        assert s['native_restart_verified']==(s['stage']=='place_release')
    assert archive['stages'][5]['recorded_host_tick']!=archive['stages'][5]['source_command_cursor']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',(root/archive['receipt']).read_text())

loaded=data.get('loaded_boundary_probe')
if loaded:
    import csv
    assert loaded['status']=='FAIL_MATCHED_NEXT_STAGE_ORIENTATION_WITH_VERIFIED_LOADED_HOLD'
    assert loaded['review_scope']=='POST_COLLECTION_NEGATIVE_OUTCOME_RECOMPUTATION_NOT_RETROACTIVE_PASS'
    assert loaded['registered_entities_each_sample']==65 and loaded['matched_hold_native_steps']==30
    assert loaded['matched_hold_pass'] and loaded['initial_velocity_gate_pass']
    assert loaded['transport_source_command_start']==4560 and loaded['transport_source_command_stop']==6480
    assert loaded['transport_commands_each']==1920 and loaded['transport_task_predicates_pass']
    assert loaded['bilateral_contact_fraction']==dict(parent=1.,child=1.)
    assert loaded['endpoint_orientation_error_deg']>loaded['original_orientation_limit_deg']==.5
    assert loaded['endpoint_position_error_mm']<loaded['original_position_limit_mm']==1.
    assert loaded['parent_files_preserved']==67 and loaded['pinned_files_verified']==122
    assert loaded['native_workers']==2 and loaded['actual_model_calls']==loaded['training_jobs']==0
    assert abs(loaded['r2_allocated_gpu_hours_upper_bound']+loaded['failed_r1_allocated_gpu_hours_upper_bound']-loaded['total_V93_allocated_gpu_hours_upper_bound'])<1e-12
    for key in ('full_endpoint_equivalence_pass','thresholds_changed_after_outcome',
                'root_cause_established','loaded_boundary_full_continuation_accepted',
                'new_generic_restart_admission','agent_context_and_original_timer_rebound',
                'pending_original_event_deadline_tested','scientific_admission',
                'training_admission','formal_M1_admission','full_benchmark_pass'):
        assert loaded[key] is False,key
    for key in ('receipt','plot','numeric_projection'):
        path=loaded[key]
        assert path.startswith(('artifacts/loaded-boundary-v93-', 'assets/native-v93/'))
        assert (root/path).resolve().is_relative_to(root.resolve())
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==loaded[key+'_sha256']
    rows=list(csv.DictReader((root/loaded['numeric_projection']).open()))
    assert len(rows)==1920
    assert list(rows[0])==['native_transport_s','orientation_error_deg','position_error_mm']
    values=[{k:float(v) for k,v in row.items()} for row in rows]
    assert all(math.isfinite(v) and v>=0 for row in values for v in row.values())
    assert all(a['native_transport_s']<b['native_transport_s'] for a,b in zip(values,values[1:]))
    assert abs(values[-1]['orientation_error_deg']-loaded['endpoint_orientation_error_deg'])<1e-12
    crossing=next(row for row in values if row['orientation_error_deg']>.5)
    assert crossing['native_transport_s']==loaded['first_orientation_limit_crossing']['aligned_native_transport_s']
    assert [(f['phase'],f['source_command_cursor']) for f in loaded['frames']]==[('parent',4560),('child',4560),('parent',6480),('child',6480)]
    for frame in loaded['frames']:
        assert re.fullmatch(r'assets/native-v93/(parent|child)-(04560|06480)\.jpg',frame['image'])
        assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(loaded))
    assert archive['native_restart_verified_task_boundaries']==1 and archive['full_registered_stage_archives']==8

baseline=data.get('live_baseline_probe')
if baseline:
    import csv
    assert baseline['status']=='LIVE_BASELINE_DATA_VALIDATED_WITHIN_ORIGINAL_ENDPOINT_LIMITS'
    assert baseline['baseline_workers']==2 and baseline['source_commands_each']==6480
    assert baseline['source_command_cut']==4560 and baseline['transport_commands_each']==1920
    assert baseline['registered_entities']==65 and baseline['matched_hold_steps']==30
    assert baseline['whole_registered_endpoint_equivalence_pass'] and baseline['matched_hold_equivalence_pass']
    assert baseline['recorded_bottle_transport_pose_arrays_identical'] and baseline['tiny_angle_residual_is_formula_roundoff_on_identical_poses']
    assert baseline['endpoint_bottle_orientation_error_deg']==baseline['endpoint_bottle_position_error_mm']==0
    assert baseline['maximum_computed_transport_orientation_error_deg']<1e-5
    assert baseline['live_a_files_preserved']==67 and baseline['pinned_files_verified']==124
    assert baseline['loaded_restore_calls_at_cut']==baseline['model_calls']==baseline['training_jobs']==0
    assert baseline['reader_sealed_before_collection']
    assert baseline['total_allocated_gpu_hours_upper_bound']<2*435/3600
    for key in ('randomized_success_rate_measured','causal_cold_restore_effect_established',
                'root_cause_established','loaded_boundary_full_continuation_accepted',
                'new_generic_restart_admission','original_event_and_agent_timer_binding_tested',
                'scientific_admission','training_admission','formal_M1_admission','full_benchmark_pass'):
        assert baseline[key] is False,key
    for key in ('receipt','plot','numeric_projection'):
        path=baseline[key]
        assert path.startswith(('artifacts/live-baseline-v94.', 'assets/native-v94/'))
        assert (root/path).resolve().is_relative_to(root.resolve())
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==baseline[key+'_sha256']
    values=[{k:float(v) for k,v in row.items()} for row in csv.DictReader((root/baseline['numeric_projection']).open())]
    assert len(values)==1920 and all(row['position_error_mm']==0 for row in values)
    assert all(math.isfinite(v) and v>=0 for row in values for v in row.values())
    assert max(row['orientation_error_deg'] for row in values)==baseline['maximum_computed_transport_orientation_error_deg']
    assert all(a['native_transport_s']<b['native_transport_s'] for a,b in zip(values,values[1:]))
    assert len(baseline['frames'])==4
    for frame in baseline['frames']:
        assert re.fullmatch(r'assets/native-v94/live_[ab]-(04560|06480)\.jpg',frame['image'])
        assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(baseline))
    assert loaded['full_endpoint_equivalence_pass'] is False
    assert archive['native_restart_verified_task_boundaries']==1

same=data.get('same_process_probe')
if same:
    import csv
    assert same['status']=='FAIL_SAME_PROCESS_MATCHED_NEXT_STAGE_ENDPOINT'
    assert same['native_workers']==2 and same['source_commands_each']==6480
    assert same['source_command_cut']==4560 and same['transport_commands_each']==1920
    assert same['registered_entities']==65 and same['matched_hold_steps']==30
    assert same['both_workers_execute_prefix'] and same['loaded_intervention_inside_existing_worker']
    assert same['initial_source_physics_and_graph_exact'] and same['matched_hold_pass']
    assert same['restoration_writer_calls']==sum(same['restoration_call_counts'].values())==167
    assert same['restoration_physics_callbacks']==same['model_calls']==same['training_jobs']==0
    assert same['endpoint_bottle_orientation_error_deg']>.5
    assert same['endpoint_bottle_position_error_mm']<1.
    assert same['original_orientation_limit_deg']==.5 and same['original_position_limit_mm']==1.
    assert same['thresholds_unchanged'] and same['reader_sealed_before_collection']
    assert same['pinned_files_verified']==126 and same['live_control_files_preserved']==68
    assert same['all_owned_native_process_groups_closed']
    assert same['total_allocated_gpu_hours_upper_bound']<2*435/3600
    for key in ('next_stage_pose_control_pass','fresh_process_required_for_this_failure',
                'specific_writer_cause_established','hidden_state_cause_established',
                'randomized_effect_measured','cold_restart_admitted','new_generic_restart_admission',
                'full_stored_state_equivalence_certified','original_event_and_agent_timer_binding_tested',
                'scientific_admission','training_admission','formal_M1_admission','full_benchmark_pass'):
        assert same[key] is False,key
    for key in ('receipt','plot','numeric_projection'):
        path=same[key]
        assert path.startswith(('artifacts/same-process-v95-negative.', 'assets/native-v95/'))
        assert (root/path).resolve().is_relative_to(root.resolve())
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==same[key+'_sha256']
    values=[{k:float(v) for k,v in row.items()} for row in csv.DictReader((root/same['numeric_projection']).open())]
    assert len(values)==1920 and all(math.isfinite(v) and v>=0 for row in values for v in row.values())
    assert all(a['native_transport_s']<b['native_transport_s'] for a,b in zip(values,values[1:]))
    assert values[-1]['orientation_error_deg']==same['endpoint_bottle_orientation_error_deg']
    assert values[-1]['position_error_mm']==same['endpoint_bottle_position_error_mm']
    crossing=next(row for row in values if row['orientation_error_deg']>.5)
    assert crossing['native_transport_s']==same['first_sampled_orientation_exceedance']['aligned_native_transport_s']
    assert len(same['frames'])==4
    for frame in same['frames']:
        assert re.fullmatch(r'assets/native-v95/(live_control|same_process_restore)-(04560|06480)\.jpg',frame['image'])
        assert hashlib.sha256((root/frame['image']).read_bytes()).hexdigest()==frame['image_sha256']
    assert not re.search(r'(?i)Bearer\s|ct-[a-f0-9]{20}|znt_[a-f0-9]{20}|/mnt/|/home/|/data/|ssh\s',json.dumps(same))
    assert same['saved_task_boundaries']==8 and same['validated_cold_restart_boundaries']==1
    assert archive['native_restart_verified_task_boundaries']==1

print(json.dumps(dict(status='PASS',checked_scene_replays=6,checked_camera_videos=count,
                     same_process_negative_evidence_checked=bool(same),
                     live_baseline_evidence_checked=bool(baseline),
                     loaded_continuation_accepted=False,
                     loaded_negative_evidence_checked=bool(loaded),
                     matched_original_deadline_contract_pass=True,
                     verified_task_checkpoint_boundaries=1,
                     committed_evidence_stages=8,
                     full_registered_state_archives=8 if archive else 1,
                     native_bottle_frames=30 if bottle else 0,
                     native_bottle_pair_pass=bool(bottle),
                     native_mid_task_resume_pass=bool(mid),
                     preserved_memory_readout_pass=bool(memory),
                     native_agent_memory_timed_contact_pass=bool(agent),
                     historical_carry_whole_scene_restore_accepted=False,
                     native_released_restore_tested=bool(native.get('physical_measurement_started')),
                     scientific_admission=False)))
