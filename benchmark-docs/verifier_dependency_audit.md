# Verifier dependency audit

Protocol migration: legacy → measured-v1. The audit uses development seeds0–19
only; saved verdicts are preserved. Full per-seed results are separate evidence.
Native queues already running remain legacy, with no silent scoring change.

| Task | Legacy controller dependency | Measured-v1 evidence |
|---|---|---|
| T1 pick_place | finish, command cursor, completion, expert stage registry | rigid pose/velocity, measured open fingers, lift, raw contacts |
| T2 bottle_balance | expert mode, phase=transport, fixed1920 ticks, place_release snapshot, stage registry, phase-scoped drift accumulator | ordered measured lift/placement/regrasp/return, measured transport interval, raw bilateral contacts, FK from measured joints |
| T3 pour | finish, command cursor, completion, expert stage registry | particle positions and rigid frames, measured quaternion crossings, raw grasp contacts and open fingers |
| T4-v2 press | finish, command cursor, completion, expert stage registry | benchmark cue event and physical button force crossing/deadline |
| T5 open_cabinet | finish, command cursor, completion, expert stage registry | joint opening and contiguous hold, measured release, raw robot contacts |
| T7 endpoint_stop | finish, completion, expert stage registry | raw button edges, privately sampled count, benchmark color event and decoded pixel contrast |
| T8 delayed_cue_memory | T1 administrative dependencies; motor_object_selected diagnostic | all three candidate trajectories, first measured lift, benchmark cue/go schedule and measured held-home joints |

All seven legacy verdicts had at least one controller dependency. World-owned
events and privately sampled task parameters are verifier inputs; controller
events, expert plans and controller internal state are not grading inputs.
Contact-log coverage may use the number of recorded actions, without reading
their phase, command_index, finish or other controller annotations.

The metadata counterfactual replaces stages with policy_start/end, removes the
task program, changes policy identity, clears completion and finish/cursor
annotations, and removes controller motor-selection/boundary events. It keeps
state, contact, benchmark-event and camera evidence fixed. Each task must pass
this test in all20 development attempts before its grader is admitted. Old/new
grade discrepancies require supervisor review before adoption, without tuning
parameters against these outcomes. Infrastructure errors remain in the audit.

Formal T1/T5/T7 action evaluations check their own admission before GPU launch.
Training is permitted while these CPU checks run. T2's legacy17/20 remains
historical; its main-table upper bound changes only after measured-v1 adoption.

T2 development audit completed:20/20 old/new grades agree,20/20 metadata
counterfactuals invariant,17 success/3 return failures. Remaining tasks are
still under audit; this is not a seven-task admission receipt.
