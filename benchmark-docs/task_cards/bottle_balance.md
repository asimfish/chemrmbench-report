# T2 — Bottle to balance and return

Setting: precursor_1, dosing balance and station-A FR3 in the preserved twin.
Start is the fixed home pose. Source xy±2cm and yaw±15degrees; target is public,
with no hidden M/T variable (M0/T0).

The eight expert stages are approach, grasp, lift, transport, place_release,
regrasp, return, retreat. Existing physical grading requires lift>=3cm, target
distance<=2cm at placement, final return error<=1mm, bilateral transport
contact>=80% over at least1920 physics ticks, relative drift<=2cm, and complete
registered stage evidence. Safety limits remain25N/0.25rad/20mm; the historical
peak-force readback specifically covers robot/bottle contact.

Main17/20 retains strict return failures1.026,1.071,1.124mm; none were rounded
down or retried. Legacy sampled clearance9.70mm is not a continuous certificate.
Stage-dependent grading must be resolved before admitting an unlabeled DP
action result. The candidate does not substitute missing stage evidence with
a favorable score. Same-process saves are supported; general cold restore is
not claimed. See [data card](../data_card.md).
