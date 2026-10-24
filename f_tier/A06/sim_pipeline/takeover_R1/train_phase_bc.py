"""Train the A06 R1 phase BC on exactly three R1-admitted teacher demos (fixed 2000 Adam updates, seed 2026102406)."""
import json, sys, time
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motion import sample
from phase_policy import PhasePolicy, phase_features, save
from analyze_r1 import analyze
def main(demo_dirs, motion_path, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=False); motion = json.loads(Path(motion_path).read_text())
    t = np.asarray(motion['relative_time_s']); duration = float(t[-1] - t[0]); X = []; Y = []; records = []
    assert len(demo_dirs) == 3
    for dd in demo_dirs:
        m = analyze(dd, motion_path); assert m['R1_teacher_admitted'], ('demo not R1-admitted', dd, m)
        d = json.loads((Path(dd)/'result.json').read_text()); r = np.load(Path(dd)/'raw.npz', allow_pickle=True)
        ev = next(e for e in d['stage_events'] if e['event'] == 'swirl_after_observed_settling'); a_tick = ev['tick']; start = ev['first_reference_tick']*.05
        anchor = r['obs'][a_tick, 14:16]; rows = np.where((r['stage'] == 'swirl') & (r['source_frame'] >= 83))[0]
        for i in rows:
            ph = float(r['policy_time'][i] - start); X.append(phase_features(ph/duration, r['obs'][i, 14:16] - anchor)); Y.append(sample(motion, ph, partition='full'))
        records.append(dict(demo=str(dd), rows=int(len(rows)), seed=d['seed'], initial_source_xy_m=d['initial_source_xy_m']))
    X = torch.tensor(np.array(X)); Y = torch.tensor(np.array(Y), dtype=torch.float32)
    pol = PhasePolicy(); pol.mean.copy_(X.mean(0)); pol.std.copy_(X.std(0, unbiased=False).clamp_min(1e-3))
    opt = torch.optim.Adam(pol.parameters(), lr=1e-3); g = torch.Generator().manual_seed(2026102406); curve = []; t0 = time.monotonic()
    for step in range(2000):
        idx = torch.randint(len(X), (64,), generator=g); loss = ((pol(X[idx]) - Y[idx])**2).mean(); opt.zero_grad(); loss.backward(); opt.step()
        if step % 200 == 0 or step == 1999: curve.append([step, float(loss)])
    with torch.no_grad(): err = torch.linalg.norm(pol(X) - Y, dim=1)*1000
    save(pol, out/'final_model.pt', dict(updates=2000, seed=2026102406, duration_s=duration, demos=records))
    rep = dict(status='CLOSED_TRAIN_ONLY_FIXED2000', rows=len(X), demos=records, curve=curve, train_error_mm_median=float(err.median()),
               train_error_mm_p95=float(torch.quantile(err, .95)), wall_s=time.monotonic()-t0, checkpoint=str(out/'final_model.pt'))
    (out/'training_report.json').write_text(json.dumps(rep, indent=2) + '\n'); print(json.dumps(rep))
if __name__ == '__main__': main(sys.argv[1:4], sys.argv[4], sys.argv[5])
