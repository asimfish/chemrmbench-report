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

print(json.dumps(dict(status='PASS',checked_scene_replays=6,checked_camera_videos=count,
                     native_bottle_frames=30 if bottle else 0,
                     native_bottle_pair_pass=bool(bottle),
                     native_mid_task_resume_pass=bool(mid),
                     preserved_memory_readout_pass=bool(memory),
                     native_agent_memory_timed_contact_pass=bool(agent),
                     historical_carry_whole_scene_restore_accepted=False,
                     native_released_restore_tested=bool(native.get('physical_measurement_started')),
                     scientific_admission=False)))
