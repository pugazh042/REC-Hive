(function () {
  const sum = document.getElementById("analytics-summary");
  const top = document.getElementById("top-items");
  if (!sum || !top) return;

  RHApi.fetch("/api/admin/analytics")
    .then((d) => {
      sum.innerHTML = "";
      const t = d.totals;
      Object.entries(t).forEach(([k, v]) => {
        sum.appendChild(
          RHUi.el("div", { class: "stat-pill" }, [
            RHUi.el("span", { class: "muted small" }, [k]),
            RHUi.el("strong", {}, [String(v)]),
          ])
        );
      });
      top.innerHTML = "";
      (d.top_items || []).forEach((row) => {
        top.appendChild(
          RHUi.el("li", {}, [`${row.product_name} — ${row.total_qty} sold`])
        );
      });
    })
    .catch(() => {
      if (window.RHToast) RHToast.error("Could not load analytics");
      sum.textContent = "—";
    });
})();
