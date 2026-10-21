# ChemRMBench v0.1 release contract

Status: **candidate, not released**. Guidance11 fixes seven active tasks:
T1 pick_place, T2 bottle_balance, T3 pour, T4-v2 press, T5 open_cabinet,
T7 endpoint_stop and T8 delayed_cue_memory. T6 is deferred, with all failures
and videos retained. ChemLab novel-object evaluation moves to v0.1.1.

Release requires all of the following evidence, not just runnable code:

1. Each active task has20 development attempts with recording acceptance and
   expert success>=80%, retaining every failure/error.
2. Each of T3/T4-v2/T7/T8 has10 matched fixed-response attempts and passes the
   analytical demand bound and one-sided binomial check.
3. Each of these four M/T tasks has all50 fixed public-observation cases.
4. T1/T2/T5 each has formal100-attempt training provenance, >=80 successful
   public demonstrations, <=6 single-card GPU hours and50 native action cases.
   Their combined formal training cap is18 GPU hours; global cap remains64.
5. The main table has every denominator,95% Wilson interval, timing/memory
   coverage and explicit missing entries. Expert20 and evaluated50 are different
   cohorts and do not establish paired policy effects.
6. Seven task cards, an evaluation protocol, data card and version history exist.
7. Only after the evidence gate passes, tag the reviewed branch
   `chemrmbench-v0.1`. Do not mint the tag for a partial candidate.
8. The website presents the table, seven playable representative videos and
   download instructions. Raw data availability must be described accurately.

The CPU evidence builder reads explicit cohort paths from a local source map:

```bash
python -m chemrm.bench.release --sources /persistent/release_sources.json \
  --out /persistent/release_v0_1
```

It writes `public_main_table.json` and `main_table.md`, keeps missing scores
null, rejects duplicate seeds and T4-v1 evidence, and reports incomplete gates.
The source map uses expert/ablation/public_heuristic/dp dictionaries mapping
task IDs to lists of cohort directories, training_runs mapping basic task IDs
to training directories, plus budget_ledger and website_receipt paths. It is
an internal routing file, never a policy observation or public artifact.

Minimal native reproduction, from the repository root:

```bash
python -m chemrm.bench.collect --task pick_place --backend isaac \
  --episodes 1 --seed0 0 --gpu 0 --out /persistent/new_episode
python -m chemrm.bench.eval.native_run --task press --episodes 1 \
  --seed0 1000 --gpu 0 --policy privileged_expert \
  --out /persistent/new_eval_seed
```

Use a fresh output directory. The second command is a privileged reference,
not public-observation evidence. Public heuristic evaluation additionally needs
the frozen development-only `--public-calibration` file. Evaluation seeds must
never be collected through the development CLI.

Environment: Isaac Sim5.1.0, Isaac Lab0.54.2, Linux RTX runtime, A-Lab twin and
station-A FR3. Native launch wraps InteractiveScene; SafeLab RLEnv/cuRobo are not
required. Configure the external asset roots described by
`native_scene/ORIGIN.json`; the local launcher maps the preserved asset root
to authored USD paths with bwrap. Match CUDA/NVML/PTX user libraries to the
loaded kernel driver. On the recorded local570 runtime, the existing persistent
driver capsule is required. A different host with matching system libraries
does not need that capsule. Do not change system drivers to reproduce a run.

Same-process stage saves include the full registered rigid/articulation state.
Ordinary cold reconstruction remains1/8 and is not a v0.1 capability claim.

Validation: `python -m pytest tests/bench -q`; recording replay and video decode:
`python -m chemrm.bench.validate --out /persistent/new_episode`.
