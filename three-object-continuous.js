"use strict";
(() => {
  const node = document.getElementById("three-object-live");
  fetch("data/full-reference-progress.json", {cache: "no-store"})
    .then(response => { if (!response.ok) throw new Error("snapshot unavailable"); return response.json(); })
    .then(data => {
      const row = data.modules.find(item => item.id === "ot2-continuous-noasp-r9-restart1");
      if (!row) throw new Error("control record missing");
      const pair = data.modules.find(item => item.id === "ot2-three-object-continuous-pair-accepted");
      const stamp = new Date(data.exported_at_utc);
      const stale = !Number.isFinite(stamp.getTime()) || Date.now() - stamp.getTime() > 25 * 60 * 1000;
      const title = document.createElement("strong"); title.textContent = "No-aspiration control · continuous three-object task";
      const progress = document.createElement("p");
      progress.textContent = `${row.metrics.native_steps.toLocaleString()} recorded steps · ${row.metrics.native_seconds.toFixed(1)} trial-relative seconds · ${row.metrics.completed_objects} objects placed.`;
      const verdict = document.createElement("p");
      verdict.textContent = pair && pair.subsystem_passed ? "The independent pair audit passes its stated local scope; full reference reproduction remains open." : "Independent pair acceptance is not established in this published snapshot.";
      const time = document.createElement("p"); time.className = stale ? "muted stale" : "muted";
      time.textContent = `${stale ? "STALE SNAPSHOT · " : "Snapshot · "}${data.exported_at_utc}`;
      node.replaceChildren(title, progress, verdict, time);
    }).catch(() => { node.textContent = "The live control snapshot is unavailable. Use the full evidence index; the positive result does not imply pair acceptance."; });
})();
