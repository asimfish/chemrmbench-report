(function(root){'use strict';
function validate(data,runs){
  if(data.schema!=='chemrm-public-cold-boundary-v1'||data.scientific_admission!==false||data.training_admission!==false||data.full_benchmark_pass!==false)throw Error('invalid cold experiment scope');
  if(data.task_boundaries!==8||!Number.isInteger(data.cold_restart_boundaries_added)||![0,1].includes(data.cold_restart_boundaries_added)||data.verified_boundaries!==1+data.cold_restart_boundaries_added)throw Error('invalid cold coverage');
  for(const key of ['initial_gate_pass','matched_hold_pass','full_tail_task_clock_matches','strict_endpoints_pass'])if(typeof data[key]!=='boolean')throw Error('missing cold gate');
  if(data.cold_restart_boundaries_added===1&&!['initial_gate_pass','matched_hold_pass','full_tail_task_clock_matches','strict_endpoints_pass'].every(k=>data[k]))throw Error('unverified cold admission');
  if(!Number.isFinite(data.gpu_hours)||data.gpu_hours<0||data.gpu_hours>0.341667)throw Error('invalid cold allocation');
  for(const key of ['source_pins_sha256','reader_source_sha256'])if(!/^[a-f0-9]{64}$/.test(data[key]))throw Error('invalid cold source digest');
  if(!Array.isArray(data.rows)||data.rows.length<1||data.rows.length>2)throw Error('invalid cold rows');
  const seen=new Set();
  for(const row of data.rows){
    if(!['live','cold'].includes(row.phase)||seen.has(row.phase)||row.run_id!=='V99-'+row.phase||!runs.some(r=>r.id===row.run_id))throw Error('invalid cold run identity');seen.add(row.phase);
    const cold=row.phase==='cold',expected=cold?11027:13427;
    if(row.source_start!==(cold?2400:0)||row.expected_boundaries!==(cold?7:8)||!Number.isInteger(row.source_commands)||row.source_commands<0||row.source_commands>expected)throw Error('invalid cold source cursor');
    if(!Number.isInteger(row.committed_boundaries)||row.committed_boundaries<0||row.committed_boundaries>row.expected_boundaries||typeof row.full_tail_complete!=='boolean'||row.full_tail_complete!==(row.source_commands===expected))throw Error('invalid cold completion');
    for(const key of ['initial_gate','hold_gate'])if(!['pass','fail','not_tested'].includes(row[key]))throw Error('invalid cold gate');
    if(!['pass','fail','reference','not_tested'].includes(row.strict_gate)||(!cold&&row.strict_gate!=='reference'))throw Error('invalid strict gate');
    if(row.final_return_error_mm!==null&&(!Number.isFinite(row.final_return_error_mm)||row.final_return_error_mm<0))throw Error('invalid return error');
    if(cold&&data.cold_restart_boundaries_added===1&&(!row.full_tail_complete||row.committed_boundaries!==7||row.strict_gate!=='pass'||row.initial_gate!=='pass'||row.hold_gate!=='pass'))throw Error('partial tail cannot add coverage');
    if(cold&&row.strict_gate==='pass'&&!data.strict_endpoints_pass)throw Error('contradictory strict gate');
  }
  const ids=['grasp','lift','transport','place_release','regrasp','return','retreat'];
  if(!Array.isArray(data.stage_rows)||![0,7].includes(data.stage_rows.length))throw Error('incomplete endpoint table');
  for(const [i,row]of data.stage_rows.entries()){
    if(row.stage_id!==ids[i])throw Error('invalid endpoint order');
    for(const key of ['position_max_mm','orientation_max_deg','joint_coordinate_max'])if(!Number.isFinite(row[key])||row[key]<0)throw Error('invalid endpoint error');
    for(const key of ['drive_state_equal','strict_pass','pose_drive_pass'])if(typeof row[key]!=='boolean')throw Error('invalid endpoint verdict');
    if(row.strict_pass&&(!row.drive_state_equal||!row.pose_drive_pass||row.position_max_mm>1||row.orientation_max_deg>.5||row.joint_coordinate_max>.0001))throw Error('contradictory endpoint admission');
  }
  if(data.cold_restart_boundaries_added===1&&(data.stage_rows.length!==7||!data.stage_rows.every(r=>r.strict_pass)))throw Error('missing strict endpoint proof');
  if(data.comparison_video!==undefined&&(data.comparison_video!=='assets/native-v99/aligned-comparison.mp4'||data.comparison_poster!=='assets/native-v99/aligned-comparison.jpg'||data.comparison_receipt!=='artifacts/v99-aligned-replay.json'))throw Error('invalid derived comparison asset');
  return data;
}
function validateFrames(run,frames){
  if(!['V99-live','V99-cold','V100-live','V100-cold'].includes(run.id)||!Number.isFinite(run.task_time_offset_s)||!Array.isArray(frames)||!frames.length)throw Error('invalid restored task clock');
  const cold=run.id.endsWith('-cold'),start=cold?2400:0;
  if(Math.abs(run.task_time_offset_s-(cold?10:0))>1e-5||frames[0].source_command_cursor!==start)throw Error('restored task clock or source cursor reset');
  for(const f of frames)if(!Number.isFinite(f.task_time_s)||!Number.isInteger(f.physics_tick)||f.physics_tick<0||Math.abs(f.native_elapsed_s-f.physics_tick/240)>1e-5||Math.abs(f.task_time_s-run.task_time_offset_s-f.native_elapsed_s)>1e-7)throw Error('task/native frame time inconsistent');
  return frames;
}
root.ChemRMCold={validate,validateFrames};if(typeof module!=='undefined'&&module.exports)module.exports={validate,validateFrames};
})(typeof window!=='undefined'?window:globalThis);
