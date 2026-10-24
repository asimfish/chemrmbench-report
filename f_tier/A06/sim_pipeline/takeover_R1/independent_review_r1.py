"""Independent recomputation of R1 run metrics with separate code paths (no analyze_r1/motion imports):
reference via direct np.interp of the motion file, phase from stage_events tick index, tilt/contact from raw arrays,
particle displacement in the flask frame from particles.npz, and raw-vs-native 300 Hz joint-state consistency."""
import json, sys
from pathlib import Path
import numpy as np
def qrot(q):  # wxyz -> R
    w, x, y, z = q/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)], [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)], [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])
def review(run, motion_path):
    run = Path(run); d = json.loads((run/"result.json").read_text()); r = np.load(run/"raw.npz", allow_pickle=True)
    nat = np.load(run/"native_300Hz.npz"); par = np.load(run/"particles.npz", allow_pickle=True); mo = json.loads(Path(motion_path).read_text())
    t = np.asarray(mo["relative_time_s"]); t = t-t[0]; xy = np.asarray(mo["planar_displacement_m"]); xy = xy-xy[0]
    ev = [e for e in d["stage_events"] if e["event"].startswith("swirl")][0]; a = ev["tick"]; first = ev["first_reference_tick"]
    sel = np.where((r["stage"] == "swirl") & (r["source_frame"] >= 83))[0]
    phase = (sel-first)*.05; phase_check = float(np.max(np.abs(phase-(r["policy_time"][sel]-first*.05))))
    ref = np.c_[np.interp(phase, t, xy[:, 0]), np.interp(phase, t, xy[:, 1])]
    tcp = r["obs"][sel, 14:16]-r["obs"][a, 14:16]; e = np.linalg.norm(tcp-ref, axis=1)
    amp = float(np.mean(tcp.std(0)/ref.std(0)))
    tilt = np.degrees([np.arccos(np.clip(qrot(q)[2, 2], -1, 1)) for q in r["obs"][sel, 26:30]])
    f = r["contact"][sel, :2]; bil = float(np.mean((f > .01).all(1)))
    idx = (np.arange(len(r["obs"]))[1:])*15-1; q_consistent = bool(np.array_equal(r["obs"][1:, :7], nat["actual_q"][idx, 0]))
    acc_max = float(np.abs(nat["actual_acceleration"]).max())
    ps = par["stage"] == "swirl"; pi = np.where(ps)[0]
    loc = np.stack([(qrot(par["object_pose_wxyz"][i, 3:]).T@(par["positions"][i]-par["object_pose_wxyz"][i, :3]).T).T for i in pi]) if len(pi) else None
    disp = float(np.sqrt(np.mean(np.sum((loc-loc[0])**2, -1)))) if loc is not None else None
    return dict(run=str(run), actor=d.get("actor"), seed=d.get("seed"), rows=int(len(sel)), phase_vs_policy_time_max_s=phase_check,
                TCP_vs_video_RMS_m=float(np.sqrt(np.mean(e**2))), TCP_vs_video_max_m=float(e.max()), amplitude_ratio=amp,
                tilt_p95_deg=float(np.percentile(tilt, 95)), bilateral_contact_fraction=bil, raw_q_equals_native_300Hz=q_consistent,
                native_actual_acceleration_max=acc_max, runner_actual_acceleration_max=d["motion_maxima"]["actual_acceleration"],
                particle_local_displacement_RMS_from_first_swirl_obs_m=disp, runner_particle_displacement_RMS_m=d["particle_metrics"]["swirl_local_particle_displacement_RMS_m"],
                runner_counts=d["counts"], runner_retention_swirl=d["particle_metrics"]["minimum_strict_ideal_cavity_fraction_swirl"])
if __name__ == "__main__":
    print(json.dumps([review(p, sys.argv[1]) for p in sys.argv[2:]]))
