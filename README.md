# ChemRMBench — Paper A research progress

Public report: **https://asimfish.github.io/chemrmbench-report/**

Continuously updated task dashboard: **https://asimfish.github.io/chemrmbench-report/collection.html**

The task dashboard shows registered development collection, committed stages, three distinct timing anchors, actual replay, open scientific gates, resource use and the next experiments. The browser checks every minute; a local collector samples every minute and a publisher pushes a reviewed public snapshot every ten minutes. Pages builds and caching add delay. Research evidence, telemetry sampling and publication have separate timestamps; regular refresh does not imply a new experiment.

Live reproduction dashboard: **https://asimfish.github.io/chemrmbench-report/reproduction.html**

The new dashboard tracks MATTERIX and Auto-Engineering simulation reproduction. It exposes 13 reference capability gates, scoped development and confirmation results, the original failed/inconclusive budget, active native progress, and the proposed verified-experience research system. Chinese is the default; use `reproduction.html?lang=en` for English. The original report below remains a dated snapshot.

An installed local publisher resamples the explicit public allowlist every 10 minutes. The page polls every minute and marks exports older than 25 minutes stale. It shows experiment and export timestamps separately. Publication validates field/path restrictions and evidence boundaries, refuses protected branches, unrelated local changes or divergent remote history, and only commits reviewed public JSON paths. It never exports raw logs, credentials, simulator meshes or private source manifests. `python3 check_reproduction.py` checks the public artifact contract. SHA-256 values identify private underlying evidence; the dashboard is not a standalone reproduction capsule.

This repository hosts a bilingual, buildless research report: benchmark design, an explicitly illustrative mechanism, actual development figures and a failed diagnostic replay, and the scientific acceptance roadmap. English is the default; `?lang=zh&view=method` selects a language and section.

## Evidence and scope

- The main report is versioned research evidence; the task dashboard adds timestamped progress snapshots and shared local GPU telemetry.
- Development native runs, CPU checks and formal scientific experiments have separate denominators.
- Failed trials, open gates and unrun experiments retain their status. A limited engineering pass is not benchmark or conference acceptance.
- The qualified 700-demonstration dataset and 15 matched native VLA fits are not yet complete. Current development diagnostics are excluded from these counts.
- Region particle counts are not calibrated liquid volume, and diagnostic markers are not benchmark cues.
- The V37-R3 video is a lossy presentation derivative: all 70 saved RGB captures replayed at 10 fps, without added cue markers or annotations. It is a failed development diagnostic, not a formal M1 benchmark result or raw sensor archive.
- The full unpublished manuscript, private raw data, credentials, filesystem paths and licensed simulator assets are not part of this public subset.
- SHA-256 digests identify underlying research artifacts. This subset is not a standalone reproduction capsule.
- V75 is one seen 37 s development motor-proxy episode, with one actual Astra image request and eight saved time bins. It is not eight episodes, chemical A/B validation, five-way task recognition or M1 memory evidence. The second cycle sent 69/70 targets; real A-to-B motor error fails ±100 ms, and 123 final cup-exterior proxy points remain. Formal and training gates remain blocked.
- The V75 video includes all 163 saved images using their relative capture times. Encoding quantizes timestamps (37.04 s presentation of an approximately 37 s record); it is a lossy display derivative, never the clock used for timing acceptance. The actual model-input image is the poster. No artificial chemical cue is added.

## Site

Serve the directory with any static HTTP server. No install, build, tracking scripts, external font service or server backend is required. `index.html`, `styles.css` and `app.js` render the report; `data/progress.json` supplies dated evidence. Owned SVG figures are in `assets/`. GitHub Pages publishes the `main` branch root, with `.nojekyll`.

Update snapshots only from checked research evidence. The private research checkout contains an allowlisted exporter; do not copy private research manifests wholesale into this repository. Publication records should bind the source commit and public response, with credential values excluded.

## Collector and publisher

`scripts/export_dashboard.py --config PRIVATE_CONFIG` reads an explicitly pinned, sealed development completion receipt and registered development stage directories. It checks receipt/package/audit identities, stage commit markers and schema limits. Only fixed public labels, selected numbers, digests and read-only GPU telemetry leave the private source. Live hidden event times, seeds, commands, prompts, PIDs and paths are omitted. It performs no training, model requests, SSH or simulator work.

The private JSON config is kept **outside this public checkout**. Its fields are `experiment_root`, `pilot_root`, `closed_receipt` (`id`, `path`, `sha256`), `live_runs` (explicit `id`/`path` registrations), `gpu_environment` (optional driver-library overrides), `snapshot_path`, `publication_receipt_path`, `site_root`, `github_repository` and `pages_branch`. Register a new development run before starting collection. Closed scientific results need review before replacing the pinned completion receipt; this development-only exporter cannot grant formal admission. Its evidence adapter currently supports the V75 receipt layout, not arbitrary future experiments.

`scripts/publish_dashboard.py --config PRIVATE_CONFIG` accepts a snapshot no older than three minutes, requires a clean checkout on the configured Pages branch and rechecks the exact remote and branch protection through GitHub. It fetches and integrates only by fast-forward, stages only `data/collection.json`, commits and pushes without force. Credentials come from the existing Git helper and are never written to the website, config or command line. Dirty/diverged/protected branches and stale snapshots stop publication. A failed push can be retried from the clean local commit; staged or unrelated edits need operator review.

The operator uses separate user systemd timers: collector every minute, publisher every ten minutes. Services have a bounded runtime, process locks and private receipts. If telemetry is unavailable, the page reports unavailable data rather than idle GPUs. If evidence export fails, the previous snapshot stays visible and its age makes the stale state explicit. User services require the host and registered evidence storage to remain available; they do not run experiments autonomously.

Verify with Python 3.10+ and Node: `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q scripts tests`, `node --check collection.js`, and `git diff --check`. Tests cover denied public fields, development admission, parser ambiguity, path escape, partial stage commits, stale snapshots, dirty checkouts and telemetry failure. The task page also needs a desktop/mobile browser check before publication. To suspend publishing, stop the operator's publish timer; published research remains online. Revert an owned website commit normally to roll back a presentation change; preserve the research evidence.

## Presentation references

The reading structure is inspired by the user-selected [anonymous report](https://anonymous-report-421.github.io/public-website/?lang=en&view=), [RoboDojo report](https://robodojo-benchmark.com/report/gpt-6-astra-eval), and [Awesome Astra Embodied AI](https://github.com/zjwzcx/Awesome-Astra-Embodied-AI). Report text, interactive diagram and figures here are authored for ChemRMBench; no reference media or results are copied.

The task dashboard structure is also inspired by [SafeLab PickPlace](https://asimfish.github.io/psibot-dashboard/pick_place.html). Its code, data, results and media are not reused.
