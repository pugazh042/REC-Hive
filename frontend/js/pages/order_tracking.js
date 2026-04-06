(function () {
  const main = document.querySelector("main[data-order-id]");
  const root = document.getElementById("track-root");
  if (!main || !root) return;
  const id = main.dataset.orderId;

  const steps = [
    { key: "ordered", label: "Ordered", icon: "📝" },
    { key: "accepted", label: "Accepted", icon: "✓" },
    { key: "preparing", label: "Preparing", icon: "👨‍🍳" },
    { key: "ready", label: "Ready", icon: "📦" },
    { key: "completed", label: "Completed", icon: "🎉" },
  ];

  const orderIdx = { ordered: 0, accepted: 1, preparing: 2, ready: 3, completed: 4, cancelled: -1 };

  function render(order) {
    const idx = orderIdx[order.status] ?? 0;
    const pct =
      order.status === "cancelled"
        ? 0
        : Math.max(0, Math.min(100, ((idx + 1) / steps.length) * 100));
    root.innerHTML = "";
    root.appendChild(
      RHUi.el("p", { class: "muted small" }, [`Order #${order.id} · ${order.shop_name}`])
    );
    const wrap = RHUi.el("div", { class: "track-steps" }, []);
    steps.forEach((s, i) => {
      const done = order.status !== "cancelled" && i < idx;
      const current = i === idx && order.status !== "completed" && order.status !== "cancelled";
      const step = RHUi.el("div", { class: `track-step ${done ? "is-done" : ""} ${current ? "is-current" : ""}` }, [
        RHUi.el("div", { class: "track-step__icon", "aria-hidden": "true" }, [s.icon]),
        RHUi.el("div", {}, [
          RHUi.el("div", { class: "track-step__label" }, [s.label]),
          RHUi.el("div", { class: "track-step__sub" }, [
            done ? "Done" : current ? "In progress" : "Pending",
          ]),
        ]),
      ]);
      wrap.appendChild(step);
    });
    root.appendChild(wrap);
    root.appendChild(
      RHUi.el("div", { class: "progress" }, [
        RHUi.el("div", { class: "progress__bar", style: `width:${pct}%` }),
      ])
    );
    if (order.status === "cancelled") {
      root.appendChild(RHUi.el("p", { class: "alert alert--error mt-2" }, ["This order was cancelled."]));
    }
    const card = RHUi.el("div", { class: "card mt-3" }, [RHUi.el("strong", {}, ["Order summary"])]);
    order.items.forEach((it) => {
      const img = it.image || RHUi.placeholderImg();
      card.appendChild(
        RHUi.el("div", { class: "product-card", style: "box-shadow:none;border:none;padding:8px 0;" }, [
          RHUi.el("img", {
            class: "product-card__img",
            style: "width:56px;height:56px;",
            src: img,
            alt: "",
            loading: "lazy",
          }),
          RHUi.el("div", { class: "product-card__body" }, [
            RHUi.el("span", { class: "small" }, [`${it.name} × ${it.quantity}`]),
            RHUi.el("span", { class: "muted small" }, [`₹${Number(it.line_total).toFixed(0)}`]),
          ]),
        ])
      );
    });
    root.appendChild(card);
  }

  function poll() {
    RHApi.fetch(`/api/orders/${id}`)
      .then((d) => render(d.order))
      .catch(() => {
        root.textContent = "Could not load order.";
      });
  }

  poll();
  setInterval(poll, 8000);
})();
