"use strict";
const video = document.getElementById("comparison");
const output = document.getElementById("playback");
function updateTime() {
  const duration = Number.isFinite(video.duration) ? video.duration : 23;
  output.textContent = `${video.currentTime.toFixed(2)} / ${duration.toFixed(2)} s`;
}
video.addEventListener("timeupdate", updateTime);
video.addEventListener("loadedmetadata", updateTime);
document.querySelectorAll("button[data-seek]").forEach((button) => {
  button.addEventListener("click", () => {
    const seek = () => { video.currentTime = Number(button.dataset.seek); updateTime(); };
    if (video.readyState >= 1) seek();
    else { video.addEventListener("loadedmetadata", seek, {once:true}); video.load(); }
  });
});
