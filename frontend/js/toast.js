(function () {
  function host() {
    let el = document.getElementById("toast-host");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast-host";
      el.className = "toast-host";
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    return el;
  }

  function show(message, variant, ms) {
    const h = host();
    const t = document.createElement("div");
    t.className = "toast" + (variant ? ` toast--${variant}` : "");
    t.textContent = message;
    h.appendChild(t);
    const dur = ms == null ? 3200 : ms;
    setTimeout(() => {
      t.style.opacity = "0";
      t.style.transition = "opacity 0.2s ease";
      setTimeout(() => t.remove(), 220);
    }, dur);
  }

  window.RHToast = { show, success: (m) => show(m, "success"), error: (m) => show(m, "error") };
})();
