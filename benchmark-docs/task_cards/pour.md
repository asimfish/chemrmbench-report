# T3 — Duration-controlled pour

Engineering task, chemistry_calibrated=false. A rigid vessel transfers125
particles into a receiver in the twin. Source xy±1cm, yaw±15degrees; fixed
home posture. Public instruction specifies tilt hold D in{2,4,6}s. No hidden
answer parameter. The skill agent controls start/stop separately (M0/T-dur).

Success requires received fraction>=0.85, spilled<=0.03, source residual<=0.05,
unaccounted<=0.10; measured tilt duration error<=max(0.2s,0.05D). Events arise
from measured tilt crossing, not command initiation. Receiver safety uses
the unchanged SafeLab-style25N/0.25rad/20mm limits with measured coverage.

Main17/20 retains one spill failure0.032>0.03 and two infrastructure/runtime
errors. Fixed4s lower bound4/10; theoretical optimum1/3. Legacy sampled
clearance9.45mm is recorded only. Particle states are evidence readback,
not restorable stage state. No calibrated fluid force, chemistry or particle
cold reconstruction claim. See [protocol](../evaluation_protocol.md).
