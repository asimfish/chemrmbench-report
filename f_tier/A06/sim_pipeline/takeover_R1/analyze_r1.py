"""A06 R1 metrics for one closed run, recomputed against the VIDEO reference (not the runner's commanded target).
Also reports the frozen A06 bottle gate. Usage: analyze_r1.py RUN_DIR MOTION_JSON [--negative-displacement M]"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motion import sample
def analyze(run, motion_path, negative_disp=None):
    run = Path(run); d = json.loads((run/'result.json').read_text()); r = np.load(run/'raw.npz', allow_pickle=True)
    motion = json.loads(Path(motion_path).read_text())
    ev = next(e for e in d['stage_events'] if e['event'] in ('swirl_after_observed_settling', 'swirl'))
    a_tick = ev['tick']; swirl_start = ev.get('first_reference_tick', a_tick + 1)*.05
    obs = r['obs']; tcp = obs[:, 14:17]; obj = obs[:, 23:26]; anchor = tcp[a_tick, :2]; obj0 = obj[a_tick, :2]
    rows = np.where((r['stage'] == 'swirl') & (r['source_frame'] >= 83))[0]
    out = dict(run=str(run), actor=d.get('actor'), seed=d.get('seed'), initial_source_xy_m=d.get('initial_source_xy_m'), swirl_rows=int(len(rows)))
    if len(rows):
        phase = r['policy_time'][rows] - swirl_start
        ref = np.stack([sample(motion, float(np.clip(t, 0, None)), partition='full') for t in phase])
        e_tcp = np.linalg.norm(tcp[rows, :2] - (anchor + ref), axis=1)
        e_obj = np.linalg.norm((obj[rows, :2] - obj0) - ref, axis=1)
        amp = float(np.mean(np.std(tcp[rows, :2] - anchor, axis=0) / np.maximum(np.std(ref, axis=0), 1e-6)))
        out.update(TCP_vs_video=dict(RMS_m=float(np.sqrt(np.mean(e_tcp**2))), max_m=float(e_tcp.max())),
                   bottle_vs_video=dict(RMS_m=float(np.sqrt(np.mean(e_obj**2))), p95_m=float(np.percentile(e_obj, 95))), amplitude_ratio=amp)
    g = d.get('grasp_drift_metrics', {}); p = d.get('particle_metrics', {}); c = d.get('counts', {})
    out.update(physical=dict(complete=d.get('complete'), clock_valid=d.get('clock_valid'), finite=d.get('finite'), lift=d.get('physical_lift_verified'),
                             swirl_complete=d.get('swirl_complete'), returned=d.get('physical_return_verified'), contact=d.get('swirl_bilateral_contact_fraction'),
                             counts=c, tilt_p95_deg=g.get('bottle_Z_axis_tilt_p95_deg'), retention_swirl=p.get('minimum_strict_ideal_cavity_fraction_swirl'),
                             particle_displacement_RMS_m=p.get('swirl_local_particle_displacement_RMS_m')),
               frozen_gate_runner=d.get('trajectory_metrics', {}).get('bottle_XY_relative'))
    ph = out['physical']
    phys_ok = bool(ph['complete'] and ph['clock_valid'] and ph['finite'] and ph['lift'] and ph['swirl_complete'] and ph['returned'] and ph['contact'] == 1
                   and not any(c.values()) and ph['tilt_p95_deg'] is not None and ph['tilt_p95_deg'] <= 10 and (ph['retention_swirl'] or 0) >= .95)
    out['R1_physical_ok'] = phys_ok
    if len(rows):
        out['R1_teacher_admitted'] = bool(phys_ok and out['TCP_vs_video']['RMS_m'] <= .005 and out['TCP_vs_video']['max_m'] <= .010)
        fb = out['frozen_gate_runner'] or {}
        out['frozen_bottle_gate_pass'] = bool(fb and fb.get('RMS_m', 1) <= .005 and fb.get('p95_m', 1) <= .010)
        if negative_disp is not None:
            out['swirl_evidence'] = bool((ph['particle_displacement_RMS_m'] or 0) >= 2*negative_disp)
            out['R1_student_success'] = bool(phys_ok and out['swirl_evidence'] and out['TCP_vs_video']['RMS_m'] <= .010 and .6 <= amp <= 1.4)
    return out
if __name__ == '__main__':
    neg = float(sys.argv[sys.argv.index('--negative-displacement')+1]) if '--negative-displacement' in sys.argv else None
    print(json.dumps(analyze(sys.argv[1], sys.argv[2], neg), indent=2))
