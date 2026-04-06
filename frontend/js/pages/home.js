(function () {
  const root = document.getElementById("home-root");
  if (!root) return;

  const chips = document.getElementById("category-chips");
  const featured = document.getElementById("featured-shops");
  const popular = document.getElementById("popular-items");

  function shopCard(s) {
    const img = s.image || RHUi.placeholderImg();
    const open = s.is_open;
    return RHUi.el("a", { class: "shop-card card--interactive", href: `/outlets/${s.slug}/` }, [
      RHUi.el("img", { class: "shop-card__img", src: img, alt: "", loading: "lazy" }),
      RHUi.el("div", { class: "shop-card__meta" }, [
        RHUi.el("strong", {}, [s.name]),
        RHUi.el("span", { class: "muted small" }, [s.category_name || "Outlet"]),
        RHUi.el(
          "span",
          { class: `badge ${open ? "badge--open" : "badge--closed"}` },
          [open ? "Open" : "Closed"]
        ),
      ]),
      RHUi.el("span", { class: "muted small" }, [`★ ${s.rating}`]),
    ]);
  }

  function productTile(p) {
    const img = p.image || RHUi.placeholderImg();
    const avail = p.is_available;
    const tile = RHUi.el("article", { class: "product-tile card--interactive" }, [
      RHUi.el("a", { class: "product-tile__media", href: `/outlets/${p.shop_slug}/p/${p.slug}/` }, [
        RHUi.el("img", { src: img, alt: "", loading: "lazy" }),
      ]),
      RHUi.el("div", { class: "product-tile__body" }, [
        RHUi.el("strong", { class: "small" }, [p.name]),
        RHUi.el("span", { class: "muted small" }, [p.shop_name]),
        RHUi.el("span", { class: "h2" }, [RHUi.money(p.price)]),
        RHUi.el(
          "span",
          { class: `badge ${avail ? "badge--available" : "badge--unavailable"}` },
          [avail ? "In stock" : "Unavailable"]
        ),
        RHUi.el("div", { class: "product-tile__actions" }, [
          RHUi.el(
            "button",
            {
              type: "button",
              class: "btn btn--primary btn--block",
              disabled: !avail,
              onclick: async (e) => {
                e.preventDefault();
                try {
                  await RHApi.fetch("/api/cart/add", {
                    method: "POST",
                    body: { product_id: p.id, quantity: 1 },
                  });
                  if (window.RHToast) RHToast.success("Added to cart");
                  window.location.href = "/cart/";
                } catch (err) {
                  if (window.RHToast) RHToast.error(err.message || "Could not add");
                }
              },
            },
            ["Add to cart"]
          ),
        ]),
      ]),
    ]);
    return tile;
  }

  function skeletonGrid(n) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < n; i += 1) {
      const d = document.createElement("div");
      d.className = "product-tile";
      d.innerHTML = '<div class="skeleton skeleton--card"></div>';
      frag.appendChild(d);
    }
    return frag;
  }

  async function load() {
    popular.appendChild(skeletonGrid(4));
    const [cats, shops, prods] = await Promise.all([
      RHApi.fetch("/api/categories"),
      RHApi.fetch("/api/shops"),
      RHApi.fetch("/api/products?popular=1"),
    ]);
    chips.innerHTML = "";
    cats.categories.forEach((c) => {
      const b = RHUi.el("button", { type: "button", class: "chip", "data-slug": c.slug }, [
        `${c.icon || ""} ${c.name}`.trim(),
      ]);
      b.addEventListener("click", () => {
        window.location.href = `/outlets/?category=${encodeURIComponent(c.slug)}`;
      });
      chips.appendChild(b);
    });
    featured.innerHTML = "";
    shops.shops.slice(0, 6).forEach((s) => featured.appendChild(shopCard(s)));
    popular.innerHTML = "";
    let list = prods.products;
    if (!list.length) {
      const all = await RHApi.fetch("/api/products");
      list = all.products;
    }
    list.slice(0, 8).forEach((p) => popular.appendChild(productTile(p)));
  }

  load().catch(() => {
    popular.innerHTML = "";
    if (window.RHToast) RHToast.error("Could not load home content");
    featured.innerHTML = "<p class='muted'>Try again later.</p>";
  });
})();
