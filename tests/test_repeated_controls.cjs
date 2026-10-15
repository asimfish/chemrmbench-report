'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const {validate} = require('../repeated-controls.js');
function fixture() {
  const rows = [], runs = [];
  for (const repeat of [1, 2, 3]) for (const condition of ['no_write', 'read_only_sham', 'single_pose_write']) {
    const id = `r${repeat}-${condition}`, control = condition === 'no_write', write = condition === 'single_pose_write';
    runs.push({id, repeat, condition});
    rows.push({run_id: id, repeat, condition, control_reference: control, source_match_pass: true,
      matched_hold_pass: true, endpoint_pass: !write, state_writer_calls: write ? 1 : 0,
      endpoint_orientation_error_deg: control ? null : write ? .65 : 0,
      endpoint_position_error_mm: control ? null : write ? .31 : 0, gpu_hours_upper_bound: .06, video_frames: 326});
  }
  return {data: {schema: 'chemrm-public-repeated-controls-v1', repetitions: 3, rows,
    original_orientation_limit_deg: .5, original_position_limit_mm: 1, signature_consistent: true,
    all_pairs_usable: true, controls_identical: true, cohort_gpu_hours_upper_bound: .6,
    prior_gpu_hours_upper_bound: .22, scope: 'Fixed-condition repetitions'}, runs};
}
test('retain all three negative write outcomes and zero-write baseline references', () => {
  const {data, runs} = fixture(), result = validate(data, runs);
  assert.equal(result.filter(r => r.endpoint_pass === false).length, 3);
  assert.equal(result.filter(r => r.control_reference && r.endpoint_orientation_error_deg === null).length, 3);
});
test('refused pairing remains unknown and cannot become a success', () => {
  const {data, runs} = fixture(); data.signature_consistent = false; data.all_pairs_usable = false;
  Object.assign(data.rows[2], {source_match_pass: false, state_writer_calls: 0, matched_hold_pass: null,
    endpoint_pass: null, endpoint_orientation_error_deg: null, endpoint_position_error_mm: null});
  assert.equal(validate(data, runs)[2].endpoint_pass, null);
  data.rows[2].endpoint_pass = true;
  assert.throws(() => validate(data, runs), /contradicts evidence/);
});
test('reject a positive verdict above the unchanged orientation limit', () => {
  const {data, runs} = fixture(); data.signature_consistent = false; data.rows[2].endpoint_pass = true;
  assert.throws(() => validate(data, runs), /contradicts evidence/);
});
test('reject duplicate pairings or mismatched video identity', () => {
  for (const edit of [d => {d.data.rows[8] = {...d.data.rows[7]};},
                     d => {d.runs[0].repeat = 2;}]) {
    const f = fixture(); edit(f); assert.throws(() => validate(f.data, f.runs), /pairing invalid/);
  }
});
test('reject extra writes, changed gates, fabricated summary and over-budget cohort', () => {
  for (const edit of [d => {d.rows[1].state_writer_calls = 1;}, d => {d.original_orientation_limit_deg = 1;},
                     d => {d.rows[1].endpoint_pass = false;}, d => {d.cohort_gpu_hours_upper_bound = 2;}]) {
    const f = fixture(); edit(f.data); assert.throws(() => validate(f.data, f.runs));
  }
});
