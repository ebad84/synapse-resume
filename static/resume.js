/* Vanilla JS; content and projects remain server-rendered without it. */
(function () {
  "use strict";
  const root = document.documentElement;
  const theme = document.getElementById("themeBtn");
  function applyTheme(value) {
    root.dataset.theme = value === "dark" ? "dark" : "light";
    theme.textContent = root.dataset.theme === "dark" ? theme.dataset.light : theme.dataset.dark;
    theme.setAttribute("aria-pressed", String(root.dataset.theme === "dark"));
    try { localStorage.setItem("synapse-theme", root.dataset.theme); } catch (_) {}
  }
  applyTheme(root.dataset.theme);
  theme.addEventListener("click", () => applyTheme(root.dataset.theme === "dark" ? "light" : "dark"));
  const assembly = document.getElementById("iso-toggle");
  assembly.addEventListener("click", () => {
    assembly.setAttribute("aria-pressed", String(assembly.getAttribute("aria-pressed") !== "true"));
  });
  const cards = Array.from(document.querySelectorAll(".project[data-category]"));
  const filters = Array.from(document.querySelectorAll("[data-filter]"));
  filters.forEach(button => button.addEventListener("click", () => {
    filters.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    let visible = 0;
    cards.forEach(card => {
      card.hidden = button.dataset.filter !== "all" && card.dataset.category !== button.dataset.filter;
      if (!card.hidden) visible++;
    });
    document.getElementById("filter-status").hidden = visible > 0 || cards.length === 0;
  }));
  const copy = document.getElementById("copy");
  const originalLabel = copy.textContent;
  let resetTimer;
  copy.addEventListener("click", async () => {
    const command = document.getElementById("command");
    const status = document.getElementById("copy-status");
    try {
      await navigator.clipboard.writeText(command.textContent.trim());
      copy.textContent = copy.dataset.copied;
      status.textContent = copy.dataset.copied;
    } catch (_) {
      command.focus();
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(command);
      if (selection) { selection.removeAllRanges(); selection.addRange(range); }
      copy.textContent = copy.dataset.fallback;
      status.textContent = copy.dataset.fallback;
    }
    clearTimeout(resetTimer);
    resetTimer = setTimeout(() => { copy.textContent = originalLabel; status.textContent = ""; }, 2400);
  });
  // Keep the original 418 easter egg without hijacking text fields.
  let buffer = "";
  document.addEventListener("keydown", event => {
    const target = event.target;
    if (event.ctrlKey || event.metaKey || event.altKey || (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)))) return;
    if (event.key.length === 1) {
      buffer = (buffer + event.key).slice(-3);
      if (buffer === "418") location.href = "/teapot" + (document.body.dataset.lang === "fa" ? "?lang=fa" : "");
    }
  });
})();
