"""Public history subset: media identity + explicit reconstruction claim boundaries."""
import hashlib
import json
from pathlib import Path
import re

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
print(json.dumps(dict(status='PASS',checked_scene_replays=6,checked_camera_videos=count,
                     historical_carry_whole_scene_restore_accepted=False,
                     native_released_restore_tested=bool(native.get('physical_measurement_started')),
                     scientific_admission=False)))
