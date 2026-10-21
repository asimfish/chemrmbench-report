# ChemRMBench v0.1 data card

Status: native collection and baseline evaluation in progress. Do not describe
the candidate as a completed benchmark or a calibrated chemistry simulator.
The release scope is seven tasks in one reconstructed A-Lab scene with FR3 at
station A. T3/T7 are engineering analogues, not chemical-reaction fidelity tests.

Each collection has `collection.json`, all-attempt `manifest.jsonl` and recording
acceptance. Each episode has `task.json`, `run.json`, `verdict.json` and media
metadata. `obs/` contains public instructions, proprioception, actions and
station-A/wrist videos (640x400,20fps). T8 also retains lossless RGB for cue and
counterfactual checks. `privileged/` contains sampled hidden parameters, events,
state archives, contact records and stage snapshots. Complete task metadata
and root directories are not policy inputs.

Public HDF5 exports use only obs/ plus recorded actions; failed/error/excluded
attempts remain in the export manifest. Formal training requires exactly100
development attempts and at least80 accepted successful public demonstrations.
The DP input is two RGB cameras plus18D proprioception, output nine joint
targets. Export tests reject privileged fields and held-out seeds.

Primary experts, lower bounds and evaluations run on one local runtime.
Some early local cohorts predate per-episode runtime_host labels; their host
field remains unknown, with counts reported separately. Their retained local
collection provenance is not replaced by an invented host name.
Training expansion also uses the functionally admitted remote RTX runtime;
record runtime_host for every episode and publish counts by runtime class.
V2 strict cross-machine force equivalence did not pass: paired differences
11.4%/17.2% at about4N exceeded10%. Remote episodes are training-only, each
independently checked against its own25N threshold. They are not merged into
the primary results table. Do not claim hardware-deterministic dynamics.

All successes, failures, launch errors and renderer timeouts remain retained.
SSD staging is not formal NAS admission: size verification and offline replay
must finish before data enter a formal manifest. Unknown durations remain
unknown. Near-clearance legacy paths (7.6–9.7mm) use record-only geometry
diagnostics; new/changed paths require the strict10mm screen. Raw contact peaks
are impulse/dt measurements, not glass stress or calibrated human safety.
T2's historical force metric covers robot/bottle contact; legacy grading also
required expert stages. Its candidate measured-v1 replacement uses raw robot
contact peaks, measured transport/subgoals and a90s horizon. All seven tasks
undergo development-only old/new and controller-metadata invariance audits.
Old verdicts remain available; discrepancies require review. Other tasks retain
their recorded force scope. No averaging redefines25N.

Assets are external. SafeLab provides beaker, vessel and stirrer CAD plus task
and metric conventions; preserve its asset-specific licenses. A-Lab scene
provenance is in `native_scene/ORIGIN.json`. Supplemental
[ChemLab-Assets](https://github.com/mbzuai-nlp/ChemLab-Assets) by MBZUAI NLP has
CC BY-NC4.0 assets (attribution and non-commercial restriction), MIT code.
The [dataset source](https://huggingface.co/datasets/MBZUAI/ChemLab-Assets)
and registry provenance must accompany any redistributed derivative. These
assets are separate from SafeLab and are not needed for the v0.1 seven-task
matrix. Novel-object evaluation is deferred to v0.1.1. Estimated masses and
units are not physical calibration.

Downloads: the public website supplies representative MP4s and aggregate JSON.
The complete native/HDF5 archives are currently on project storage and have no
public dataset URL yet. Do not publish internal machine addresses or credentials
as download instructions. A release archive must include manifests, status
counts, host-class counts, this card and license notices, with a confirmed
download location. Reconstruct assets from their original sources; do not
bundle restricted CAD indiscriminately. The minimal reproduction commands are
in [release_v0_1.md](release_v0_1.md).

Dataset hosting is awaiting the user’s choice. The data card remains candidate
and a release tag, when eligible, must remain local until that choice.
