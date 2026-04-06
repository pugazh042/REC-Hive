(function () {
  const box = document.getElementById("sk-orders");
  if (!box) return;

  const flow = {
    ordered: "accepted",
    accepted: "preparing",
    preparing: "ready",
    ready: "completed",
  };

  async function load() {
    const data = await RHApi.fetch("/api/orders/all");
    box.innerHTML = "";
    if (!data.orders.length) {
      box.appendChild(
        RHUi.el("div", { class: "empty-state" }, [
          RHUi.el("div", { class: "empty-state__art" }, ["📋"]),
          RHUi.el("p", {}, ["No orders for your shop yet."]),
        ])
      );
      return;
    }
    data.orders.forEach((o) => {
      const next = flow[o.status];
      const row = RHUi.el("div", { class: "row gap-sm mt-1", style: "flex-wrap:wrap;" }, []);
      o.items.forEach((i) => {
        row.appendChild(
          RHUi.el("img", {
            src: i.image || RHUi.placeholderImg(),
            width: "44",
            height: "44",
            alt: "",
            loading: "lazy",
            style: "border-radius:10px;object-fit:cover;border:1px solid var(--border);",
          })
        );
      });
      box.appendChild(
        RHUi.el("div", { class: "order-card" }, [
          RHUi.el("div", { class: "row spread" }, [
            RHUi.el("strong", {}, [`#${o.id}`]),
            RHUi.el("span", { class: "badge badge--primary" }, [o.status]),
          ]),
          row,
          RHUi.el(
            "ul",
            { class: "muted small" },
            o.items.map((i) => RHUi.el("li", {}, [`${i.name} × ${i.quantity}`]))
          ),
          next
            ? RHUi.el(
                "button",
                {
                  type: "button",
                  class: "btn btn--primary btn--block mt-1",
                  onclick: async () => {
                    const ok = await RHConfirm.ask(`Update order #${o.id} to ${next}?`);
                    if (!ok) return;
                    try {
                      await RHApi.fetch("/api/order/status", {
                        method: "PATCH",
                        body: { order_id: o.id, status: next },
                      });
                      if (window.RHToast) RHToast.success("Status updated");
                      load().catch(() => {});
                    } catch (e) {
                      if (window.RHToast) RHToast.error(e.message);
                    }
                  },
                },
                [`Mark ${next}`]
              )
            : RHUi.el("span", { class: "muted small" }, ["No further actions"]),
        ])
      );
    });
  }

  load().catch(() => {
    if (window.RHToast) RHToast.error("Could not load orders");
  });
})();
