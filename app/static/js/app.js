document.addEventListener("DOMContentLoaded", () => {
  // ── Mobile hamburger ──────────────────────────────────────────────
  const btn = document.querySelector(".hamburger");
  const backdrop = document.querySelector(".side-backdrop");
  const sidebarLinks = document.querySelectorAll(".side .nav a");

  const closeSideMobile = () => document.body.classList.remove("side-open");
  if (btn) btn.addEventListener("click", () => document.body.classList.toggle("side-open"));
  if (backdrop) backdrop.addEventListener("click", closeSideMobile);
  sidebarLinks.forEach(link => link.addEventListener("click", closeSideMobile));

  // ── Sidebar collapse (desktop) ────────────────────────────────────
  const collapseBtn = document.getElementById("sideCollapseBtn");
  const expandBtn   = document.getElementById("sideExpandBtn");
  const SIDE_KEY    = "fin_side_collapsed";

  const setSideCollapsed = (collapsed) => {
    document.body.classList.toggle("side-collapsed", collapsed);
    localStorage.setItem(SIDE_KEY, collapsed ? "1" : "0");
  };
  if (localStorage.getItem(SIDE_KEY) === "1") document.body.classList.add("side-collapsed");
  if (collapseBtn) collapseBtn.addEventListener("click", () => setSideCollapsed(true));
  if (expandBtn)   expandBtn.addEventListener("click",   () => setSideCollapsed(false));

  // ── Modal ─────────────────────────────────────────────────────────
  const overlay   = document.getElementById("modal-overlay");
  const modalBody = document.getElementById("modal-body");
  const modalTitleEl = document.getElementById("modal-title");
  const modalClose = document.getElementById("modal-close");

  const openModal = (title) => {
    if (title && modalTitleEl) modalTitleEl.textContent = title;
    overlay.classList.add("modal-open");
    document.body.style.overflow = "hidden";
    setTimeout(() => {
      const first = modalBody.querySelector("input, textarea, select");
      if (first) first.focus();
    }, 80);
  };

  const closeModal = () => {
    overlay.classList.remove("modal-open");
    document.body.style.overflow = "";
    setTimeout(() => { if (modalBody) modalBody.innerHTML = ""; }, 220);
  };

  if (modalClose) modalClose.addEventListener("click", closeModal);
  if (overlay) overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });

  // Open modal on HTMX afterSwap into #modal-body
  document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.detail.target && e.detail.target.id === "modal-body") {
      const trigger = e.detail.requestConfig && e.detail.requestConfig.elt;
      const title = trigger ? (trigger.dataset.modalTitle || trigger.textContent.trim()) : "formulário";
      openModal(title);
    }
  });

  // ── Global keyboard shortcuts ─────────────────────────────────────
  document.addEventListener("keydown", (e) => {
    const tag = document.activeElement.tagName;
    const inInput = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";

    if (e.key === "Escape") {
      if (overlay && overlay.classList.contains("modal-open")) { closeModal(); return; }
      closeSideMobile();
    }

    if (!inInput && (e.key === "b" || e.key === "B")) {
      setSideCollapsed(!document.body.classList.contains("side-collapsed"));
    }
  });
});
