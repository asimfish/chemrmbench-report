# ChemRMBench: three task scopes and compatible chemical-time profiles

Design revision, 23 October 2026. This document refines the earlier five-family
matrix into a reported capability hierarchy. Old v0.1 tasks, verdicts, seed
splits, videos and the 20 prototype M/T specifications remain unchanged.
The new chemical cases are source-grounded designs, not native successes.
The [revised experimental design](experimental_design.md) is now primary:
protocol family × atomic/subprotocol/complete scope. It separates five scientific
roles of time, control logic, memory and batching. The six labels below are
compatible entry profiles, not a total ordering of difficulty. They must not
force source methods into scientifically invalid untimed counterparts.

## Why these compatible profiles

[LabUtopia, Section 4.1](https://arxiv.org/html/2505.22634v2) reports atomic,
short-horizon, generalizable short-horizon, long-horizon and mobile tasks.
Its evaluation also includes terminal-state persistence. We adopt its clear
separation of task complexity, while reporting memory and generalization as
horizontal axes and explicitly separating process-time obligations. We do not
claim that earlier work has no temporal checks, or that hierarchy alone is new.

The research question is whether an agent can retain experimental history and
coordinate physical actions with evolving process state, from one operation to
a complete experiment. Chemical progress, measured action timing and history
dependence must be independently visible in the evaluation.

| Level | Task scope | Example and question |
|---|---|---|
| L1 | One atomic operation | Pick, place, press, open, close or pour from an already held vessel. Can the operation physically succeed? |
| L2 | Same atomic operation with time contract | Complete within a window, maintain a process for a duration, stop after a visible event or control a rate. Is physical completion timely? |
| L3 | Local composition, core 2–5 operations | Pick→place on device→activate; open→insert sample→close. Can skills compose? |
| L4 | Local composition with process timing or reaction logic | Develop colour→wait appropriately→read in-window; heat→detect state→stop or continue. Does action depend on the right condition and time? |
| L5 | Complete experiment within a declared scope | Preparation→execution/reaction/separation→measurement→result record→safe shutdown. Can the whole protocol be completed? |
| L6 | Time-sensitive complete experiment | Multiple process timers, valid sample lifetimes, state-triggered actions and shared-instrument scheduling across the complete protocol. Can history and time remain correct throughout? |

These are curriculum and reporting profiles, not a guarantee that every L2 task
is easier than every L3 task. Local 6–10-operation extensions are reported
separately. A long sequence of button presses does not automatically become a
complete experiment. A full protocol requires a named source-defined scope,
all declared phases and a measured terminal result, not just more nodes.

An operation is a registered, meaningful laboratory action with an entry state
and a measured termination condition. Internal waypoints, robot ticks, passive
observations, waits and archive saves do not add operations. Repeated physical
actions count when executed; a dosing loop cannot be renamed an atomic skill
to make its horizon smaller. A maintained registry must freeze the granularity.

For conditional atomic tests such as pouring, establish the admitted ready
state with a live setup prefix. Record setup attempts, failures and videos;
report setup success, atomic success conditional on setup, and overall success.
Do not discard failed prefixes. This does not require the currently unsupported
arbitrary-stage cold restoration. A standalone primitive is newly qualified
only after its own ready-state and measurement protocol is checked.

## Ten composable operators, below the scientific classification

The types are not ten additional difficulty levels. A task can combine several.
Every relation has an identified sample, operation and observable event origin.

| Type | Mathematical or logical contract | Laboratory interpretation |
|---|---|---|
| Completion deadline | `t_complete − t_ref ≤ D` | Complete a measurement before its sample holding time expires |
| Scheduled window | `a ≤ t_action − t_ref ≤ b` | Read after colour develops but before the valid window closes |
| Duration | `D_min ≤ t_stop − t_start ≤ D_max` | Incubate or stir under the stated process condition |
| Event response | `0 ≤ t_response − t_condition ≤ δ` | Respond to an actual measured transition |
| Rate or slope | `r_min ≤ dx/dt ≤ r_max` over the active interval | Control delivery flow or temperature ramp |
| Order and relative gap | `A before B`, with a minimum/maximum interval | Cool before transfer, or read within a gap after treatment |
| Synchronization | Coupled intervals or acquisition span across samples | Treat standards/unknowns consistently and share an instrument |
| Cumulative exposure | `Q = integral f(state(t)) dt` | Integrate measured light/thermal exposure, with a declared model |
| Continuous persistence | Predicate stays true continuously for a specified dwell | Confirm a stable endpoint; a false interval resets the clock |
| Periodic sampling | `t_k = t_0 + kΔ ± ε` for every required index | Acquire a kinetic time series; missing points remain missing |

Temperature-qualified residence is not heater-on duration. A stable colour is
not the sum of intermittent flashes. Constant mass is a different, historical
comparison between repeated heat/cool/weigh cycles, not a continuous-colour
timer. A cross-sample acquisition span is not a per-sample reagent-addition
deadline. These differences must survive serialization and offline grading.

`TDeadline`, `TDuration`, `TEvent` and `TRate` are reused where their semantics
match. Early-action guards and event scope remain necessary. Generic native
synchronization, periodic-acquisition and chemical-exposure referees are not
implemented merely by listing these types; the existing thermal model is an
uncalibrated F0 diagnostic. Unsupported relations must fail closed.

## Reaction logic is an additional process contract

Goal milestones remain a DAG in `TaskProgram`. Conditional and repeated process
behaviour belongs in a separate benchmark-owned state model; it must not be
forced into a cycle in the goal DAG or delegated to a policy's phase labels.

- **Preconditions:** sample identity, correct contents, fixture state and valid
  measurement range before an action.
- **State guards:** temperature in a band, phase boundary visible, bulk colour
  settled, or previous/current masses sufficiently close.
- **Branches:** stop or continue dosing; resume waiting if emulsion remains;
  repeat a processing cycle when the termination measurement is not met.
- **Loops:** repeat measured operations with an explicit scientific stop rule
  and a separately declared engineering timeout/cycle cap.
- **Invariants:** sample preservation, safe heating, no extra dose after an
  accepted endpoint, and instrument occupancy rules.
- **Recovery:** retry only while the sample and time window remain valid.
  Restarting a controller must not reset sample age or reaction progress.

Examples: an endpoint candidate pauses dosing while persistence is checked;
if the colour fades, the process can continue. An actual overshoot is failure.
After a drying cycle, compare the new mass against the previous completed
cycle and repeat if necessary. Holding a balance reading still does not prove
constant mass. These are observable process rules, not fixed successful scripts.

## Source-grounded experimental catalogue

The maintained [YAML catalogue](../data/chemistry-design-cases.json) records 13 themes,
their source links, exact parameter anchors, conditions, memory demands and
missing instrumentation. These themes can produce tasks at more than one
level; they are not 13 newly supported native experiments.

| Theme | Genuine temporal/process feature | Candidate use |
|---|---|---|
| Indicator titration | Near-endpoint adaptive addition and persistent colour confirmation | L4 endpoint fragment; L6 full analysis under this timed protocol |
| Iodine clock | Measure the interval from mixing to colour change | L4 event recording; L6 trial series |
| Orthophosphate Method 8114 | At 23°C, reaction wait then a bounded sample-reading window | L4 single sample; L6 multi-sample scheduling |
| Free/total chlorine | Different method-specific development/read intervals | L4 method binding; L6 mixed-method batch |
| BCA assay | Temperature-qualified incubation, cooling and a shared reading span | L4 single tube; L6 standards plus unknowns |
| Recrystallization | Hot filtration, gradual cooling and observed nucleation | L4 subflow; L5/L6 purification protocol |
| Gravimetry | Conditioned digestion and repeat drying/cooling/weighing to constant mass | L4 loop; L6 full analysis under this timed protocol |
| Liquid-liquid extraction | Mix/vent cycles, emulsion resolution and interface-controlled drainage | L4 separation fragment; L5/L6 extraction |
| Melting-point measurement | Switch to a controlled ramp near the measurement region | L2 ramp; L4/L6 measurement |
| Aspirin back titration | Method-specific heating/cooling and a state-dependent check | L6 content analysis |
| Winkler dissolved oxygen | Sample preservation and a source-specific holding-time deadline | L6 age-aware sample scheduling |
| Actinometry | Instrument-specific cumulative exposure and applicability limits | Later exposure-control study |
| Crystal-violet kinetics | Periodic timestamped absorbance acquisition | L4 time series; L6 multi-condition kinetics |

Specific rules verified from primary sources:

1. The [UW-Madison indicator module](https://www2.chem.wisc.edu/deptfiles/genchem/lab/labdocs/modules/titrate/titrind.htm)
   uses at least 30 seconds of persistent final colour. This supports endpoint
   confirmation, not a universal whole-titration deadline or continued addition.
2. [Hach Method 8114](https://cdn.hach.com/7FYZVWYB/as/9wp6b7c89p2jrbhnvw9n5fnn/Phosphorus_Reactive_Orthophosphate_Molybdovanadate_Method_8114_Test_N_Tube_Vials_DOC3165301116)
   specifies 7 minutes at 23°C, then reading within 2 minutes after timer expiry.
   It also documents alternative waits at other temperatures **and** temperature
   interferences. First implementation should use 23°C, not claim equal accuracy
   for all temperature variants.
3. The [Thermo BCA test-tube guide](https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0011430_Pierce_BCA_Protein_Asy_UG.pdf)
   specifies standard incubation at 37°C for 30 minutes, then cooling. Its
   10-minute acquisition condition spans the set of tubes, rather than starting
   separately at each reagent addition.
4. [CSUDH sulfate gravimetry](https://www2.csudh.edu/oliver/che230/labmanual/gravsulf.htm)
   supplies a specific digestion condition and a 0.2mg successive-cycle mass
   criterion. Those numbers belong to that method, not every drying task.
5. [Thermo's crystal-violet lesson](https://assets.thermofisher.com/TFS-Assets/CAD/Application-Notes/FL54678-genesys-kinetics-general-chemistry-lesson-plan.pdf)
   records absorbance every 30 seconds after live acquisition begins, ending
   five minutes after reaction initiation. Preserve both anchors and actual
   timestamps; do not invent a reading at reaction time zero. Timestamp jitter
   and missing-data rules need a separate instrumentation contract.
6. The [archived EPA monitoring table](https://archive.epa.gov/water/archive/web/html/table52.html)
   describes an 8-hour collection-to-measurement bound for field-fixed Winkler
   samples measured in the laboratory. It is a specific archived reference,
   not a claim about a universal current regulatory requirement.

The other cases retain their direct university, manufacturer or original-paper
sources in the catalogue. Reaction recipes and reagent preparation are outside
this task-design document.

## Priorities and asset roles

Develop three coherent complete-protocol families instead of separately adding
unrelated button tasks: **titration/content analysis**, **water colourimetry with
separate sample timers**, and **drying/constant-mass analysis**. Use iodine-clock
and crystal-violet subflows to validate event measurement and periodic sampling.
Recrystallization and extraction follow a validated phase/thermal model.

Current ChemLab instruments can support balances, oven access and mixing where
their contracts actually match. A turbidity meter, water-activity meter or
polarimeter must not be relabelled an absorbance spectrophotometer because it
has a screen. Colourimetry requires an appropriate qualified instrument/readback
or an explicitly labelled engineering surrogate. Ten passive asset admissions
remain zero robot-qualified new-instrument tasks. CC BY-NC attribution remains.

## Memory, timing and fidelity controls

Memory is orthogonal to the levels: remembered sample/rule identities, earlier
mass/volume readings, timer origins and unfinished commitments. Report fact
count, retention, interference and clock access. At higher levels some new
results must be learned during execution; do not announce future reaction
outcomes at protocol start. For an isolated instruction-memory test give the
relevant instruction once; for procedural history test actual measured results.
Do not refresh hidden answers at stage boundaries.

The previous four M/T cells remain useful diagnostic relaxations. Removing
scientifically required timing from a score does not turn the resulting run
into a valid chemical method. L5 can use intrinsically less time-sensitive
protocols, while L6 reports genuine timing obligations. Across different
experiments, level differences are descriptive, not paired causal effects.

Not every method has a legitimate untimed counterpart. The selected indicator,
sulfate-gravimetry, aspirin and preserved-sample Winkler procedures already
contain explicit time obligations; their full forms belong in L6. Calling them
L5 would require a different justified protocol, not deleting required timings.

A prescribed fixed wait can be the correct policy for a standard method. The
earlier 35% fixed-strategy ceiling is a gate for randomized diagnostic variants,
not a rule that every chemistry task must defeat a clock-based policy. Randomize
sample start times, method bindings and admissible process conditions where
appropriate; never invent incompatible reaction times to force an ablation to
fail. A claim of required memory needs different histories with the same
current public evidence but different correct decisions, not just a long delay.

Time anchors follow the selected method: stable bath conditions, sample entry,
mixing, instrument timer start or actual acquisition are different events. Do
not infer a new sample-equilibration convention where the source does not specify
one. Likewise, cutting heater power and a sample actually cooling are different
measurements; thermal inertia belongs in the process and quality checks.

Store source parameter, source conditions, event anchor, simulation parameter,
time mapping and tolerance provenance separately. Real-method times, robot
timeouts and deliberate engineering thresholds are distinct. If minutes are
compressed, label `engineering_time_scaled`, keep the original value and adjust
the declared process model consistently. Do not silently change robot dynamics,
safety integration or comparison denominators. Compression changes the ratio
between reaction and motion times, so results are reported as a separate setting.
No compression schedule or new chemical threshold is activated by this design.

Record robot simulation time, process time and wall time. In latency-charged
mode thinking advances the appropriate process state; paused mode is a separate
simulator setting. Save active timers, sample identities, process state and
instrument occupancy alongside physical state at every meaningful boundary.
Existing T2 archives prove neither calibrated chemical state nor general cold
reconstruction; those capabilities remain limited as previously documented.

## Current evidence and implementation boundary

| Existing native task | Semantic profile | Evidence caveat |
|---|---|---|
| T5 open_cabinet | L1 | One opening operation; no new standalone-primitive qualification implied |
| T4-v2 press | L2 | One timed press from a ready pose |
| T1 pick_place | L3, two operations | Internal six-stage recording does not change the count |
| T2 bottle_balance | L3, four operations | Eight full-state saves; not a full chemical experiment |
| T8 delayed cue | L3, memory variant | Two manipulation operations; cue/retention do not inflate the count |
| T3 pour | L4 engineering proxy | Three operations with timing, no calibrated chemistry |
| T7 endpoint stop | L4 engineering proxy, 4–8 presses | Variable local horizon; binary colour model remains an engineering proxy |

These mappings describe existing scope; they do not award new level certification.
No calibrated complete L5/L6 experiment has yet been accepted. The implementation
now contains a six-level specification classifier, a ten-type contract catalogue,
source-parameter validation and 13 source-grounded case designs. Native process
adapters, reaction-state validation and model experiments still require work.

Next bounded implementation: choose the 23°C colour-development subflow and the
indicator-persistence subflow, define their measured anchors and public sensor
contracts, and pass CPU process/referee tests before GPU scene qualification.
Frozen v0.1 collection and baseline rules continue independently. No additional
GPU reservation or LLM/VLM evaluation is authorized by this document.
