# Gravimetry native feasibility (read-only, 2026-11-06)

This is a CPU/read-only feasibility note. It does not start Isaac, change a
scene, or admit a native task. The source evidence is the retained P12
SAGE-Mat/OpenLab delivery under
`/home/liyufeng/scholarship_ppt_sync_20261025/sagemat_p12_video/`, especially
`v3_work/C_balance/plan.json`, the `C_balance` pose/readback captures, and
`A_terminal_verification_contract.json`. That delivery explicitly describes
kinematic replay and rendering, not a new chemistry or instrument-success
claim; its furnace and balance objects therefore remain engineering assets.

## Objects and roles

The Station B plan contains `furnace_1`–`furnace_4`, `crucible_rack_1/2`,
`crucible_1`–`crucible_4`, `transfer_rack`, and a crucible-tong asset. The
furnaces have a named `Door_joint` with a declared 0–100° range and a 1.5 rad
open target in the plan. The crucible USD is a small rigid asset (the direct
CPU USD inspection measured an approximately 70 mm × 70 mm × 73 mm authored
bound); the transfer rack has an authored approximately 219 mm × 75 mm × 73 mm
bound. Furnace, rack and dosing-balance direct layers contain referenced
payloads, so their direct layer traversal returned no mesh bound. The plan's
measured placement and support fields remain the authoritative geometry source
until those payloads are expanded in a dedicated certificate run.

The available objects can serve the following engineering roles:

| Object | Direct role | What is still unproved |
|---|---|---|
| `furnace_1–4` | heat receptacle; door state | temperature field, heat transfer, physical treatment duration |
| `crucible_1–4` | sample identity and grasp target | stable tong/gripper grasp over the complete route |
| `crucible_rack_1/2` | load/unload receptacle | every slot's contact and release clearance |
| `transfer_rack` | cooling/desiccator proxy | actual desiccator environment and room-temperature sensor |
| `dosing_balance` / `balance` | pose target and readout fixture | mass readback calibration and weighing event adapter |
| `carousel_crucible_0–5` | optional source rack | slot-specific contract and full-arm certificate |

The P12 material shows furnace-door and crucible-rack trajectories and an A
station bottle-to-balance trajectory. It does not establish the gravimetry
chain `load → heat → unload → cool → weigh → repeat`, nor does it provide a
mass signal. We therefore reuse the assets as scene geometry only.

## Required measured events

The native verifier should derive events from state and contacts, never from an
expert phase label:

1. `load_furnace`: crucible identity is in the selected furnace receptacle and
   the door is closed/latched by measured joint state.
2. `unload`: the crucible leaves the furnace, and the measured door state and
   crucible pose establish the operation completion.
3. `desiccator_in` / `desiccator_out`: the crucible enters/leaves the cooling
   rack; out is accepted only after the measured cooling-ready signal (initially
   a declared engineering temperature proxy).
4. `weigh`: the crucible is seated on the balance, is stationary for the
   declared stability interval, and the balance adapter emits a numerical
   reading bound to the same crucible identity.
5. `declare_constant_mass`: two consecutive measured readings differ by no more
   than 0.2 mg. The previous reading and crucible identity are mandatory memory.

The furnace door joint and crucible/rack poses are feasible event sources. A
balance display/readback and cooling-state sensor are missing adapters. A
fixed dwell, a still frame, or an expert `phase=weigh` string cannot substitute
for either signal.

## Clearance and adapter gates

The benchmark-wide strict gate remains full-arm, all-scene clearance ≥10 mm,
with the existing 1 mm tracking margin. The P12 read-only captures include
pose checks and clearance views for selected historical trajectories, but they
are replay/render evidence rather than a new gravimetry full-arm certificate.
Before native admission, a CPU certificate must expand all referenced furnace,
rack, balance and crucible payloads and check every FR3 link on the complete
route: rack → furnace, furnace → transfer rack, transfer rack → balance, and
return. Any path below 10 mm is rejected before Isaac starts.

Missing adapters are: (a) a validated crucible-tong grasp and release
primitive, (b) furnace-door interaction/latched-state readback, (c) cooling
readiness/temperature proxy, (d) balance stability and numerical readback, and
(e) a measured sample-mass process model. None should be hidden inside a
trajectory phase label.

## First native unit proposal

The smallest useful native unit is **one crucible, two completed cycles**:

```text
load furnace → measured treatment interval → unload
→ transfer to cooling rack → measured cooling window → weigh
→ repeat load/treatment/unload/cool/weigh
→ compare the two readings → return crucible and leave instrument idle
```

Use the existing P12 furnace/rack/crucible geometry and the Station A balance
fixture, but keep the output as `engineering_proxy` until the balance and
cooling adapters are independently qualified. The process clock may use the
explicit gravimetry `time_scale`; robot and safety clocks remain unscaled.
Admission requires three CPU full-arm certificates, then three native seeds,
with raw force ≤25 N, no penetration >1 mm, complete measured events and
offline/video acceptance. A successful first unit would still be a
heat–cool–weigh process unit, not a calibrated chemical experiment.

The CPU contract and its100-case witness/negative-control evidence live in
`chemrm/bench/process/gravimetry.py`, `gravimetry_sim.py` and
`tests/bench/test_gravimetry.py`. Native robot qualification remains pending.
