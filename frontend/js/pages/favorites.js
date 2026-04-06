(function () {
  const shops = document.getElementById("fav-shops");
  const products = document.getElementById("fav-products");
  if (!shops || !products) return;

  RHApi.fetch("/api/favorites")
    .then((data) => {
      shops.innerHTML = "";
      products.innerHTML = "";
      if (!data.shops.length) shops.appendChild(RHUi.el("p", { class: "muted" }, ["No saved shops."]));
      else
        data.shops.forEach((s) =>
          shops.appendChild(
            RHUi.el("a", { class: "shop-card", href: `/outlets/${s.slug}/` }, [
              RHUi.el("img", { class: "shop-card__img", src: s.image || RHUi.placeholderImg(), alt: "" }),
              RHUi.el("div", { class: "shop-card__meta" }, [
                RHUi.el("strong", {}, [s.name]),
                RHUi.el("span", { class: "muted small" }, [`★ ${s.rating}`]),
              ]),
            ])
          )
        );
      if (!data.products.length)
        products.appendChild(RHUi.el("p", { class: "muted" }, ["No saved products."]));
      else
        data.products.forEach((p) =>
          products.appendChild(
            RHUi.el(
              "a",
              { class: "product-card", href: `/outlets/${p.shop_slug}/p/${p.slug}/` },
              [
                RHUi.el("img", {
                  class: "product-card__img",
                  src: p.image || RHUi.placeholderImg(),
                  alt: "",
                }),
                RHUi.el("div", { class: "product-card__body" }, [
                  RHUi.el("strong", {}, [p.name]),
                  RHUi.el("span", { class: "small" }, [RHUi.money(p.price)]),
                ]),
              ]
            )
          )
        );
    })
    .catch(() => {
      shops.textContent = "Login to view favorites.";
    });
})();
