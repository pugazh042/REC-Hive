(function () {
  const tbody = document.querySelector("#admin-products-table tbody");
  const form = document.getElementById("admin-product-form");
  const shopSel = document.getElementById("ap-shop");
  const catSel = document.getElementById("ap-cat");
  const fileIn = document.getElementById("ap-image");
  const prev = document.getElementById("ap-preview");
  if (!tbody || !form) return;

  fileIn.addEventListener("change", () => {
    const f = fileIn.files && fileIn.files[0];
    if (!f) {
      prev.hidden = true;
      return;
    }
    prev.src = URL.createObjectURL(f);
    prev.hidden = false;
  });

  async function loadMeta() {
    const [shops, cats] = await Promise.all([RHApi.fetch("/api/admin/shops/list"), RHApi.fetch("/api/categories")]);
    shopSel.innerHTML = "";
    shops.shops.forEach((s) => {
      const o = document.createElement("option");
      o.value = s.id;
      o.textContent = s.name;
      shopSel.appendChild(o);
    });
    catSel.innerHTML = '<option value="">—</option>';
    cats.categories.forEach((c) => {
      const o = document.createElement("option");
      o.value = c.id;
      o.textContent = c.name;
      catSel.appendChild(o);
    });
  }

  async function loadTable() {
    const data = await RHApi.fetch("/api/admin/products");
    tbody.innerHTML = "";
    data.products.forEach((p) => {
      const tr = document.createElement("tr");
      const img = p.image
        ? `<img src="${p.image}" width="44" height="44" loading="lazy" alt="">`
        : `<img src="${RHUi.placeholderImg()}" width="44" height="44" alt="">`;
      tr.innerHTML = `<td>${img}</td><td><strong>${p.name}</strong><br><span class="muted small">${p.slug}</span></td><td>${p.shop_name}</td><td>₹${Number(
        p.price
      ).toFixed(0)}</td><td>${p.is_available ? "Active" : "Off"}</td><td></td>`;
      const td = tr.querySelector("td:last-child");
      const del = document.createElement("button");
      del.type = "button";
      del.className = "btn btn--ghost";
      del.textContent = "Delete";
      del.addEventListener("click", async () => {
        const ok = await RHConfirm.ask(`Delete ${p.name}?`);
        if (!ok) return;
        try {
          await RHApi.fetch(`/api/admin/products/${p.id}`, { method: "DELETE", body: {} });
          if (window.RHToast) RHToast.success("Deleted");
          loadTable().catch(() => {});
        } catch (e) {
          if (window.RHToast) RHToast.error(e.message);
        }
      });
      td.appendChild(del);
      tbody.appendChild(tr);
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    fd.set("is_available", form.querySelector("[name=is_available]").checked ? "true" : "false");
    if (!fileIn.files || !fileIn.files[0]) {
      if (window.RHToast) RHToast.error("Choose a product image");
      return;
    }
    try {
      await RHApi.fetch("/api/admin/products", { method: "POST", body: fd });
      if (window.RHToast) RHToast.success("Product created");
      form.reset();
      prev.hidden = true;
      loadTable().catch(() => {});
    } catch (err) {
      if (window.RHToast) RHToast.error(err.message || "Failed");
    }
  });

  loadMeta()
    .then(() => loadTable())
    .catch(() => {
      if (window.RHToast) RHToast.error("Could not load products");
    });
})();
