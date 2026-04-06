(function () {
  const stats = document.getElementById("sk-stats");
  const nameEl = document.getElementById("sk-shop-name");
  if (!stats) return;

  async function init() {
    const me = await RHApi.fetch("/api/me");
    const shops = await RHApi.fetch("/api/shops");
    const mine = shops.shops.find((s) => s.owner_id === me.user.id);
    if (!mine) {
      nameEl.textContent = "No shop assigned to your account.";
      return;
    }
    nameEl.textContent = mine.name;
    const orders = await RHApi.fetch("/api/orders/all");
    const today = new Date().toDateString();
    const mineOrders = orders.orders.filter((o) => o.shop_id === mine.id);
    const todayOrders = mineOrders.filter((o) => new Date(o.created_at).toDateString() === today);
    const revenue = mineOrders
      .filter((o) => o.status === "completed")
      .reduce((a, o) => a + Number(o.total), 0);
    const prods = await RHApi.fetch(`/api/products?shop=${encodeURIComponent(mine.slug)}`);
    stats.innerHTML = "";
    [
      ["Orders today", todayOrders.length],
      ["Revenue (completed)", `₹${revenue.toFixed(0)}`],
      ["Active menu items", prods.products.filter((p) => p.is_available).length],
    ].forEach(([k, v]) => {
      stats.appendChild(
        RHUi.el("div", { class: "stat-pill" }, [
          RHUi.el("span", { class: "muted small" }, [k]),
          RHUi.el("strong", {}, [String(v)]),
        ])
      );
    });
  }

  init().catch(() => {
    stats.textContent = "Could not load dashboard.";
  });
})();
