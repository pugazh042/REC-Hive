(function () {
  const box = document.getElementById("sk-reports-orders");
  if (!box) return;

  RHApi.fetch("/api/orders/all")
    .then((data) => {
      box.innerHTML = "";
      const recent = data.orders.slice(0, 15);
      if (!recent.length) {
        box.appendChild(RHUi.el("p", { class: "muted" }, ["No recent orders."]));
        return;
      }
      recent.forEach((o) => {
        box.appendChild(
          RHUi.el("div", { class: "order-card" }, [
            RHUi.el("div", { class: "row spread" }, [
              RHUi.el("strong", {}, [`#${o.id}`]),
              RHUi.el("span", {}, [`₹${Number(o.total).toFixed(0)} · ${o.status}`]),
            ]),
            RHUi.el("span", { class: "muted small" }, [new Date(o.created_at).toLocaleString()]),
          ])
        );
      });
    })
    .catch(() => {
      box.textContent = "Failed.";
    });
})();
