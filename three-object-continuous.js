"use strict";
(() => {
  const node = document.getElementById("three-object-live");
  const videoNode = document.getElementById("three-object-video-live");
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
      const video = data.modules.find(item => item.id === "ot2-three-object-video-r8-chunked");
      if (videoNode && video) {
        const heading = document.createElement("strong"); heading.textContent = "Complete video · recorded chunk progress";
        const count = document.createElement("p");
        count.textContent = `${video.metrics.frames_completed.toLocaleString()} / ${video.metrics.frames_total.toLocaleString()} frames archived · ${video.metrics.chunks_completed} / ${video.metrics.chunks_total} chunks completed.`;
        const detail = document.createElement("p"); detail.className = "muted"; detail.style.overflowWrap = "anywhere"; detail.textContent = video.scope;
        const limit = document.createElement("p"); limit.textContent = "This is the renderer progress record. The completed video above has separate source, timestamp, decode and sampled visual checks; its scoped acceptance and limitations are linked alongside the player.";
        const snapshot = document.createElement("p"); snapshot.className = stale ? "muted stale" : "muted"; snapshot.textContent = `${stale ? "STALE SNAPSHOT · " : "Snapshot · "}${data.exported_at_utc}`;
        videoNode.replaceChildren(heading, count, detail, limit, snapshot);
      } else if (videoNode) {
        videoNode.textContent = "The current published snapshot does not yet contain the new chunk renderer. The R5 incomplete attempt remains retained. Use the independently reviewed video record above.";
      }
    }).catch(() => { if (videoNode) videoNode.textContent = "Live render progress is unavailable. The completed video and its independent review are linked above."; node.textContent = "The live control snapshot is unavailable. Use the full evidence index; the positive result does not imply pair acceptance."; });
})();
