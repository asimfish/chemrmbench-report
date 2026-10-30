# Complete development workflow: explicit CPU contract

This is an engineering specification with executable logical tests. It is not
a newly qualified native task or a chemistry-calibrated experiment.

The selected source is [Hach Method8114](https://cdn.hach.com/7FYZVWYB/as/9wp6b7c89p2jrbhnvw9n5fnn/Phosphorus_Reactive_Orthophosphate_Molybdovanadate_Method_8114_Test_N_Tube_Vials_DOC3165301116),
procedure steps1–12: program540;5.0mL water for a reagent blank and5.0mL sample
for a second reagent vial; cap and invert; a7min timer at23C followed by a2min
measurement window; clean and insert the blank, zero, then clean and read the
sample. The source's standard-solution check is also represented as a separate
reference sample. Inversion count and duration are not specified by this source.

The contract's standard value2.0 and unknown range0.5–5.0 are arbitrary proxy
units inherited from the engineering process model. They are not the method's
mg/L calibration or its specified standard solution. The engineering volume
tolerance is0.05mL; event/record serialization tolerance is1e-6. No new chemical
accuracy claim follows from passing these checks.

Scope begins with identified room-temperature source water and preloaded
reagent vials. Upstream field sampling, filtration and reagent manufacture are
outside it. It includes physical transfer, sealing/mixing, method timing,
instrument occupancy and zero, result identity and numerical binding, and
sealed reacted-vial storage with the instrument idle. Storage is a simulated
safe-closure target, not chemical disposal approval or an EHS qualification.

| Block | Required evidence | Current native status |
|---|---|---|
| Prepare | measured source, vial, aliquot volume; seal; completed inversion | missing adapter |
| Develop | each physical vial's mix and timer timestamps | qualified in ready-vial unit only |
| Measure | cleaned vial, cell occupancy, blank zero, sensor reading | partial: cell/keys qualified; cleaning missing |
| Record | reading ID → physical vial → label and unchanged numerical value | CPU contract |
| Close | all reacted vials sealed in storage; empty cell; instrument idle | CPU contract |

The complete CPU model uses the source timer without compression. Semantic
operations and archive stages are counted separately. All14 operation kinds
must be represented, but the event count depends on the sample batch. A
logical checkpoint can be JSON-serialized and resumed by replaying measured
events; this is separate from native physical restoration.

Run development witnesses and negative controls (no GPU, seeds0–99 only):

```bash
python -m chemrm.bench.process.full_development_sim --out /persistent/path/new-contract-run --count 100
```

The report distinguishes a successful reference witness from rejection of
wrong identity, missing zero and unfinished closure. These are software
contract results, not expert or learned-policy benchmark success rates.
