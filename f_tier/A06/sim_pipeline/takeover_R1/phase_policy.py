"""A06 R1 phase-conditioned swirl BC (takeover). The student generates the anchor-relative TCP XY target from a
phase clock and its own TCP state; it never receives the video reference at execution time."""
import numpy as np, torch, torch.nn as nn
K = 6
def phase_features(phase, tcp_minus_anchor_xy):
    p = float(np.clip(phase, 0., 1.)); k = np.arange(1, K + 1)
    return np.r_[p, np.sin(2*np.pi*k*p), np.cos(2*np.pi*k*p), 50.*np.asarray(tcp_minus_anchor_xy, float)[:2]].astype(np.float32)
DIM = 1 + 2*K + 2
class PhasePolicy(nn.Module):
    def __init__(self, seed=2026102406, scale=.03):
        super().__init__(); torch.manual_seed(seed); self.scale = scale
        self.net = nn.Sequential(nn.Linear(DIM, 64), nn.SiLU(), nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 2))
        self.register_buffer('mean', torch.zeros(DIM)); self.register_buffer('std', torch.ones(DIM))
    def forward(self, x): return self.scale*torch.tanh(self.net((x-self.mean)/self.std))
    @torch.no_grad()
    def offset(self, phase, tcp_minus_anchor_xy):
        return self.forward(torch.from_numpy(phase_features(phase, tcp_minus_anchor_xy))[None])[0].double().numpy()
def save(policy, path, meta): torch.save(dict(schema='A06_R1_phase_BC_v1', state=policy.state_dict(), scale=policy.scale, **meta), path)
def load(path):
    d = torch.load(path, map_location='cpu', weights_only=False); assert d['schema'] == 'A06_R1_phase_BC_v1' and d['updates'] == 2000
    p = PhasePolicy(scale=d['scale']); p.load_state_dict(d['state']); return p.eval()
