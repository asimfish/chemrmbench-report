(function(root){'use strict';
function validate(data,runs){
  if(data.schema!=='chemrm-public-fixed-action-v100'||data.private_validator_only!==true||data.agent_visible_actions!==false||data.cold_restart_boundaries_added!==0||data.verified_boundaries!==1)throw Error('invalid private fixed-action scope');
  for(const k of ['fixed_action_boundary_pass','applied_action_trace_equal'])if(typeof data[k]!=='boolean')throw Error('missing fixed-action verdict');
  if(!data.rows.every(r=>r.run_id==='V100-'+r.phase))throw Error('fixed-action row linked to another cohort');
  const subset=runs.filter(r=>/^V100-(live|cold)$/.test(r.id)).map(r=>({...r,id:r.id.replace('V100-','V99-')}));
  const projected={...data,schema:'chemrm-public-cold-boundary-v1',rows:data.rows.map(r=>({...r,run_id:r.run_id.replace('V100-','V99-')}))};
  for(const key of ['comparison_video','comparison_poster','comparison_receipt'])delete projected[key];
  root.ChemRMCold.validate(projected,subset);
  const keys=['rows','start_canonical_step','actions_sha256','all_targets_and_simulator_inputs_equal','all_recorded_stage_targets_match','private_validator_only','agent_visible'];
  for(const [phase,trace]of Object.entries(data.action_trace_review)){
    if(!['live','cold'].includes(phase)||Object.keys(trace).some(k=>!keys.includes(k)))throw Error('private action values cannot be public');
    if(!Number.isInteger(trace.rows)||trace.rows<0||trace.rows>(phase==='live'?13457:11057)||trace.start_canonical_step!==(phase==='live'?0:2400)||!/^[0-9a-f]{64}$/.test(trace.actions_sha256))throw Error('invalid fixed-action trace identity');
    if(trace.private_validator_only!==true||trace.agent_visible!==false||trace.all_targets_and_simulator_inputs_equal!==true||trace.all_recorded_stage_targets_match!==true)throw Error('unverified action-input projection');
  }
  if(data.fixed_action_boundary_pass&&(!data.applied_action_trace_equal||!data.initial_gate_pass||!data.matched_hold_pass||!data.full_tail_task_clock_matches||!data.strict_endpoints_pass||data.stage_rows.length!==7||!data.stage_rows.every(r=>r.strict_pass)||data.action_trace_review.live?.rows!==13457||data.action_trace_review.cold?.rows!==11057))throw Error('partial or unmatched control cannot pass');
  if(data.comparison_video!==undefined&&(data.comparison_video!=='assets/native-v100/aligned-comparison.mp4'||data.comparison_poster!=='assets/native-v100/aligned-comparison.jpg'||data.comparison_receipt!=='artifacts/v100-aligned-replay.json'))throw Error('invalid fixed-action comparison path');
  for(const [key,path]of Object.entries({chart:'assets/native-v100/stage-endpoints.png',chart_pdf:'assets/native-v100/stage-endpoints.pdf',csv:'assets/native-v100/stage-endpoints.csv'}))if(data[key]!==undefined&&data[key]!==path)throw Error('invalid fixed-action result asset');
  return data;
}
root.ChemRMFixed={validate};if(typeof module!=='undefined'&&module.exports)module.exports={validate};
})(typeof window!=='undefined'?window:globalThis);
