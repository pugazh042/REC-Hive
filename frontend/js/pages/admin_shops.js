(function () {
  const list = document.getElementById("admin-shops-list");
  const form = document.getElementById("admin-shop-form");
  if (!list || !form) return;

  async function load() {
    const data = await RHApi.fetch("/api/admin/shops/list");
    list.innerHTML = "";
    data.shops.forEach((s) => {
      list.appendChild(
        RHUi.el("div", { class: "order-card" }, [
          RHUi.el("strong", {}, [s.name]),
          RHUi.el("span", { class: "muted small" }, [s.slug]),
          RHUi.el("div", { class: "row gap-sm mt-sm" }, [
            RHUi.el(
              "button",
              {
                type: "button",
                class: "btn btn--secondary",
                onclick: async () => {
                  const open = !s.is_open;
                  await RHApi.fetch(`/api/admin/shops/${s.id}`, {
                    method: "PATCH",
                    body: { is_open: open },
                  });
                  if (window.RHToast) RHToast.success("Updated");
                  load().catch(() => {});
                },
              },
              [s.is_open ? "Mark closed" : "Mark open"]
            ),
            RHUi.el(
              "button",
              {
                type: "button",
                class: "btn btn--ghost",
                onclick: async () => {
                  const ok = await RHConfirm.ask("Delete this shop and related data?");
                  if (!ok) return;
                  await RHApi.fetch(`/api/admin/shops/${s.id}`, { method: "DELETE", body: {} });
                  if (window.RHToast) RHToast.success("Shop removed");
                  load().catch(() => {});
                },
              },
              ["Delete"]
            ),
          ]),
        ])
      );
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    await RHApi.fetch("/api/admin/shops", {
      method: "POST",
      body: { name: fd.get("name"), description: fd.get("description") },
    });
    form.reset();
    load().catch(() => {});
  });

  load().catch(() => {
    list.textContent = "Failed to load shops.";
  });
})();
