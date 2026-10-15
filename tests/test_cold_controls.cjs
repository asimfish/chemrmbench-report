const test=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('../cold-controls.js');
const {validateFrames}=require('../cold-controls.js');
function fixture(){return {schema:'chemrm-public-cold-boundary-v1',scientific_admission:false,training_admission:false,full_benchmark_pass:false,
  task_boundaries:8,cold_restart_boundaries_added:0,verified_boundaries:1,initial_gate_pass:true,matched_hold_pass:true,
  full_tail_task_clock_matches:true,strict_endpoints_pass:false,gpu_hours:.2,source_pins_sha256:'a'.repeat(64),reader_source_sha256:'b'.repeat(64),
  rows:[{phase:'live',run_id:'V99-live',source_start:0,source_commands:13427,expected_boundaries:8,committed_boundaries:8,
    initial_gate:'pass',hold_gate:'pass',strict_gate:'reference',full_tail_complete:true,final_return_error_mm:.5},
    {phase:'cold',run_id:'V99-cold',source_start:2400,source_commands:11027,expected_boundaries:7,committed_boundaries:7,
      initial_gate:'pass',hold_gate:'pass',strict_gate:'fail',full_tail_complete:true,final_return_error_mm:.5}],
  stage_rows:['grasp','lift','transport','place_release','regrasp','return','retreat'].map(stage_id=>({stage_id,
    position_max_mm:.1,orientation_max_deg:.1,joint_coordinate_max:.00001,drive_state_equal:false,strict_pass:false,pose_drive_pass:true}))};}
const runs=[{id:'V99-live'},{id:'V99-cold'}];
test('full tail with strict drive mismatch remains a negative result',()=>{assert.equal(validate(fixture(),runs).verified_boundaries,1);});
test('refused hold with no tail stays visible without endpoint samples',()=>{const d=fixture();d.stage_rows=[];d.matched_hold_pass=false;d.full_tail_task_clock_matches=false;Object.assign(d.rows[1],{source_commands:0,committed_boundaries:0,hold_gate:'fail',strict_gate:'not_tested',full_tail_complete:false,final_return_error_mm:null});validate(d,runs);});
test('only all original gates and full tail can add a boundary',()=>{const d=fixture();d.cold_restart_boundaries_added=1;d.verified_boundaries=2;assert.throws(()=>validate(d,runs));d.strict_endpoints_pass=true;d.rows[1].strict_gate='pass';d.stage_rows.forEach(r=>{r.drive_state_equal=true;r.strict_pass=true;});validate(d,runs);});
test('source prefix replay, missing stage proof and scientific promotion reject',()=>{for(const change of [d=>d.rows[1].source_start=0,d=>d.stage_rows.pop(),d=>d.scientific_admission=true,d=>d.rows.push(d.rows[1]),d=>d.rows[1].full_tail_complete=false,d=>d.gpu_hours=1]){const d=fixture();change(d);assert.throws(()=>validate(d,runs));}});
test('cold video keeps the saved prefix time while its local movie starts at zero',()=>{const r={id:'V99-cold',task_time_offset_s:10};validateFrames(r,[{physics_tick:0,native_elapsed_s:0,task_time_s:10,source_command_cursor:2400},{physics_tick:20,native_elapsed_s:1/12,task_time_s:10+1/12,source_command_cursor:2400}]);});
test('resetting the task clock in a cold frame is refused',()=>{assert.throws(()=>validateFrames({id:'V99-cold',task_time_offset_s:0},[{physics_tick:0,native_elapsed_s:0,task_time_s:0,source_command_cursor:2400}]));assert.throws(()=>validateFrames({id:'V99-cold',task_time_offset_s:10},[{physics_tick:0,native_elapsed_s:0,task_time_s:10,source_command_cursor:0}]));});
