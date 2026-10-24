"""Diagnose the R1 phaseBC overshoot: commanded vs reference amplitude, closed-loop state-feature dependence, saturation."""
import json, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motion import sample
from phase_policy import load, phase_features
M = Path("/data/liyufeng/a06_runs/m03"); motion = json.loads(Path(sys.argv[1]).read_text())
t = np.asarray(motion["relative_time_s"]); duration = float(t[-1]-t[0]); pol = load(M/"bc_train/final_model.pt")
def rows_of(run):
    d = json.loads((run/"result.json").read_text()); r = np.load(run/"raw.npz", allow_pickle=True)
    ev = next(e for e in d["stage_events"] if e["event"] in ("swirl_after_observed_settling", "swirl")); a = ev["tick"]; s = ev.get("first_reference_tick", a+1)*.05
    rows = np.where((r["stage"] == "swirl") & (r["source_frame"] >= 83))[0]; ph = r["policy_time"][rows]-s
    ref = np.stack([sample(motion, float(max(p, 0)), partition="full") for p in ph]); anc = r["obs"][a, 14:16]
    return dict(ph=ph, ref=ref, tcp=r["obs"][rows, 14:16]-anc, cmd=r["target"][rows, :2]-anc)
def J(p, rel):
    x = torch.from_numpy(phase_features(p, rel))[None].requires_grad_(True); y = pol(x)[0]
    return np.stack([torch.autograd.grad(y[i], x, retain_graph=True)[0][0, -2:].numpy()*50 for i in range(2)])
out = {}
for name in ["demo_2026102206", "phaseBC_2026102217", "phaseUntrained_2026102216"]:
    q = rows_of(M/name); sd = lambda v: np.std(v, axis=0)/np.std(q["ref"], axis=0)
    o = dict(rows=len(q["ph"]), cmd_amp_ratio=sd(q["cmd"]).round(3).tolist(), tcp_amp_ratio=sd(q["tcp"]).round(3).tolist(),
             tcp_vs_cmd_RMS_mm=float(np.sqrt(np.mean(np.sum((q["tcp"]-q["cmd"])**2, 1)))*1e3), cmd_vs_ref_RMS_mm=float(np.sqrt(np.mean(np.sum((q["cmd"]-q["ref"])**2, 1)))*1e3),
             cmd_saturated_frac=float(np.mean(np.abs(q["cmd"]) > .029)), ref_max_abs_mm=(np.abs(q["ref"]).max(0)*1e3).round(2).tolist())
    if name.startswith("phaseBC"):
        ol = np.stack([pol.offset(p/duration, rr) for p, rr in zip(q["ph"], q["ref"])])
        o["policy_on_ideal_state_vs_ref_RMS_mm"] = float(np.sqrt(np.mean(np.sum((ol-q["ref"])**2, 1)))*1e3)
        Js = np.stack([J(p/duration, rr) for p, rr in zip(q["ph"][::5], q["ref"][::5])])
        ev = np.linalg.eigvals(Js); o["d_offset_d_state_eig_abs_median"] = float(np.median(np.abs(ev))); o["d_offset_d_state_eig_abs_max"] = float(np.abs(ev).max())
        o["d_offset_d_state_diag_median"] = np.median(np.stack([np.diag(j) for j in Js]), 0).round(3).tolist()
        o["first_10_ticks_cmd_mm"] = (q["cmd"][:10]*1e3).round(1).tolist(); o["first_10_ticks_ref_mm"] = (q["ref"][:10]*1e3).round(1).tolist()
    out[name] = o
print(json.dumps(out))
