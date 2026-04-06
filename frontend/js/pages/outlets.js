(function () {
  const list = document.getElementById("outlets-list");
  if (!list) return;

  const params = new URLSearchParams(window.location.search);
  let category = params.get("category") || "";

  function shopCard(s) {
    const img = s.image || RHUi.placeholderImg();
    return RHUi.el("a", { class: "shop-card card--interactive", href: `/outlets/${s.slug}/` }, [
      RHUi.el("img", { class: "shop-card__img", src: img, alt: "", loading: "lazy" }),
      RHUi.el("div", { class: "shop-card__meta" }, [
        RHUi.el("strong", {}, [s.name]),
        RHUi.el("span", { class: "muted small" }, [s.category_name || "Campus outlet"]),
        RHUi.el(
          "span",
          { class: `badge ${s.is_open ? "badge--open" : "badge--closed"}` },
          [s.is_open ? "Open" : "Closed"]
        ),
      ]),
      RHUi.el("span", { class: "muted small" }, [`★ ${s.rating}`]),
    ]);
  }

  function currentQuery() {
    const inp = document.getElementById("global-search");
    return inp && inp.value ? inp.value.trim() : "";
  }

  async function load() {
    const q = currentQuery();
    let url = "/api/shops";
    const bits = [];
    if (category) bits.push(`category=${encodeURIComponent(category)}`);
    if (q) bits.push(`q=${encodeURIComponent(q)}`);
    if (bits.length) url += `?${bits.join("&")}`;
    const data = await RHApi.fetch(url);
    list.innerHTML = "";
    if (!data.shops.length) {
      list.appendChild(
        RHUi.el("div", { class: "empty-state" }, [
          RHUi.el("div", { class: "empty-state__art" }, ["🍽️"]),
          RHUi.el("p", {}, ["No outlets match your filters."]),
          RHUi.el("a", { class: "btn btn--secondary btn--block mt-2", href: "/outlets/" }, ["Clear filters"]),
        ])
      );
      return;
    }
    data.shops.forEach((s) => list.appendChild(shopCard(s)));
  }

  const inp = document.getElementById("global-search");
  if (inp) {
    const u = params.get("q");
    if (u) inp.value = u;
    let t;
    inp.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(() => load().catch(() => {}), 300);
    });
  }

  load().catch(() => {
    if (window.RHToast) RHToast.error("Failed to load outlets");
    list.textContent = "";
  });
})();
