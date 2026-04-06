/**
 * REC Hive API — session auth + CSRF for POST/PATCH/DELETE.
 * JSON body or FormData (multipart uploads).
 */
(function () {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  async function ensureCsrf() {
    if (getCookie("csrftoken")) return getCookie("csrftoken");
    await fetch("/api/csrf", { credentials: "same-origin" });
    return getCookie("csrftoken");
  }

  async function apiFetch(path, options = {}) {
    const opts = { credentials: "same-origin", ...options };
    const headers = new Headers(opts.headers || {});
    const method = (opts.method || "GET").toUpperCase();
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      const token = await ensureCsrf();
      if (token) headers.set("X-CSRFToken", token);
    }
    const isForm = opts.body instanceof FormData;
    if (opts.body && typeof opts.body === "object" && !isForm) {
      headers.set("Content-Type", "application/json");
      opts.body = JSON.stringify(opts.body);
    }
    opts.headers = headers;
    const res = await fetch(path, opts);
    const text = await res.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { raw: text };
    }
    if (!res.ok) {
      const err = new Error((data && data.error) || data.detail || res.statusText || "Request failed");
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  window.RHApi = { getCookie, ensureCsrf, fetch: apiFetch };
})();
