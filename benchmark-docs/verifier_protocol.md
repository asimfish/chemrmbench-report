# Policy-independent verdict protocol (Guidance 12)

Status: development audit passed for all seven tasks (140/140 grades agree,
140/140 metadata invariance checks pass). Declared before the audit. Historical
verdict.json files remain immutable. Native queues already in progress retain
the legacy protocol. The new protocol is `measured-v1`; the development audit
and metadata-invariance regression are complete. Future discrepancies still
require supervisor review without adjusting parameters to fit outcomes.

Physical grades use recorded rigid/joint states, raw contacts, benchmark-owned
world events and privately sampled task parameters. They do not read action
phase, finish flags, command cursors, expert mode, plans or stage names. Capture
integrity and full-scene archives are reported separately from physical goals.
Infrastructure errors remain errors. A complete recording is not evidence of
task success. Conversely, a controller's missing finish label cannot negate a
measured physical goal. Actions may be counted to check contact-log coverage;
their annotations are not interpreted.

T2 has a 90 s simulation-time limit. The initial measured bottle position defines
the original support height. First lift is the first measured rise of at least
3 cm. Placement is the first later measured state within 2 cm of the balance
center, with both measured fingers at least 35 mm open and bottle speed below
0.01 m/s (the existing released/stationary convention). Transport is the span
from first lift to the last state at least 3 cm above the original support before
that placement. Every physics tick in that span belongs to the denominator,
including temporary contact losses. Bilateral contacts are its numerator; the
minimum remains 80%, with no fixed 1920-tick requirement. Selecting only ticks
with bilateral contact would make coverage tautological and is prohibited.

The regrasp requires measured bilateral contact after placement, followed by a
second lift of at least 3 cm above the measured placed height. Return uses the
final bottle pose, with the original 1 mm limit. Relative bottle/hand drift is
recomputed over the measured transport span using measured joint positions and
authored FR3 forward kinematics, keeping the existing 20 mm limit. No expert
transport accumulator is used. Raw robot contact impulse/dt is checked against
25 N. Tilt and final displacement safety limits are unchanged. Event order must
be lift, placement, regrasp, return. All measured criteria and the horizon must
hold; stage archives are not subgoal evidence.

T1/T3/T4-v2/T5/T7 retain their physical thresholds and remove only administrative
expert-completion/stage requirements. T8 grades the privately specified candidate
directly from all three measured trajectories; its choice diagnostic is the
first physically lifted candidate, not a controller's motor-selection event.
World cue, tilt and button/color events remain benchmark-owned evidence; raw
contact/pose checks independently validate operation events where available.

The action track stores full-scene `policy_start` and `policy_end` archives.
The regression removes expert metadata, renames these archives and changes all
action annotations while preserving physical evidence. Status, success,
pass/failure vectors, timing, memory and physical metrics must remain identical.
No held-out seeds are used to develop this protocol.

Primary-table scores must identify their verdict version. For native queues
already started with legacy grading, `chemrm.bench.score` replays only closed,
accepted recordings with the frozen `measured-v1` protocol. It writes a separate
score record bound to the original episode and retained grade, never replacing
`verdict.json`. Any status, success, physical/safe-success or pass-vector change
stops adoption and creates `REVIEW_REQUIRED.json`; it does not trigger parameter
search. This is application of the development-audited protocol, not protocol
development on held-out cases. The release gate requires every present primary
score to use `measured-v1`, in addition to all cohort-completeness gates.
