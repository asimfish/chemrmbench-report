const test=require('node:test'),assert=require('node:assert/strict');
require('../cold-controls.js');
const {validate}=require('../fixed-actions.js');
function fixture(){return {schema:'chemrm-public-fixed-action-v100',scientific_admission:false,training_admission:false,full_benchmark_pass:false,
  task_boundaries:8,cold_restart_boundaries_added:0,verified_boundaries:1,initial_gate_pass:true,matched_hold_pass:true,
  full_tail_task_clock_matches:true,strict_endpoints_pass:false,gpu_hours:.2,source_pins_sha256:'a'.repeat(64),reader_source_sha256:'b'.repeat(64),
  rows:[{phase:'live',run_id:'V100-live',source_start:0,source_commands:13427,expected_boundaries:8,committed_boundaries:8,
    initial_gate:'pass',hold_gate:'pass',strict_gate:'reference',full_tail_complete:true,final_return_error_mm:.5},
    {phase:'cold',run_id:'V100-cold',source_start:2400,source_commands:11027,expected_boundaries:7,committed_boundaries:7,
      initial_gate:'pass',hold_gate:'pass',strict_gate:'fail',full_tail_complete:true,final_return_error_mm:.5}],
  stage_rows:['grasp','lift','transport','place_release','regrasp','return','retreat'].map(stage_id=>({stage_id,
    position_max_mm:.1,orientation_max_deg:.1,joint_coordinate_max:.00001,drive_state_equal:false,strict_pass:false,pose_drive_pass:true}))};}

const runs=[{id:'V100-live'},{id:'V100-cold'}];
function diagnostic(){const d=fixture();Object.assign(d,{private_validator_only:true,agent_visible_actions:false,fixed_action_boundary_pass:false,applied_action_trace_equal:true,action_trace_review:{}});for(const phase of ['live','cold'])d.action_trace_review[phase]={rows:phase==='live'?13457:11057,start_canonical_step:phase==='live'?0:2400,actions_sha256:'c'.repeat(64),all_targets_and_simulator_inputs_equal:true,all_recorded_stage_targets_match:true,private_validator_only:true,agent_visible:false};return d;}
test('fixed-action strict success stays diagnostic without adding ordinary cold coverage',()=>{const d=diagnostic();d.fixed_action_boundary_pass=true;d.strict_endpoints_pass=true;d.rows[1].strict_gate='pass';d.stage_rows.forEach(r=>{r.drive_state_equal=true;r.strict_pass=true;});assert.equal(validate(d,runs).verified_boundaries,1);assert.equal(d.rows[1].run_id,'V100-cold');});
test('fixed-action negative result retains old strict state failure',()=>{assert.equal(validate(diagnostic(),runs).fixed_action_boundary_pass,false);});
test('scope promotion, missing action channels and wrong video cohort reject',()=>{for(const change of [d=>d.verified_boundaries=2,d=>d.cold_restart_boundaries_added=1,d=>d.agent_visible_actions=true,d=>d.rows[1].run_id='V99-cold',d=>d.action_trace_review.cold.all_targets_and_simulator_inputs_equal=false,d=>d.action_trace_review.cold.calls=[],d=>d.comparison_video='assets/native-v99/aligned-comparison.mp4']){const d=diagnostic();change(d);assert.throws(()=>validate(d,runs));}});
test('an incomplete private trace cannot turn into a full-control pass',()=>{const d=diagnostic();d.fixed_action_boundary_pass=true;assert.throws(()=>validate(d,runs));});
test('V100 cold frames preserve saved task time and never replay the source prefix',()=>{const {validateFrames}=require('../cold-controls.js');validateFrames({id:'V100-cold',task_time_offset_s:10},[{physics_tick:0,native_elapsed_s:0,task_time_s:10,source_command_cursor:2400}]);assert.throws(()=>validateFrames({id:'V100-cold',task_time_offset_s:0},[{physics_tick:0,native_elapsed_s:0,task_time_s:0,source_command_cursor:0}]));});
