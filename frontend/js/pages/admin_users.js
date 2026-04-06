(function () {
  const tbody = document.querySelector("#users-table tbody");
  if (!tbody) return;

  async function load() {
    const data = await RHApi.fetch("/api/admin/users");
    tbody.innerHTML = "";
    data.users.forEach((u) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${u.email}</td><td>${u.role || "—"}</td><td>${u.order_count}</td><td>${
        u.is_blocked ? "Blocked" : u.is_active ? "Active" : "Inactive"
      }</td><td></td>`;
      const td = tr.querySelector("td:last-child");
      const btn = RHUi.el(
        "button",
        {
          type: "button",
          class: "btn btn--secondary",
          onclick: async () => {
            await RHApi.fetch(`/api/admin/users/${u.id}`, {
              method: "PATCH",
              body: { is_blocked: !u.is_blocked },
            });
            load().catch(() => {});
          },
        },
        [u.is_blocked ? "Unblock" : "Block"]
      );
      td.appendChild(btn);
      tbody.appendChild(tr);
    });
  }

  load().catch(() => {
    tbody.innerHTML = "<tr><td colspan='5'>Failed to load</td></tr>";
  });
})();
