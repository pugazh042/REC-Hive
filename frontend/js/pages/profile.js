(function () {
  const form = document.getElementById("profile-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    try {
      await RHApi.fetch("/api/profile", {
        method: "PATCH",
        body: {
          first_name: fd.get("first_name"),
          last_name: fd.get("last_name"),
          phone: fd.get("phone"),
        },
      });
      if (window.RHToast) RHToast.success("Profile saved");
    } catch (err) {
      if (window.RHToast) RHToast.error(err.message || "Save failed");
    }
  });
})();
