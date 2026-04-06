(function () {
  const list = document.getElementById("cat-list");
  const form = document.getElementById("cat-form");
  if (!list || !form) return;

  async function load() {
    const data = await RHApi.fetch("/api/categories");
    list.innerHTML = "";
    data.categories.forEach((c) => {
      list.appendChild(
        RHUi.el("li", { class: "card" }, [
          RHUi.el("strong", {}, [`${c.icon || ""} ${c.name}`.trim()]),
          RHUi.el("span", { class: "muted small" }, [c.slug]),
          RHUi.el(
            "button",
            {
              type: "button",
              class: "btn btn--ghost btn--block mt-sm",
              onclick: async () => {
                if (!confirm("Delete category?")) return;
                await RHApi.fetch(`/api/admin/categories/${c.id}`, { method: "DELETE", body: {} });
                load().catch(() => {});
              },
            },
            ["Delete"]
          ),
        ])
      );
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    await RHApi.fetch("/api/admin/categories", {
      method: "POST",
      body: { name: fd.get("name"), icon: fd.get("icon") },
    });
    form.reset();
    load().catch(() => {});
  });

  load().catch(() => {
    list.textContent = "Failed.";
  });
})();
