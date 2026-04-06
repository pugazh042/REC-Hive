(function () {
  const list = document.getElementById("sk-products");
  const form = document.getElementById("sk-product-form");
  const catSel = document.getElementById("sk-cat");
  const fileIn = document.getElementById("sk-image");
  const prev = document.getElementById("sk-preview");
  if (!list || !form) return;

  let shopSlug = null;

  fileIn.addEventListener("change", () => {
    const f = fileIn.files && fileIn.files[0];
    if (!f) {
      prev.hidden = true;
      return;
    }
    prev.src = URL.createObjectURL(f);
    prev.hidden = false;
  });

  async function resolveShop() {
    const me = await RHApi.fetch("/api/me");
    const shops = await RHApi.fetch("/api/shops");
    const mine = shops.shops.find((s) => s.owner_id === me.user.id);
    shopSlug = mine ? mine.slug : null;
    return shopSlug;
  }

  async function loadCats() {
    const data = await RHApi.fetch("/api/categories");
    catSel.innerHTML = '<option value="">—</option>';
    data.categories.forEach((c) => {
      const o = document.createElement("option");
      o.value = c.id;
      o.textContent = c.name;
      catSel.appendChild(o);
    });
  }

  async function load() {
    await resolveShop();
    if (!shopSlug) {
      list.innerHTML = "<p class='muted'>No shop on your account.</p>";
      return;
    }
    const data = await RHApi.fetch(`/api/products?shop=${encodeURIComponent(shopSlug)}`);
    list.innerHTML = "";
    data.products.forEach((p) => {
      const img = p.image || RHUi.placeholderImg();
      const tile = RHUi.el("article", { class: "product-tile" }, [
        RHUi.el("div", { class: "product-tile__media" }, [
          RHUi.el("img", { src: img, alt: "", loading: "lazy" }),
        ]),
        RHUi.el("div", { class: "product-tile__body" }, [
          RHUi.el("strong", { class: "small" }, [p.name]),
          RHUi.el("span", { class: "h2" }, [RHUi.money(p.price)]),
          RHUi.el(
            "span",
            { class: `badge ${p.is_available ? "badge--available" : "badge--unavailable"}` },
            [p.is_available ? "Listed" : "Hidden"]
          ),
          RHUi.el(
            "button",
            {
              type: "button",
              class: "btn btn--secondary btn--block mt-1",
              onclick: async () => {
                try {
                  await RHApi.fetch(`/api/shopkeeper/products/${p.id}`, {
                    method: "PATCH",
                    body: { is_available: !p.is_available },
                  });
                  if (window.RHToast) RHToast.success("Updated");
                  load().catch(() => {});
                } catch (e) {
                  if (window.RHToast) RHToast.error(e.message);
                }
              },
            },
            [p.is_available ? "Mark unavailable" : "Mark available"]
          ),
          RHUi.el(
            "button",
            {
              type: "button",
              class: "btn btn--ghost btn--block mt-1",
              onclick: async () => {
                const ok = await RHConfirm.ask(`Delete ${p.name}?`);
                if (!ok) return;
                try {
                  await RHApi.fetch(`/api/shopkeeper/products/${p.id}`, { method: "DELETE", body: {} });
                  if (window.RHToast) RHToast.success("Removed");
                  load().catch(() => {});
                } catch (e) {
                  if (window.RHToast) RHToast.error(e.message);
                }
              },
            },
            ["Delete"]
          ),
        ]),
      ]);
      list.appendChild(tile);
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await resolveShop();
    if (!shopSlug) return;
    const fd = new FormData(form);
    fd.set("is_available", form.querySelector("[name=is_available]").checked ? "true" : "false");
    if (!fileIn.files || !fileIn.files[0]) {
      if (window.RHToast) RHToast.error("Add a product photo");
      return;
    }
    try {
      await RHApi.fetch("/api/shopkeeper/products", { method: "POST", body: fd });
      if (window.RHToast) RHToast.success("Product saved");
      form.reset();
      prev.hidden = true;
      load().catch(() => {});
    } catch (err) {
      if (window.RHToast) RHToast.error(err.message || "Failed");
    }
  });

  loadCats()
    .then(() => load())
    .catch(() => {
      if (window.RHToast) RHToast.error("Failed to load");
    });
})();
