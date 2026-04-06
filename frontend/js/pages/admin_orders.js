(function () {
  const box = document.getElementById("admin-orders");
  const filter = document.getElementById("order-filter");
  if (!box) return;

  async function load() {
    const q = filter && filter.value ? `?status=${encodeURIComponent(filter.value)}` : "";
    const data = await RHApi.fetch(`/api/orders/all${q}`);
    box.innerHTML = "";
    data.orders.forEach((o) => {
      box.appendChild(
        RHUi.el("div", { class: "order-card" }, [
          RHUi.el("div", { class: "row spread" }, [
            RHUi.el("strong", {}, [`#${o.id} · ${o.shop_name}`]),
            RHUi.el("span", { class: "badge" }, [o.status]),
          ]),
          (() => {
            const sel = document.createElement("select");
            sel.className = "input";
            sel.style.maxWidth = "200px";
            ["ordered", "accepted", "preparing", "ready", "completed", "cancelled"].forEach((s) => {
              const opt = document.createElement("option");
              opt.value = s;
              opt.textContent = s;
              if (s === o.status) opt.selected = true;
              sel.appendChild(opt);
            });
            sel.addEventListener("change", async (e) => {
              try {
                await RHApi.fetch("/api/order/status", {
                  method: "PATCH",
                  body: { order_id: o.id, status: e.target.value },
                });
              } catch (err) {
                alert(err.message);
              }
            });
            const lab = RHUi.el("label", { class: "small" }, ["Set status "]);
            lab.appendChild(sel);
            return lab;
          })(),
        ])
      );
    });
  }

  if (filter) filter.addEventListener("change", () => load().catch(() => {}));

  load().catch(() => {
    box.textContent = "Failed to load orders.";
  });
})();
