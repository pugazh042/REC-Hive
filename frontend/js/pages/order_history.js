(function () {
  const list = document.getElementById("orders-list");
  if (!list) return;

  RHApi.fetch("/api/orders")
    .then((data) => {
      list.innerHTML = "";
      if (!data.orders.length) {
        list.appendChild(
          RHUi.el("div", { class: "empty-state" }, [
            RHUi.el("div", { class: "empty-state__art" }, ["🧾"]),
            RHUi.el("p", {}, ["No orders yet."]),
            RHUi.el("a", { class: "btn btn--primary btn--block mt-2", href: "/outlets/" }, ["Browse outlets"]),
          ])
        );
        return;
      }
      data.orders.forEach((o) => {
        const thumbs = RHUi.el("div", { class: "row gap-sm mt-1", style: "flex-wrap:wrap;" }, []);
        (o.items || []).slice(0, 4).forEach((i) => {
          thumbs.appendChild(
            RHUi.el("img", {
              src: i.image || RHUi.placeholderImg(),
              width: "40",
              height: "40",
              alt: "",
              loading: "lazy",
              style: "border-radius:10px;object-fit:cover;",
            })
          );
        });
        const card = RHUi.el("div", { class: "order-card card--interactive" }, [
          RHUi.el("div", { class: "row spread" }, [
            RHUi.el("strong", {}, [`#${o.id} ${o.shop_name}`]),
            RHUi.el("span", { class: "badge" }, [o.status]),
          ]),
          thumbs,
          RHUi.el("span", { class: "muted small" }, [`Total ₹${Number(o.total).toFixed(0)}`]),
          RHUi.el("div", { class: "row gap-sm mt-1" }, [
            RHUi.el("a", { class: "btn btn--secondary", href: `/orders/${o.id}/track/` }, ["Track"]),
            RHUi.el(
              "button",
              {
                type: "button",
                class: "btn btn--ghost",
                onclick: () => {
                  if (window.RHToast) RHToast.show("Open the outlet and add items again to reorder.");
                },
              },
              ["Reorder"]
            ),
          ]),
        ]);
        list.appendChild(card);
      });
    })
    .catch(() => {
      if (window.RHToast) RHToast.error("Failed to load orders");
    });
})();
