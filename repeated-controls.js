'use strict';
(function (root) {
  const conditions = ['no_write', 'read_only_sham', 'single_pose_write'];
  function validate(data, runs) {
    if (!data || data.schema !== 'chemrm-public-repeated-controls-v1' || data.repetitions !== 3 ||
        data.original_orientation_limit_deg !== 0.5 || data.original_position_limit_mm !== 1 ||
        !Array.isArray(data.rows) || data.rows.length !== 9) throw Error('repeated controls scope invalid');
    for (const key of ['signature_consistent', 'all_pairs_usable', 'controls_identical']) {
      if (typeof data[key] !== 'boolean') throw Error('repeated controls verdict invalid');
    }
    for (const key of ['cohort_gpu_hours_upper_bound', 'prior_gpu_hours_upper_bound']) {
      if (!Number.isFinite(data[key]) || data[key] < 0) throw Error('repeated controls budget invalid');
    }
    if (data.cohort_gpu_hours_upper_bound > 1.0875 || typeof data.scope !== 'string') throw Error('repeated controls budget exceeded');
    const byId = new Map(runs.map(r => [r.id, r])), seen = new Set();
    for (const row of data.rows) {
      const id = `${row.repeat}:${row.condition}`, run = byId.get(row.run_id);
      if (![1, 2, 3].includes(row.repeat) || !conditions.includes(row.condition) || seen.has(id) ||
          !run || run.repeat !== row.repeat || run.condition !== row.condition ||
          row.control_reference !== (row.condition === 'no_write') || typeof row.source_match_pass !== 'boolean') {
        throw Error('repeated controls pairing invalid');
      }
      seen.add(id);
      for (const key of ['endpoint_pass', 'matched_hold_pass']) {
        if (row[key] !== null && typeof row[key] !== 'boolean') throw Error('repeated controls gate invalid');
      }
      const expectedWrites = row.condition === 'single_pose_write' && row.source_match_pass ? 1 : 0;
      if (row.state_writer_calls !== expectedWrites) throw Error('repeated controls write audit invalid');
      for (const key of ['endpoint_orientation_error_deg', 'endpoint_position_error_mm']) {
        if (row[key] !== null && (!Number.isFinite(row[key]) || row[key] < 0)) throw Error('repeated controls metric invalid');
      }
      if (!Number.isFinite(row.gpu_hours_upper_bound) || row.gpu_hours_upper_bound < 0 ||
          !Number.isInteger(row.video_frames) || row.video_frames < 1) throw Error('repeated controls resource invalid');
      if (row.endpoint_pass === true && (!row.source_match_pass || row.matched_hold_pass !== true ||
          (!row.control_reference && (row.endpoint_orientation_error_deg === null || row.endpoint_position_error_mm === null ||
            row.endpoint_orientation_error_deg > .5 || row.endpoint_position_error_mm > 1)))) {
        throw Error('repeated controls positive verdict contradicts evidence');
      }
    }
    if (data.signature_consistent && (!data.all_pairs_usable || data.rows.some(r =>
        r.condition !== 'no_write' && (r.matched_hold_pass !== true ||
          r.endpoint_pass !== (r.condition === 'read_only_sham'))))) throw Error('repeated controls summary contradicts pairs');
    return data.rows.slice().sort((a, b) => a.repeat - b.repeat || conditions.indexOf(a.condition) - conditions.indexOf(b.condition));
  }
  const api = {validate};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ChemRMRepeated = api;
})(typeof window === 'undefined' ? globalThis : window);
