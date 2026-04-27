document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".hamburger");
  const backdrop = document.querySelector(".side-backdrop");
  const sidebarLinks = document.querySelectorAll(".side .nav a");

  const close = () => document.body.classList.remove("side-open");
  if (btn) btn.addEventListener("click", () => document.body.classList.toggle("side-open"));
  if (backdrop) backdrop.addEventListener("click", close);
  sidebarLinks.forEach(link => link.addEventListener("click", close));

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
});
