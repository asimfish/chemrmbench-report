"use strict";
(() => {
  const video = document.getElementById("comparison-refined");
  const output = document.getElementById("playback-refined");
  const update = () => { output.textContent = `原生时刻 ${Math.min(video.currentTime + 0.04, 23).toFixed(2)} / 23.00 s`; };
  video.addEventListener("timeupdate", update);
  video.addEventListener("loadedmetadata", update);
  document.querySelectorAll("button[data-refined-seek]").forEach(button => {
    button.addEventListener("click", () => {
      const seek = () => { video.currentTime = Number(button.dataset.refinedSeek); update(); };
      if (video.readyState >= 1) seek();
      else { video.addEventListener("loadedmetadata", seek, { once: true }); video.load(); }
    });
  });
})();
