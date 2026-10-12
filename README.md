# ChemRMBench — Paper A research progress

Public report: **https://asimfish.github.io/chemrmbench-report/**

Live reproduction dashboard: **https://asimfish.github.io/chemrmbench-report/reproduction.html**

The new dashboard tracks MATTERIX and Auto-Engineering simulation reproduction. It exposes 13 reference capability gates, scoped development and confirmation results, the original failed/inconclusive budget, active native progress, and the proposed verified-experience research system. Chinese is the default; use `reproduction.html?lang=en` for English. The original report below remains a dated snapshot.

An installed local publisher resamples the explicit public allowlist every 10 minutes. The page polls every minute and marks exports older than 25 minutes stale. It shows experiment and export timestamps separately. Publication validates field/path restrictions and evidence boundaries, refuses protected branches, unrelated local changes or divergent remote history, and only commits reviewed public JSON paths. It never exports raw logs, credentials, simulator meshes or private source manifests. `python3 check_reproduction.py` checks the public artifact contract. SHA-256 values identify private underlying evidence; the dashboard is not a standalone reproduction capsule.

This repository hosts a bilingual, buildless research report: benchmark design, an explicitly illustrative mechanism, actual development figures and a failed diagnostic replay, and the scientific acceptance roadmap. English is the default; `?lang=zh&view=method` selects a language and section.

## Evidence and scope

- The report is a versioned snapshot, not live telemetry.
- Development native runs, CPU checks and formal scientific experiments have separate denominators.
- Failed trials, open gates and unrun experiments retain their status. A limited engineering pass is not benchmark or conference acceptance.
- The qualified 700-demonstration dataset and 15 matched native VLA fits are not yet complete. Current development diagnostics are excluded from these counts.
- Region particle counts are not calibrated liquid volume, and diagnostic markers are not benchmark cues.
- The V37-R3 video is a lossy presentation derivative: all 70 saved RGB captures replayed at 10 fps, without added cue markers or annotations. It is a failed development diagnostic, not a formal M1 benchmark result or raw sensor archive.
- The full unpublished manuscript, private raw data, credentials, filesystem paths and licensed simulator assets are not part of this public subset.
- SHA-256 digests identify underlying research artifacts. This subset is not a standalone reproduction capsule.

## Site

Serve the directory with any static HTTP server. No install, build, tracking scripts, external font service or server backend is required. `index.html`, `styles.css` and `app.js` render the report; `data/progress.json` supplies dated evidence. Owned SVG figures are in `assets/`. GitHub Pages publishes the `main` branch root, with `.nojekyll`.

Update snapshots only from checked research evidence. The private research checkout contains an allowlisted exporter; do not copy private research manifests wholesale into this repository. Publication records should bind the source commit and public response, with credential values excluded.

## Presentation references

The reading structure is inspired by the user-selected [anonymous report](https://anonymous-report-421.github.io/public-website/?lang=en&view=), [RoboDojo report](https://robodojo-benchmark.com/report/gpt-6-astra-eval), and [Awesome Astra Embodied AI](https://github.com/zjwzcx/Awesome-Astra-Embodied-AI). Report text, interactive diagram and figures here are authored for ChemRMBench; no reference media or results are copied.
