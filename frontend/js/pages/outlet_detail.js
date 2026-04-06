(function () {
  const slug = window.__SHOP_SLUG__;
  const hero = document.getElementById("shop-hero");
  const products = document.getElementById("shop-products");
  if (!slug || !hero || !products) return;

  async function load() {
    const { shop } = await RHApi.fetch(`/api/shops/${encodeURIComponent(slug)}`);
    const { products: items } = await RHApi.fetch(`/api/products?shop=${encodeURIComponent(slug)}`);
    hero.innerHTML = "";
    hero.appendChild(
      RHUi.el("div", { style: "padding:var(--s-2) var(--s-3);" }, [
        RHUi.el("h2", { class: "h1", style: "margin:0 0 8px;" }, [shop.name]),
        RHUi.el("p", { class: "muted small" }, [shop.description || "Campus outlet"]),
        RHUi.el("p", { class: "small mt-2" }, [
          shop.is_open ? RHUi.el("span", { class: "badge badge--open" }, ["Open"]) : "",
          ` · ★ ${shop.rating}`,
        ]),
      ])
    );
    products.innerHTML = "";
    products.className = "product-grid";
    items.forEach((p) => {
      const img = p.image || RHUi.placeholderImg();
      const tile = RHUi.el("article", { class: "product-tile" }, [
        RHUi.el("a", { class: "product-tile__media", href: `/outlets/${slug}/p/${p.slug}/` }, [
          RHUi.el("img", { src: img, alt: "", loading: "lazy" }),
        ]),
        RHUi.el("div", { class: "product-tile__body" }, [
          RHUi.el("strong", { class: "small" }, [p.name]),
          RHUi.el("span", { class: "h2" }, [RHUi.money(p.price)]),
          RHUi.el(
            "span",
            { class: `badge ${p.is_available ? "badge--available" : "badge--unavailable"}` },
            [p.is_available ? "Available" : "Off menu"]
          ),
          RHUi.el("div", { class: "product-tile__actions stack gap-1" }, [
            RHUi.el(
              "a",
              { class: "btn btn--secondary btn--block", href: `/outlets/${slug}/p/${p.slug}/` },
              ["Details"]
            ),
            RHUi.el(
              "button",
              {
                type: "button",
                class: "btn btn--primary btn--block",
                disabled: !p.is_available,
                onclick: async () => {
                  try {
                    await RHApi.fetch("/api/cart/add", {
                      method: "POST",
                      body: { product_id: p.id, quantity: 1 },
                    });
                    if (window.RHToast) RHToast.success("Added to cart");
                    window.location.href = "/cart/";
                  } catch (e) {
                    if (window.RHToast) RHToast.error(e.message || "Could not add");
                  }
                },
              },
              ["Add to cart"]
            ),
          ]),
        ]),
      ]);
      products.appendChild(tile);
    });
    if (!items.length) {
      products.className = "stack";
      products.appendChild(
        RHUi.el("div", { class: "empty-state" }, [
          RHUi.el("div", { class: "empty-state__art" }, ["📋"]),
          RHUi.el("p", {}, ["No items listed yet."]),
        ])
      );
    }
  }

  load().catch(() => {
    hero.textContent = "Shop not found.";
  });
})();
