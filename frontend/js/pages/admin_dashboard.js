(function () {
  const el = document.getElementById("admin-stats");
  if (!el) return;
  RHApi.fetch("/api/admin/analytics")
    .then((d) => {
      const t = d.totals;
      el.innerHTML = "";
      [
        ["Total orders", t.orders],
        ["Total revenue ₹", t.revenue],
        ["Total products", t.products],
        ["Total shops", t.shops],
        ["Users", t.users],
        ["Orders today", d.orders_today],
        ["Orders (7 days)", d.orders_week],
      ].forEach(([label, val]) => {
        el.appendChild(
          RHUi.el("div", { class: "stat-pill" }, [
            RHUi.el("span", { class: "muted small" }, [label]),
            RHUi.el("strong", {}, [String(val)]),
          ])
        );
      });
    })
    .catch(() => {
      if (window.RHToast) RHToast.error("Could not load stats");
      el.textContent = "—";
    });
})();
