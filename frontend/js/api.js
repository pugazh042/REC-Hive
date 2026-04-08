const API_BASE = "http://127.0.0.1:8000";

async function apiFetch(path, options = {}, tokenKey = "token") {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = tokenKey ? localStorage.getItem(tokenKey) : null;
  if (token) headers.Authorization = `Token ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getApiErrorMessage(data) || "Request failed");
  }
  return data;
}

function getApiErrorMessage(data) {
  if (!data) return "";
  if (typeof data === "string") return data;
  if (typeof data.detail === "string") return data.detail;
  for (const key of Object.keys(data)) {
    const value = data[key];
    if (typeof value === "string") return value;
    if (Array.isArray(value) && value.length) return `${key}: ${value[0]}`;
    if (value && typeof value === "object") {
      const nested = getApiErrorMessage(value);
      if (nested) return nested;
    }
  }
  return "";
}

function getToken(key = "token") {
  return localStorage.getItem(key);
}

function setToken(token, key = "token") {
  localStorage.setItem(key, token);
}

function clearToken(key = "token") {
  localStorage.removeItem(key);
}

function requireAuth(redirectTo = "login.html") {
  if (!getToken("token")) {
    const next = encodeURIComponent(window.location.pathname.split("/").pop() || "home.html");
    window.location.href = `${redirectTo}?next=${next}&reason=auth`;
    return false;
  }
  return true;
}

function requireShopAuth(redirectTo = "shop-login.html") {
  if (!getToken("shopToken")) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

function showMessage(text, type = "info") {
  const message = document.createElement("div");
  message.className = `toast toast-${type}`;
  message.textContent = text;
  document.body.appendChild(message);
  setTimeout(() => message.classList.add("show"), 10);
  setTimeout(() => {
    message.classList.remove("show");
    setTimeout(() => message.remove(), 250);
  }, 2200);
}

function goBackOrHome(home = "home.html") {
  if (window.history.length > 1) {
    window.history.back();
  } else {
    window.location.href = home;
  }
}

function promptAuthChoice(nextPage = "orders.html") {
  const signIn = window.confirm("Please sign in to view Orders. Click OK to Sign In, or Cancel to Sign Up.");
  const next = encodeURIComponent(nextPage);
  window.location.href = signIn
    ? `login.html?next=${next}&reason=auth`
    : `register.html?next=${next}&reason=auth`;
}

function wireOrdersAuthGuard() {
  document.querySelectorAll('a[href="orders.html"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      if (getToken("token")) return;
      e.preventDefault();
      promptAuthChoice("orders.html");
    });
  });
}

function wireProfileButton(containerId = "profileSlot") {
  const slot = document.getElementById(containerId);
  if (!slot || !getToken("token")) return;
  slot.innerHTML = '<a class="btn-login-nav" href="profile.html">Profile</a>';
}

document.addEventListener("DOMContentLoaded", () => {
  wireOrdersAuthGuard();
  wireProfileButton("profileSlot");
});
