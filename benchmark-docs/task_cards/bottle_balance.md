# T2 — Bottle to balance and return

Setting: precursor_1, dosing balance and station-A FR3 in the preserved twin.
Start is the fixed home pose. Source xy±2cm and yaw±15degrees; target is public,
with no hidden M/T variable (M0/T0).

The expert still saves eight stages, but the candidate measured-v1 verifier
uses ordered measured lift, transport, released stationary balance placement,
regrasp/lift and final return. Limits: lift>=3cm, placement<=2cm, return<=1mm,
bilateral coverage>=80% of the measured transport span, relative bottle/hand
drift<=2cm, raw robot contact peak<=25N, tilt<=0.25rad and displacement<=20mm.
The former fixed1920-tick denominator and named stage predicates are removed.
The time limit is90s. See [the verdict ADR](../verifier_protocol.md) for the
predeclared interval and released/stationary convention. Action-track archives
are policy_start/end only. All20 development old/new grades agree (17 success/3 fail), and all20
metadata-invariance checks pass. The candidate upper bound uses measured-v1;
original verdict files remain unchanged. No held-out seeds were used.

Main17/20 retains strict return failures1.026,1.071,1.124mm; none were rounded
down or retried. Legacy sampled clearance9.70mm is not a continuous certificate.
The legacy17/20 remains in version history. The measured protocol also scores
17/20; T2 DP is deferred to v0.1.1. Same-process saves are supported; general cold restore is
not claimed. See [data card](../data_card.md).
