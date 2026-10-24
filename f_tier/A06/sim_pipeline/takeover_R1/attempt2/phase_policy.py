"""A06 R1 attempt 2 phase-only swirl BC (takeover). Single change vs attempt 1: inputs are the phase clock only
(Fourier K=24); the TCP-minus-anchor state input is removed (attempt 1 copied it -> closed-loop positive feedback).
The student never receives the video reference or its own state; the shared C3 executor supplies feedback."""
import numpy as np, torch, torch.nn as nn
K = 24
def phase_features(phase, tcp_minus_anchor_xy=None):
    p = float(np.clip(phase, 0., 1.)); k = np.arange(1, K + 1)
    return np.r_[p, np.sin(2*np.pi*k*p), np.cos(2*np.pi*k*p)].astype(np.float32)
DIM = 1 + 2*K
class PhasePolicy(nn.Module):
    def __init__(self, seed=2026102406, scale=.03):
        super().__init__(); torch.manual_seed(seed); self.scale = scale
        self.net = nn.Sequential(nn.Linear(DIM, 64), nn.SiLU(), nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 2))
        self.register_buffer("mean", torch.zeros(DIM)); self.register_buffer("std", torch.ones(DIM))
    def forward(self, x): return self.scale*torch.tanh(self.net((x-self.mean)/self.std))
    @torch.no_grad()
    def offset(self, phase, tcp_minus_anchor_xy=None):
        return self.forward(torch.from_numpy(phase_features(phase))[None])[0].double().numpy()
def save(policy, path, meta): torch.save(dict(schema="A06_R1_attempt2_phase_only_BC_v2", K=K, state=policy.state_dict(), scale=policy.scale, **meta), path)
def load(path):
    d = torch.load(path, map_location="cpu", weights_only=False); assert d["schema"] == "A06_R1_attempt2_phase_only_BC_v2" and d["updates"] == 2000 and d["K"] == K
    p = PhasePolicy(scale=d["scale"]); p.load_state_dict(d["state"]); return p.eval()
