# ChemRMBench: task scopes, chemical processes and identifiable experiments

Design revision, 23 October 2026. This is the primary organization of the next
benchmark expansion. The earlier six L labels remain compatibility profiles,
not an ordinal difficulty scale. All frozen v0.1 data and verdicts are unchanged.
This document adds no native task, calibrated process, training job or model call.

## 1. Separate the questions before adding tasks

The previous proposal mixed three different questions: how much of an experiment
is performed, which process conditions matter, and what information must be
remembered. Its thirteen chemical themes also lacked common experimental
boundaries. More tiers or more names do not resolve those problems.

The primary index is **protocol family × task scope**. Process logic, temporal
requirements, memory, concurrency, generalization and fidelity are descriptors
of each cell. They are not successive rungs. In particular, a timed press is
not inherently easier than an untimed five-operation manipulation.

| Scope | Entry and end boundary | What counts as completion |
|---|---|---|
| Atomic operation | A registered robot/instrument operation from a checked ready state | Independently measured physical or acquisition result |
| Subprotocol | A meaningful experimental unit, commonly 2–5 executed skills in a non-looping core | A reusable output state: a prepared aliquot, accepted endpoint, valid reading or completed processing cycle |
| Complete protocol | A named sample-to-result analytical/purification procedure | Preparation, execution, measurement, attributable numerical/product result, record and safe shutdown within the declared scope |

Batching is a separate axis: one sample, several serial samples, or overlapping
samples sharing resources. Ten serial samples are not automatically a harder
task than one time-critical sample. Overlap only becomes a scheduling test
when independently timed obligations actually compete for resources.

Keep two counts: registered skill executions and controller/archive stages.
Also report branch decisions, loop iterations, critical-path depth, maximum
concurrent obligations, sample count and process duration. A local dosing loop
may execute more than five skills; report its realized count rather than
renaming the entire loop an atomic action. Waits and file saves add no skills.
Repeated measurements count as acquisitions, not newly invented task types.

The old L1/L2, L3/L4 and L5/L6 pairs are convenient entry profiles over these
three scopes. They are not six different physical hierarchies. A source method
that already requires timing has no valid untimed version obtained by simply
removing that requirement. Such cells are marked not applicable.

## 2. Five laboratory questions about time

These are overlapping scientific roles of time, not five new mathematical
operators. Keep the ten existing operators as a serialization vocabulary.

| Question | What is being tested | Source-grounded examples | Common wrong interpretation |
|---|---|---|---|
| Is this sample/action still in its valid window? | Sample age, earliest valid read, latest valid completion | Method 8114 development/read window; a selected holding-time method | Episode age used for every sample; a late reading treated as fresh |
| Has the required process treatment been delivered? | Residence under specified conditions, ramp, cumulative exposure | BCA incubation; controlled melting-point ramp | Heater-on time treated as sample treatment; intermittent exposure treated as continuous dwell |
| Has a measured condition actually occurred and been confirmed? | State-dependent stop/continue, continuous endpoint confirmation, response delay | Indicator titration; phase resolution before drainage | A transient flash treated as the endpoint; an arbitrary reaction-time countdown substituted for observation |
| Was the time evolution measured correctly? | Event-time measurement, indexed acquisitions, actual timestamps | Iodine-clock onset; crystal-violet absorbance series | Recording an event confused with stopping a reaction; fabricated or backfilled samples |
| Can several valid processes be coordinated? | Per-sample timers, shared instruments, inter-sample spans | Staggered colourimetry; BCA batch acquisition span | One global timer; independently valid tubes but an invalid batch |

Some tasks only require sequence or state logic, without a numerical time
bound. Put those in the process model, not the timing count. Constant mass is
an example: successive completed heat/cool/weigh measurements are compared.
A balance staying stable for thirty seconds cannot establish constant mass.

Also distinguish **time as a constraint** from **time as a measured output**.
An iodine-clock trial asks for an unknown induction time. Making its physical
reaction last a requested number of seconds is a different task. Likewise,
kinetic sampling asks for a time series and derived result, not merely waiting
until a timer expires.

## 3. Four core protocol families, one later extension

Each family supplies nested subprotocols and one explicitly bounded full
experiment, with the same sample identities and compatible process model.
Related source methods are separate protocol variants, never casually merged.

| Family | Reusable operations/subprotocols | Complete experimental output | First implementation boundary |
|---|---|---|---|
| Endpoint-based quantitation | Incremental delivery, mixing, endpoint-candidate pause, confirmation, volume bookkeeping | Unknown concentration/content from measured delivered volume and the selected method | A calibrated acid-base indicator protocol; the current T7 button/colour task remains a proxy |
| Development-based quantitation | Sample/blank preparation, mixing, source-anchored timer, blank zero, acquisition | Sample-specific concentration plus a standard check and complete identity/timing record | Method 8114 at 23°C; DPD and BCA follow as separately validated variants |
| Thermal/gravimetric analysis | Tare, load/unload, condition-controlled treatment, desiccator cooling, weigh, compare, repeat | Method-specific loss-on-drying or gravimetric result with an attributable mass history | An oven-based moisture/loss-on-drying method; do not substitute an oven for sulfate-method ashing |
| Time-resolved kinetics | Blank/acquisition setup, reaction initiation, timestamped sampling, series analysis | Time series and estimated kinetic quantity with uncertainty/model checks | Crystal-violet acquisition protocol; iodine-clock onset is a useful component test |
| Separation/purification, later | Mix/vent/settle/drain or dissolve/filter/cool/isolate | Recovery and independently assessed purity or phase composition | Requires validated phase, filtration or crystallization dynamics; not a coloured-button substitute |

This is four proposed full-protocol families, not four completed experiments.
The existing thirteen themes remain a reference library. Recrystallization,
extraction and actinometry should not compete with the first executable
subprotocols simply to increase a catalogue count.

### 3.1 Endpoint-based quantitation

**Nested progression:** controlled delivery from a ready dispenser → one
delivery/mix/inspect unit → the repeated endpoint controller → sample preparation,
initial/final volume measurement, endpoint procedure, result calculation,
record and cleanup. Repeated trials are a separate reproducibility/batch setting.

The selected [UW indicator procedure](https://www2.chem.wisc.edu/deptfiles/genchem/lab/labdocs/modules/titrate/titrind.htm)
supports slowing near the endpoint and confirming a persistent final colour
for at least 30 seconds. It supplies neither a universal total-titration
deadline nor a generic permitted post-endpoint dosing delay.

Required distinctions: a local transient tint, an accepted persistent endpoint,
and overshoot. The candidate endpoint pauses further dosing; fading colour
can reopen the dosing branch. Actual delivered volume and sample contents
determine the analytical error, not a hidden target number of button presses.
The instruction states the method; it must not reveal the unknown endpoint volume.

**Diagnostic pairs:** vary analyte amount within the selected method's valid
range; compare brief tint versus persistent tint; compare equal current volume
with different measured initial volumes. Correct action or reported result
must differ for a reason available in public observations/history.

**Report:** endpoint/overshoot error, analytical error, unsupported early
confirmation, unnecessary extra delivery, confirmation duration and safe success.
Absolute RGB/colour and concentration tolerances require independent calibration
before qualification; source text alone does not supply them.

### 3.2 Development-based quantitation

**Nested progression:** insert a ready vial/acquire a reading → mix/start a
method timer → wait/zero/read one prepared sample → a full blank/standard-check/
unknown workflow → staggered unknowns sharing the same instrument.

[Hach 8114](https://cdn.hach.com/7FYZVWYB/as/9wp6b7c89p2jrbhnvw9n5fnn/Phosphorus_Reactive_Orthophosphate_Molybdovanadate_Method_8114_Test_N_Tube_Vials_DOC3165301116)
has a seven-minute reaction timer at 23°C, followed by a two-minute sample-read
window. Its standard-solution check supports checking the analytical chain.
For sample i, preserve the actual post-mixing instrument-timer event:

`t_start_i + 420 s <= t_read_i <= t_start_i + 540 s`.

Do not silently move this anchor to episode reset, container pickup or reagent
contact. A faithful process must also account for handling and mixing; excessive
delay before starting the instrument timer cannot reset physical sample age.
The procedure does not give a universal numerical bound for that delay. Record
both anchors and resolve validity through calibrated process behaviour or an
explicitly labelled engineering bound before native admission.

**Diagnostic pairs:** swap publicly observed start histories of otherwise
matched samples; keep the current global clock fixed. The correct ready/urgent
sample can change. First prove the intended current-observation ambiguity and
past-cue visibility; do not assume that two RGB frames match. Vary serial versus
overlapping preparation while preserving the chemical method.

Choose a small feasible batch, initially 1/2/4 samples as *design settings*, not
new chemical constants. A schedule feasibility check must include instrument
occupancy and measured robot/acquisition duration. If no policy can meet all
windows, score a separate infeasibility-detection setting rather than a normal
success trial. A policy must be free to stagger starts instead of being forced
to create artificial conflicts.

**Report:** early/late read counts, signed window violations, wrong-blank/sample
binding, concentration/standard-check error, valid-sample fraction and all-sample
success. A late measurement remains invalid even if its numerical answer happens
to be close. Unsupported sample deletion cannot improve the batch denominator.

DPD and BCA are useful transfer settings only after their own contracts exist.
[BCA's test-tube procedure](https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0011430_Pierce_BCA_Protein_Asy_UG.pdf)
uses 37°C/30-minute incubation, room-temperature equilibration and all-tube
readings within ten minutes of one another. This is not ten minutes per tube
from reagent addition. Bath versus sample temperature must remain distinct;
the source does not authorize inventing a new equilibration start convention.

### 3.3 Thermal/gravimetric analysis

**Nested progression:** door/load/read operations → one treatment/cool/weigh
cycle → compare two completed cycles and decide repeat/finish → sample/tare
preparation through method-specific numerical loss and record/shutdown.

Use a single selected oven-compatible method. The
[FAO moisture example](https://www.fao.org/4/v5380e/v5380e0a.htm) describes oven
drying, desiccator cooling, weighing and repeated processing to constant weight.
It is a comparative method description, not a ready-made calibrated simulator
or a source of a universal numerical constant-mass tolerance. Freeze a fully
specified method/criterion before native qualification; do not combine separate
timing descriptions from the page into an invented SOP.

Keep the older [CSUDH sulfate procedure](https://www2.csudh.edu/oliver/che230/labmanual/gravsulf.htm)
separate: it includes precipitation, filtration and ashing, and its successive
mass criterion is 0.2mg. Its furnace/flame and filter requirements cannot be
deleted because a ChemLab oven mesh is available.

**Diagnostic pairs:** identical current mass with different previous completed
cycle masses; both readings publicly observed at acquisition. One history
requires repetition while the other permits completion. Also distinguish a
stable but still-wet sample from a genuinely converged sequence, and a hot
weighing from one meeting the method's cooling condition.

**Report:** premature finish, unnecessary cycles, sample/tare mix-ups, temperature
and treatment compliance, complete mass history, and analytical result error.
Default-density instrument meshes and a scripted decreasing number are not
validation of drying kinetics, thermal inertia or balance resolution.

### 3.4 Time-resolved kinetics

**Nested progression:** ready-instrument acquisition → mixing/transfer/first
reading → valid indexed series → blank/calibration, selected-condition reaction
series, analysis, interpretable result, record and cleanup.

[Thermo's lesson](https://assets.thermofisher.com/TFS-Assets/CAD/Application-Notes/FL54678-genesys-kinetics-general-chemistry-lesson-plan.pdf)
starts the stopwatch at solution preparation, then transfers to the instrument.
After live measurement begins, it records every 30 seconds and retains actual
measurement times, with the observation ending five minutes after reaction
initiation. Preserve **two anchors**, reaction initiation and acquisition start.
Do not manufacture a t=0 sample before the instrument is ready. Sampling jitter
and acceptable initial data loss need a declared instrumentation contract.

**Diagnostic pairs:** similar final signal but different earlier trajectories;
different valid transfer latencies; dropped/late acquisitions. Use original
timestamps for analysis, never retrospectively relabel a delayed observation as
an on-time reading. Series/model fitting must use the observations actually made.

**Report:** initial acquisition delay, missing points, cadence errors, timestamp
accuracy, fitted-quantity error/uncertainty and model adequacy. High R-squared
alone cannot prove the correct kinetic model or rate parameter. Quantitative
reference data must be held out from policy inputs and independently validated;
agreement with the same unvalidated generator only demonstrates self-consistency.

## 4. The experiments must identify a capability

| Study | Matched comparison | What it can establish | What would invalidate the claim |
|---|---|---|---|
| Composition | Admitted subprotocols versus their full-protocol use; shared skills/process | Accumulated planning and handoff cost | Different controllers, thresholds or process models across conditions |
| Memory | Full public history, bounded recent history, and bounded history plus self-written ledger | Need to retain measured identities/values/timer origins | Correct answer still visible in the current observation; hidden cue never observable |
| Timing | Cue/timer-aware controller versus declared fixed policy on the same valid instances | Whether timing/state adaptation is useful | Changing required chemistry to manufacture an untimed success; randomizing unsupported reaction times |
| Scheduling | Same valid method with serial and overlapping samples/resource occupancy | Coordination of competing commitments | Infeasible batches mixed into ordinary success; future bookings leaked as answers |
| Closed-loop recovery | Same predeclared perturbation and recoverable sample state, with/without recovery | Ability to repair without invalidating the sample | Resetting sample age, inventing a new sample, or granting extra time after failure |
| Generalization | Held-out object, method binding, process condition, and composition tests reported separately | Which transfer actually occurs | Calling new lighting a new chemical task or tuning on held-out outcomes |

State-feedback and timing are not the same ablation. Compare timer-only,
current-state-only, and state-plus-history controllers where each is meaningful.
Do not require every source method to defeat a fixed wait: a prescribed fixed
wait can be the scientifically correct solution. A fixed-policy success ceiling
must be derived for that diagnostic's distribution, not imported from T4-v2.

Memory descriptors are (a) sample/object/method bindings, (b) historical
measurements and differences, (c) prospective commitments such as active timers,
and (d) retained procedural facts when the observation contract really removes
them. Describe retention, interference and external storage access explicitly.
Do not hide all timestamps and then mistake an unobservable task for memory.

For a history-dependence claim, construct paired histories with the same current
allowed observation but different correct decisions/results. Show that the
distinguishing fact was previously observable and that static labels, RGB,
metadata and skill responses do not leak the answer. Metadata renaming must
leave the independent verdict unchanged.

Freeze new development/qualification/held-out splits by **protocol instance**,
including identities, process parameters, start schedules and perturbations.
Do not split adjacent video frames from one trial across train/test. Keep all
existing v0.1 held-out seeds untouched. Fit thresholds and calibrations on
independent qualification material before any new held-out model experiments.

Each comparison uses the same sampled instances and perturbation streams, not
independent easy/hard seed sets. Report paired differences and uncertainty;
individual-success Wilson intervals alone do not estimate a paired difference.
Resample at the independent protocol/batch unit, not at the frame or correlated
sample level. Define primary comparisons and multiplicity handling before testing.

## 5. A complete result, not only a successful animation

For environment state `s=(robot/objects, per-sample process state, resources)`,
the public observation is `o=O(s, public instructions)`. Policy history/ledger
is separate. Benchmark-owned sensors/events, not policy phase labels, establish
the protocol predicates and temporal relations. A result has explicit sample,
method, units, raw measurements, transformation/calibration and uncertainty.

Strict success is the conjunction of physical completion, process validity,
temporal validity, safety and an acceptable result. An instrument or result
quality gate that is not yet defined and validated makes that new task **not
admitted to its claimed evaluation track**; omit no gate simply to report a
success. Fidelity is independent of scope: a complete virtual protocol can be
an engineering benchmark with a declared model and independently checked
analytical reference, without being calibrated chemistry. Label its result
model-consistent; do not report it as experimental chemical accuracy. Reference
data/analytical solutions can validate a model within a stated domain; a real
calibration claim additionally needs appropriate empirical evidence. Comparing
two outputs from the same unchecked generator is insufficient for either claim.
The four selected core families are quantitative. A future qualitative protocol
must instead define its appropriate scientific outcome; do not invent a
concentration requirement for every possible chemistry experiment.

Report the components alongside strict success: physical, process/time,
identity/memory, scientific result and safety. Keep missing events, missing
readings, early/late signed errors, infrastructure errors and failure causes.
All attempted instances remain in the denominator. Conditional timing accuracy
on physically successful runs can diagnose a failure, but never replaces
unconditional success. Macro-average by declared family/scope rather than by
however many similar variants were generated.

Stage archives include physical state, sample contents/age, temperature/process
state, active constraints, acquired measurements, sample bindings, occupied
resources and random-generator state. Policy context/ledger is a separate
artifact with declared retention. Archive consistency, same-process continuation
and new-process restoration are three distinct claims. Current T2 supports the
first two within its existing physical task; arbitrary cold restoration remains
unsolved and is not re-opened by this design.

## 6. Qualification and the next executable slice

1. **Contract qualification on CPU:** explicit anchor/units/provenance; positive,
   early, late, missing, repeated, wrong-sample and wrong-order traces. In endpoint
   confirmation, a false interval resets the dwell; in gravimetry it is successive
   cycles, not dwell. Reject contradictory/infeasible contracts.
2. **Process qualification:** check volumes, mixing/signal evolution, temperature
   response and measurement noise against an independently checked reference
   appropriate to the stated fidelity. An analytical engineering model and
   empirical chemical calibration are different tracks; retain applicability
   limits and never promote one into the other.
3. **Observation qualification:** demonstrate that public RGB/readbacks expose
   each required cue with usable timing. Paired observation/leakage tests are
   necessary for claims of memory dependence.
4. **Robot qualification:** assets function as named; full-arm/all-scene paths
   and force/safety checks; real executed acquisition/control events. A pretty
   instrument or a passive door joint is not an admitted analytical instrument.
5. **Protocol qualification:** full identity/material/timer/result chain and a
   public-observation controller can complete the protocol. Only then freeze
   new held-out model comparisons; no benchmark LLM/VLM calls are added here.

The first implementation slice comprises endpoint continuous confirmation and
the 23°C phosphate acquisition window, with both physical-age and method-timer
anchors declared. Their current qualification is recorded below. The moisture cycle follows the
balance/oven chain, and kinetics reuses an actually qualified photometer rather
than relabelling a turbidity meter. Four full protocols are the design target,
not the immediate GPU queue.

ChemLab assets enter through actual function: a qualified oven door/loading
chain for treatment, a balance for measurement, and an appropriate photometer
for optical results. All current ten passive admissions remain passive; none
is promoted by this document. Keep CC BY-NC attribution. No extra card is
reserved until an executable, independently verifiable workload is ready.

### 6.1 Status of the two first units (2026-10-26)

Both units have passed contract qualification on CPU and robot qualification on
the native A-Lab twin. They are two additional engineering subprotocols alongside
the frozen seven-task v0.1 release scope. Neither has a
calibrated process or a held-out model comparison.

| Unit | Module | Source parameters | Public CPU controller | History-free / method-free controls |
|---|---|---|---|---|
| Titration endpoint confirmation | `chemrm.bench.process.titration` | 30 s persistence (UW) | 100% of 200 seeds | declare at first colour 0%; coarse until persistent 20.5%; fixed fine count 19.5% |
| Development read window | `chemrm.bench.process.development` | 420 s timer, 120 s window (Hach 8114), process clock × 0.2 | 100% for 1, 2 and 4 samples (150 seeds each) | read immediately 0%; episode anchor 0%; no blank zero 0%; identity memory loss 46% (2 samples), 4.7% (4 samples) |

The titration proxy keeps a transient tint and the persistent endpoint identical at any
instant; only the observed history separates them. The development unit compresses the
process clock only; robot and safety clocks retain their original time scale.
The native two-sample development unit uses measured key contacts and vial poses;
it has not validated reagent chemistry or public RGB control. The native titration scene
reuses the qualified T7 stirrer keys (coarse = key 1, fine = key 2, declare = key 3).

Titration robot qualification (`titration_endpoint`, host ubuntu-TRX50-AI-TOP, Isaac Sim
5.0). The verifier re-derives every dose and the declaration from key contact impulses,
replays the CPU referee and checks receiver contrast and safety; every collection passed
offline recording acceptance.

| Cohort | Seeds | Successes |
|---|---|---|
| Qualification (r4) | 5000–5002 | 3/3 |
| Planned-path expert | 0–19 | 20/20 |
| Matched no-persistence ablation (declare at first colour) | 0–9 | 0/10 |

The analytic fixed-strategy bound for this unit is one fixed delivered volume:
p_max = 0.2 mL / (8 − 4) mL = 0.05, so 0/10 is inside the predeclared ten-trial rule.
The ablation pairs seed-for-seed with the expert (same hidden V_eq, criteria,
instruction and task revision); peak raw contact force stayed at 12.3 N.

Development robot qualification (`development_read`, same local host). The
instrument is a declared derived DR6000 engineering fixture, with compliant keys.
The verifier reconstructs ZERO, MIX/START and READ from measured contacts and
vial poses, then runs the same independent sample referee.

| Cohort | Seeds | Successes |
|---|---|---|
| Qualification (r7) | 5000–5002 | 3/3 |
| Expert | 0–19 | 20/20 |
| Matched read-on-load ablation | 0–9 | 0/10 |

All 30 main/ablation recordings passed offline verdict replay, full two-camera
video decode and input-boundary checks. All ten pairs have identical sampled
parameters, instructions, revisions and criteria. Every main read occurs at
91.475 seconds in the scaled [84,108]-second window; ablation reads occur at
28.683–28.842 seconds and fail as early. Maximum raw force is 4.574N. Mean
episode wall time is 1716.9 seconds for the main expert and 1449.7 for ablation.
The complete cohorts and three qualification seeds have size-checked NAS copies.

The ablation's expected success probability zero applies **only to reading on
load**, not to an optimal fixed-wait policy. A prescribed fixed 90-second wait
is a valid solution for an isolated sample. The 35% fixed-policy design ceiling
is inapplicable to this method-bound control. This contrast establishes that
early reads are rejected; it does not establish native visual memory or
chemical accuracy. The earlier nominal 28.8-second estimate is rounded; the
observed maximum is 28.842 seconds, still below the 84-second opening.

The next frozen baseline step is T7 action evaluation from predeclared training
seed 42 on held-out seeds 1000–1049. New process-unit public-observation/model
evaluations require their own declared protocol; no held-out comparison or
complete calibrated chemical experiment is claimed by these expert batches.
