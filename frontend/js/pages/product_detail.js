(function () {
  const root = document.getElementById("product-root");
  if (!root) return;
  const shop = root.dataset.shop;
  const prod = root.dataset.product;
  let qty = 1;

  const hero = document.getElementById("product-hero");
  const minus = document.getElementById("qty-minus");
  const plus = document.getElementById("qty-plus");
  const qtyVal = document.getElementById("qty-val");
  const addBtn = document.getElementById("add-cart-btn");

  function syncQty() {
    qtyVal.textContent = String(qty);
  }

  minus.addEventListener("click", () => {
    qty = Math.max(1, qty - 1);
    syncQty();
  });
  plus.addEventListener("click", () => {
    qty += 1;
    syncQty();
  });

  RHApi.fetch(`/api/shops/${encodeURIComponent(shop)}/products/${encodeURIComponent(prod)}`)
    .then((data) => {
      const p = data.product;
      hero.innerHTML = "";
      hero.appendChild(
        RHUi.el("img", {
          class: "product-hero__img",
          src: p.image || RHUi.placeholderImg(),
          alt: "",
          loading: "eager",
        })
      );
      hero.appendChild(RHUi.el("h2", { class: "h1 mt-2" }, [p.name]));
      hero.appendChild(RHUi.el("p", { class: "muted" }, [p.description || ""]));
      hero.appendChild(
        RHUi.el("p", { class: "h2" }, [
          RHUi.money(p.price),
          " ",
          RHUi.el(
            "span",
            { class: `badge ${p.is_available ? "badge--available" : "badge--unavailable"}` },
            [p.is_available ? "Available" : "Unavailable"]
          ),
        ])
      );
      addBtn.disabled = !p.is_available;
    })
    .catch(() => {
      hero.textContent = "Product not found.";
    });

  addBtn.addEventListener("click", async () => {
    try {
      const { product } = await RHApi.fetch(
        `/api/shops/${encodeURIComponent(shop)}/products/${encodeURIComponent(prod)}`
      );
      if (!product.is_available) return;
      await RHApi.fetch("/api/cart/add", {
        method: "POST",
        body: { product_id: product.id, quantity: qty },
      });
      if (window.RHToast) RHToast.success("Added to cart");
      window.location.href = "/cart/";
    } catch (e) {
      if (window.RHToast) RHToast.error(e.message || "Could not add");
    }
  });
})();
