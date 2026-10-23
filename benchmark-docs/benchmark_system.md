# ChemRMBench: one research question, controlled workflows

The [protocol-family experimental design](experimental_design.md) now defines
the primary organization, with [six compatible profiles](hierarchical_benchmark.md)
over three task scopes. This earlier family matrix remains the diagnostic-control
layer; its routing-first roadmap is retained as historical planning and is
superseded by the source-grounded process-contract frontier in that document.

Design candidate, 23 October 2026. The seven-task v0.1 protocol, data and frozen
split remain unchanged. The new 20 diagnostic specifications and four long
protocols below are **designs**, with no newly qualified native tasks implied.

## Research question and contribution

Can a laboratory agent retain the right fact from an earlier event and perform
the corresponding physical operation at the right time, through a multi-stage
protocol? A final correct object pose cannot establish either ability: a robot
may choose the right vessel by a visible shortcut, or reach the right endpoint
after an unacceptable delay. Conversely a missed deadline can be caused by a
failed grasp rather than a clock or memory failure.

The benchmark therefore isolates manipulation, event memory, operation timing
and their interaction using the **same workflow**, then tests their composition
over longer protocols. SafeLab's assets, operation semantics and safety metrics
are retained. ChemLab adds articulated-object variation, with separate licence
and qualification. Neither asset diversity nor chaining policy-training methods
is the research contribution. Chemical fidelity is a separate, uncalibrated
engineering boundary in the current simulator.

## Task hierarchy

1. **Skill and instrumentation layer:** the seven existing native tasks calibrate
   grasp/place, balance transport, pouring, press, articulated access, endpoint
   response and transient-cue observation. T6 remains deferred.
2. **Workflow layer:** five families, each with the same four memory/timing
   conditions. A changed object, seed or duration is an instance, not a new task.
3. **Protocol layer:** four long workflows retain physical state across stages;
   their semantic nodes are not yet qualified robot stages.
4. **Generalization layer:** new objects, compositions and dependency graphs are
   separate held-out axes. Position/light changes alone are environment variation.

| Workflow family | Earlier fact | Timing requirement | Existing building blocks |
|---|---|---|---|
| Sample routing | Which of three identical samples | Initiate grasp after transfer cue within a candidate 10 s window | T1, T8, T4 |
| Balance and return | Which return slot | Residence interval on balance, 2/4/6 s | T2 |
| Dispensing | Which receiver | Tilt interval, 2/4/6 s | T3, T8 |
| Endpoint dosing | Which colour is the requested endpoint | Finish within 5 s, zero extra dose | T7, T4 |
| Instrument cycle | Which fixture/door | Open residence interval, then close | T5, qualified ChemLab fixtures |

Every row contains `M0_T0`, `M1_T0`, `M0_T1`, `M1_T1`:

| Condition | Cue availability | Temporal grading |
|---|---|---|
| M0/T0 | Persistent cue | Physical goal and safety only |
| M1/T0 | One-second transient cue, then 3/10/20 s retention | Physical goal and safety only |
| M0/T1 | Persistent cue | Physical goal, safety and declared timing |
| M1/T1 | Transient cue and retention | Physical goal, safety and declared timing |

All four cells have the same sampled layout, target, durations, endpoint stream
and goal graph for a given family/seed. Timing is sampled even when not graded.
The M0/M1 intervention changes cue persistence only. The compiler stores answer
bindings and future event schedules exclusively in `privileged`; public goals
refer to roles, not hidden indices. Future native adapters must preserve these
contracts. For M1, different cue histories must yield indistinguishable current
pixels but different correct decisions. A specification check cannot replace
this pixel check or public-observation solvability qualification.

The endpoint extension uses a target-independent three-colour stream with a
remembered target; it is a new design, not a reinterpretation of T7's existing
single-endpoint data. Instrument closing is a missing skill, not an achieved
capability. Routing's candidate window is relative to a cue sampled 2–47 s after
the retention gate; this is not a modification of T4's frozen 3 s window.
New thresholds remain candidate settings until development qualification.

## Formalization and metrics

A specification is `τ = (S, O, G, Ω, M, T, C)`: scene, object roles, a directed
acyclic goal graph, observation schedule, remembered facts, temporal constraints
and safety conditions. `TaskProgram` owns the scene/object/graph schema; this
suite composes its memory and timing contract without replacing the old schema.
A measured trace supplies physical states, contacts and benchmark-owned events.
Controller phase labels and saved stage names are not goal evidence.

For a duration constraint, report `e = |(t_stop − t_start) − D|`, early/late
violations and the pass threshold. Deadline and endpoint tasks report response
lag and anticipation/overshoot separately. Success requires physical completion,
all applicable timing constraints and safety. Missing instrumentation is not a
clean pass. Record simulation time, wall time and the selected paused or
latency-charged clock separately.

Let `P_mt` be success in a matched cell. Report all four values, memory gaps
`P_00−P_10` and `P_01−P_11`, timing gaps `P_00−P_01` and `P_10−P_11`, and the
interaction `P_11−P_10−P_01+P_00`. Use paired uncertainty over shared instances;
do not subtract Wilson intervals and call that a paired confidence interval.
Use Wilson intervals for individual success rates. Macro-average families
equally, retaining every cell and failure denominator; do not let a family with
more object instances dominate the headline score. Report physical completion,
timing error, memory decision accuracy and safety violations beside success.

## Long protocols and stage preservation

| Protocol | Semantic nodes in current specification | Missing integration |
|---|---:|---|
| Select → weigh → return | 16 | Preserve selected sample and return-slot bindings |
| Weigh → timed dispense → return | 19 | Same source, contacts and clocks across fragments |
| Select → endpoint → archive | 17 | Sample, endpoint rule and archive destination bindings |
| Open → load → process → unload → close | 19 | Instrument closing and load/unload expert |

The first three concatenate semantic fragments; this is a goal-graph
specification, not proof that independently initialized controllers compose.
All remembered slots must be disclosed once at protocol start. Later fragments
replace cue presentation and retention setup with current-state observation and
measured prerequisite checks; they may not re-display the answer. The native
adapter must enforce and audit this observation schedule before making any
long-horizon memory claim.
An executor must check measured preconditions at each handoff, preserve the
same object registry and simulation clock, and never reset between fragments.
All completed and failed prefixes retain full state, events, action/video time
indices and parent-stage links. Score whole-protocol success plus measured
subgoal progression and earliest unmet dependency. A successful prefix is not a
successful complete protocol.

Existing T2 **already** saves eight live stages and continues in one process.
`python -m chemrm.bench.stage_chain EPISODE` audits archive counts, identities,
joint/control completeness, event cursors and clocks. This checks recorded
boundary consistency; archives alone do not prove uninterrupted simulation.
Arbitrary-stage new-process restoration is not implemented; ordinary historical
cold coverage remains 1/8. This plan does not reopen cold-reconstruction work.

## ChemLab's role

Ten assets passed passive physics checks; four have explicit handle contracts;
none has passed robot opening qualification. Six still need contact annotation.
Ossila has an actual in-twin inspection video; its attempted complete CPU paths
did not pass admission. Inspection is not an opening demonstration.

Promote an asset only through: passive admission → explicit handle/contact
contract → full-arm opening **and closing** path checks → three native
qualification seeds → public-observation instance. Retain every failed prefix.
Admitted objects form an object-held-out set; do not train on those objects.
Instrument selection among several fixtures additionally needs a feasible shared
layout. Unqualified meshes may not silently become benchmark distractors.
Keep MBZUAI attribution and CC BY-NC 4.0; mass/units/contact dynamics remain
unvalidated engineering estimates. Do not count ten assets as ten tasks.

## Experimental plan and implementation order

1. **Specification gate (CPU, now):** 20 paired templates plus four protocol
   DAGs, private/public split, existing temporal checkers and archive-chain audit.
   Generate only development/qualification examples, not a new held-out split.
2. **First native family:** routing's four conditions, reusing T1/T8. Admit the
   three-candidate path and cue/clock adapter, then three qualification seeds
   per condition. Stop on physical or instrumentation failure. Check that
   removing memory or timing actually impairs the applicable conditions.
3. **Next families:** balance and dispensing, then the endpoint extension.
   Instrument cycles follow qualified articulated assets; T6 is not a dependency.
   Existing v0.1 experiments continue under their frozen protocols.
4. **Long integration:** first select/weigh/return in one live environment.
   Qualify handoffs before extending the other three protocols. Do not produce
   a long-task result by concatenating separately reset videos.
5. **Evaluation:** once qualified, freeze a new split with matched seeds across
   cells and separate object/composition/dependency holdouts. Privileged expert,
   public-observation heuristic, no-memory and no-timing controls precede model
   comparisons. Keep the old v0.1 scores separate. No LLM/VLM calls are authorized.

The analytical constant-response ceilings are routing 10/45, duration 1/3 and
endpoint fixed-ordinal 1/3, under their declared uniform distributions. They are
not bounds on arbitrary policies. Confirm that empirical ablations match the
intended task difficulty; account for finite-sample uncertainty. The old T7's
1/5 and T4-v2's 1/5 bounds remain unchanged in their old reports.

Native runtime and memory costs must be measured before estimating a new
evaluation campaign. The 24 specifications are not a request to allocate 24
jobs. Fill existing admitted RTX capacity first; use four cards only for four
ready workloads. Do not reserve eight cards or allocate unused tensors to make
utilization look higher. Training remains within its existing 64 GPU-hour cap.

## Reproduction of design artifacts

```bash
python -m chemrm.bench.suite --out workflow_inventory.json
python -m chemrm.bench.suite --template dispensing.M1_T1 --seed 5000 --out qualification_spec.json
python -m chemrm.bench.stage_chain /persistent/existing/native_episode
```

`qualification_spec.json` contains private world parameters and is **not** a
public policy input or website download. `workflow_inventory.json` contains
specification status and no sampled answers. Native execution deliberately
rejects design-only templates; original collection still selects seven tasks.
