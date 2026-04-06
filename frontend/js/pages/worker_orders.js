(function () {
  const box = document.getElementById("wk-orders");
  if (!box) return;

  const flow = {
    accepted: "preparing",
    preparing: "ready",
    ready: "completed",
  };

  const labels = {
    preparing: "Start preparing",
    ready: "Mark ready",
    completed: "Complete pickup",
  };

  function cardClass(status) {
    if (status === "preparing") return "order-card order-card--preparing";
    if (status === "ready") return "order-card order-card--ready";
    if (status === "ordered") return "order-card order-card--pending";
    return "order-card";
  }

  async function load() {
    const data = await RHApi.fetch("/api/orders/kitchen");
    box.innerHTML = "";
    if (!data.orders.length) {
      box.appendChild(
        RHUi.el("div", { class: "empty-state" }, [
          RHUi.el("div", { class: "empty-state__art" }, ["👨‍🍳"]),
          RHUi.el("p", {}, ["No active tickets."]),
          RHUi.el("p", { class: "small muted" }, ["Ask admin to assign you to a shop."]),
        ])
      );
      return;
    }
    data.orders.forEach((o) => {
      const next = flow[o.status];
      const action =
        next &&
        RHUi.el(
          "button",
          {
            type: "button",
            class: "btn btn--primary btn--block mt-2",
            onclick: async () => {
              const ok = await RHConfirm.ask(`Move order #${o.id} to ${next}?`);
              if (!ok) return;
              try {
                await RHApi.fetch("/api/order/status", {
                  method: "PATCH",
                  body: { order_id: o.id, status: next },
                });
                if (window.RHToast) RHToast.success("Updated");
                load().catch(() => {});
              } catch (e) {
                if (window.RHToast) RHToast.error(e.message);
              }
            },
          },
          [labels[next] || "Update"]
        );
      const wait =
        o.status === "ordered" &&
        RHUi.el("p", { class: "muted small mt-2" }, ["Waiting for shop to accept."]);
      const imgs = RHUi.el("div", { class: "row gap-sm", style: "flex-wrap:wrap;" }, []);
      o.items.forEach((it) => {
        const src = it.image || RHUi.placeholderImg();
        imgs.appendChild(
          RHUi.el("img", {
            src,
            alt: "",
            width: "48",
            height: "48",
            loading: "lazy",
            style: "border-radius:12px;object-fit:cover;border:1px solid var(--border);",
          })
        );
      });
      const card = RHUi.el("div", { class: cardClass(o.status) }, [
        RHUi.el("strong", {}, [`#${o.id} · ${o.shop_name}`]),
        RHUi.el("span", { class: "badge badge--primary" }, [o.status]),
        imgs,
        RHUi.el("p", { class: "small" }, [o.special_instructions || "—"]),
        RHUi.el(
          "ul",
          { class: "muted small" },
          o.items.map((i) => RHUi.el("li", {}, [`${i.name} × ${i.quantity}`]))
        ),
      ]);
      if (wait) card.appendChild(wait);
      if (action) card.appendChild(action);
      box.appendChild(card);
    });
  }

  load().catch(() => {
    if (window.RHToast) RHToast.error("Could not load kitchen queue");
  });
})();
