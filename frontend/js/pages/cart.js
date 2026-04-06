(function () {
  const lines = document.getElementById("cart-lines");
  const summary = document.getElementById("cart-summary");
  const empty = document.getElementById("cart-empty");
  const subtotalEl = document.getElementById("cart-subtotal");
  if (!lines) return;

  async function render() {
    const data = await RHApi.fetch("/api/cart");
    lines.innerHTML = "";
    if (!data.items.length) {
      summary.hidden = true;
      empty.hidden = false;
      empty.innerHTML = "";
      empty.appendChild(RHUi.el("div", { class: "empty-state" }, [
        RHUi.el("div", { class: "empty-state__art" }, ["🛒"]),
        RHUi.el("p", {}, ["Your cart is empty."]),
        RHUi.el("a", { class: "btn btn--primary btn--block mt-2", href: "/outlets/" }, ["Browse outlets"]),
      ]));
      return;
    }
    empty.hidden = true;
    summary.hidden = false;
    subtotalEl.textContent = `₹${Number(data.subtotal).toFixed(0)}`;
    data.items.forEach((item) => {
      const img = item.image || RHUi.placeholderImg();
      const row = RHUi.el("div", { class: "product-card" }, [
        RHUi.el("div", { style: "flex-shrink:0;width:88px;" }, [
          RHUi.el("img", {
            class: "product-card__img",
            style: "width:88px;height:88px;border-radius:14px;",
            src: img,
            alt: "",
            loading: "lazy",
          }),
        ]),
        RHUi.el("div", { class: "product-card__body" }, [
          RHUi.el("strong", {}, [item.name]),
          RHUi.el("span", { class: "muted small" }, [item.shop_name]),
          RHUi.el("span", { class: "small" }, [`Line: ₹${Number(item.line_total).toFixed(0)}`]),
        ]),
        RHUi.el("div", {}, [
          RHUi.el(
            "button",
            {
              type: "button",
              class: "icon-btn",
              "aria-label": "Decrease",
              onclick: async () => {
                const n = Math.max(0, item.quantity - 1);
                await RHApi.fetch("/api/cart/update", {
                  method: "POST",
                  body: { product_id: item.id, quantity: n },
                });
                render().catch(() => {});
              },
            },
            ["−"]
          ),
          RHUi.el("span", { class: "small", style: "margin:0 8px;font-weight:700;" }, [String(item.quantity)]),
          RHUi.el(
            "button",
            {
              type: "button",
              class: "icon-btn",
              "aria-label": "Increase",
              onclick: async () => {
                await RHApi.fetch("/api/cart/update", {
                  method: "POST",
                  body: { product_id: item.id, quantity: item.quantity + 1 },
                });
                render().catch(() => {});
              },
            },
            ["+"]
          ),
          RHUi.el(
            "button",
            {
              type: "button",
              class: "btn btn--ghost btn--block mt-1",
              onclick: async () => {
                const ok = await RHConfirm.ask("Remove this item?");
                if (!ok) return;
                await RHApi.fetch("/api/cart/remove", {
                  method: "POST",
                  body: { product_id: item.id },
                });
                render().catch(() => {});
              },
            },
            ["Remove"]
          ),
        ]),
      ]);
      lines.appendChild(row);
    });
  }

  render().catch(() => {
    if (window.RHToast) RHToast.error("Could not load cart");
  });
})();
