/**
 * Sticky header search: suggestions + navigate (home / outlets pages).
 */
(function () {
  function debounce(fn, ms) {
    let t;
    return (...a) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...a), ms);
    };
  }

  function init() {
    const inp = document.getElementById("global-search");
    const panel = document.getElementById("search-suggest");
    if (!inp || !panel) return;

    function close() {
      panel.classList.remove("is-open");
      panel.innerHTML = "";
    }

    inp.addEventListener("blur", () => setTimeout(close, 180));
    inp.addEventListener("focus", () => {
      if (panel.children.length) panel.classList.add("is-open");
    });

    const run = debounce(async () => {
      const q = inp.value.trim();
      if (q.length < 2) {
        close();
        return;
      }
      try {
        const [shops, prods] = await Promise.all([
          RHApi.fetch(`/api/shops?q=${encodeURIComponent(q)}`),
          RHApi.fetch(`/api/products?q=${encodeURIComponent(q)}`),
        ]);
        panel.innerHTML = "";
        const frag = document.createDocumentFragment();
        const addBtn = (label, href) => {
          const b = document.createElement("button");
          b.type = "button";
          b.textContent = label;
          b.addEventListener("mousedown", (e) => {
            e.preventDefault();
            window.location.href = href;
          });
          frag.appendChild(b);
        };
        shops.shops.slice(0, 5).forEach((s) => addBtn(`Outlet · ${s.name}`, `/outlets/${s.slug}/`));
        prods.products.slice(0, 5).forEach((p) =>
          addBtn(`Item · ${p.name} — ${p.shop_name}`, `/outlets/${p.shop_slug}/p/${p.slug}/`)
        );
        if (!frag.childNodes.length) {
          const b = document.createElement("button");
          b.type = "button";
          b.textContent = "No matches — browse all outlets";
          b.addEventListener("mousedown", (e) => {
            e.preventDefault();
            window.location.href = `/outlets/?q=${encodeURIComponent(q)}`;
          });
          frag.appendChild(b);
        }
        panel.appendChild(frag);
        panel.classList.add("is-open");
      } catch {
        close();
      }
    }, 280);

    inp.addEventListener("input", run);
    inp.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const q = inp.value.trim();
        window.location.href = q ? `/outlets/?q=${encodeURIComponent(q)}` : "/outlets/";
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
