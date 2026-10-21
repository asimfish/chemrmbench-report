# v0.1 evaluation protocol

Active tasks are the seven listed in [the release contract](release_v0_1.md).
The authoritative fixed cases are `eval/eval_split_v0_1_1.json`, seeds1000–1049.
This file only revises T4 cue times from the previous split; all other cases
are unchanged. T6 cases remain archived and outside the v0.1 release matrix.
Development/training attempts use0–99, qualification uses5000–5002.
Do not train, calibrate, select checkpoints or tune detectors on held-out cases.

The skill track exposes public instruction, station-A RGB and simulation time.
Registered calls select public object/fixture IDs and primitive skills; motors
do not accept the correct object index, hidden count or requested hold duration.
The caller decides which object and when to press/stop. Privileged motor
geometry is encapsulated; it does not determine task-level choices.

The action track exposes both RGB cameras and18D joint position/velocity at20Hz,
and accepts nine FR3 joint targets (seven arm, two fingers), held for12 native
240Hz physics ticks. A policy never receives verifier states, sampled hidden
parameters or expert phase labels. Task grading must be independent of the
policy supplying correct phase names. The measured-v1 protocol removes expert completion/stage dependencies for all
seven tasks; see [the verdict ADR](verifier_protocol.md). Each formal baseline
(T1/T5/T7) requires its complete development audit before native evaluation.
T2 uses a 90 s horizon and measured subgoal order; its DP is deferred to v0.1.1.
Action policies save only policy_start and policy_end full-scene archives.
Historical verdicts are preserved and ongoing legacy cohorts remain explicitly
versioned; audit comparisons do not rewrite their saved files.

In paused mode, decision latency consumes no simulated time. In latency_charged
mode, measured monotonic latency advances the simulator with the prior command
held, carrying fractional ticks between calls. Both modes consume simulation
time for actuation/waiting. The release public-heuristic matrix uses paused50;
the separate paired charged-clock plumbing case is not a full second matrix.
Formal DP action evaluation currently uses paused mode. Unsupported clock/track
combinations fail explicitly.

The public heuristic reads pixels and public parameters only. Calibration is
frozen from development data. T8 requires station A; wrist-only visibility is
insufficient. No LLM/VLM evaluation is part of this release. The expert upper
bound has20 development attempts, the ablation lower bound has the matched first
10, and public/DP evaluation has50 held-out attempts. Report these separate
cohorts and intervals; do not imply a paired50-seed upper/lower experiment.

Success denominators include fail/error attempts. Wilson95% intervals are used
for binomial rates. Report timing error/latency mean and p95 with observed
counts, T8 measured first-lift choice accuracy separately from physical success, safety
coverage and violation rates, and mean simulation/wall duration. Missing
measurements remain null. Safety-force scope differs in historical verifiers;
the data card describes it rather than claiming full-robot calibrated safety.

T3/T4-v2/T7/T8 fixed-strategy upper bounds are1/3,0.2,0.2,1/3 respectively.
All must be<=0.35. With10 lower-bound attempts, one-sided binomial upper-tail
p<0.05 triggers review; do not tune the lower bound to match a desired result.

An instrumentation error or safety violation stops the current writer cohort.
Keep its error in the table and resume only never-attempted seeds in a fresh
cohort. Zero-action infrastructure retries follow the existing authorized rule
and retain both original and retry records. Never choose a best rerun.
