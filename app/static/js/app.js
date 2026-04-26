// Menu hamburger em mobile
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".hamburger");
  const backdrop = document.querySelector(".side-backdrop");
  if (btn) {
    btn.addEventListener("click", () => document.body.classList.toggle("side-open"));
  }
  if (backdrop) {
    backdrop.addEventListener("click", () => document.body.classList.remove("side-open"));
  }
});
