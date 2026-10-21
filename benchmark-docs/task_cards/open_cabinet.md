# T5 — Open a passive oven door

Setting: existing station-A drying-oven Door_joint in the twin, not a screw
cap. FR3 starts at fixed home. Initial door angle varies0–5degrees; articulated
range0–100degrees. Public instruction identifies the fixture; no hidden cue
or duration variable (M0/T0).

Success: measured opening>=70% of joint range, continuously held>=0.5s,
physical handle contact and released fingers, with no safety violation.
The arm commands nine FR3 joint targets only; the door is passive, stiffness0,
damping0.4. Stages are approach, grasp, open, hold, release, retreat.
Safety25N/0.25rad/20mm covers reported robot contacts and unintended chassis
movement; intentional door travel is excluded from chassis drift.

Main20/20. Legacy sampled clearance8.81mm is recorded, not a continuous10mm
certificate. Action grading can use measured joint history and policy_start/end
registries; no expert door-angle label goes to the policy. ChemLab novel-door
objects are deferred to v0.1.1; real bottle-cap unscrewing remains outside scope.
