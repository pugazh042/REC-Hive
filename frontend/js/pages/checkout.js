(function () {
  const box = document.getElementById("checkout-summary");
  const btn = document.getElementById("confirm-order");
  const pickup = document.getElementById("pickup-note");
  const notes = document.getElementById("order-notes");
  if (!box || !btn) return;

  async function load() {
    const cart = await RHApi.fetch("/api/cart");
    box.innerHTML = "";
    if (!cart.items.length) {
      box.appendChild(
        RHUi.el("div", { class: "empty-state" }, [
          RHUi.el("p", { class: "muted" }, ["Cart is empty."]),
          RHUi.el("a", { class: "btn btn--primary btn--block mt-2", href: "/outlets/" }, ["Browse outlets"]),
        ])
      );
      btn.disabled = true;
      return;
    }
    btn.disabled = false;
    const list = RHUi.el("div", { class: "stack gap-2" }, []);
    cart.items.forEach((i) => {
      const img = i.image || RHUi.placeholderImg();
      list.appendChild(
        RHUi.el("div", { class: "product-card" }, [
          RHUi.el("img", {
            class: "product-card__img",
            style: "width:64px;height:64px;",
            src: img,
            alt: "",
            loading: "lazy",
          }),
          RHUi.el("div", { class: "product-card__body" }, [
            RHUi.el("strong", { class: "small" }, [`${i.name} × ${i.quantity}`]),
            RHUi.el("span", { class: "muted small" }, [i.shop_name]),
          ]),
          RHUi.el("strong", {}, [`₹${Number(i.line_total).toFixed(0)}`]),
        ])
      );
    });
    box.appendChild(list);
    box.appendChild(
      RHUi.el("div", { class: "row spread mt-3 pt-2", style: "border-top:1px solid var(--border);" }, [
        RHUi.el("strong", {}, ["Total"]),
        RHUi.el("strong", { class: "h2" }, [`₹${Number(cart.subtotal).toFixed(0)}`]),
      ])
    );
  }

  btn.addEventListener("click", async () => {
    const ok = await RHConfirm.ask("Place this order for pickup?");
    if (!ok) return;
    try {
      const { order } = await RHApi.fetch("/api/order/create", {
        method: "POST",
        body: {
          pickup_location: pickup.value.trim(),
          special_instructions: notes.value.trim(),
        },
      });
      if (window.RHToast) RHToast.success("Order placed");
      window.location.href = `/orders/${order.id}/track/`;
    } catch (e) {
      if (window.RHToast) RHToast.error(e.message || "Order failed");
    }
  });

  load().catch(() => {
    if (window.RHToast) RHToast.error("Could not load checkout");
  });
})();
