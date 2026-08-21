/** Cliente HTTP + helpers de auth para o Tinder do Descarte */

const API_BASE = window.location.origin;

function toast(msg, type = "ok") {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.className = "show " + type;
  clearTimeout(el._t);
  el._t = setTimeout(() => {
    el.className = "";
  }, 3500);
}

function getToken() {
  return localStorage.getItem("td_token");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("td_user") || "null");
  } catch {
    return null;
  }
}

function saveSession(token, role, usuario_id, email) {
  localStorage.setItem("td_token", token);
  localStorage.setItem(
    "td_user",
    JSON.stringify({ role, usuario_id, email })
  );
}

function clearSession() {
  localStorage.removeItem("td_token");
  localStorage.removeItem("td_user");
}

function authHeaders(extra = {}) {
  const h = { ...extra };
  const t = getToken();
  if (t) h["Authorization"] = `Bearer ${t}`;
  return h;
}

async function api(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    ...options,
    headers: {
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...authHeaders(options.headers || {}),
    },
  });

  let data = null;
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }

  if (!res.ok) {
    const msg =
      (data && (data.detail || data.mensagem || data.message)) ||
      `Erro ${res.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

async function login(email, senha) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", senha);
  const res = await fetch(API_BASE + "/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Falha no login");
  saveSession(data.access_token, data.role, data.usuario_id, email);
  return data;
}

async function registrar(email, senha, role, nome) {
  return api("/auth/registro", {
    method: "POST",
    body: JSON.stringify({ email, senha, role, nome }),
  });
}

function getGeo() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocalização não disponível"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        }),
      (err) => reject(err),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });
}

function formatNum(n, decimals = 1) {
  if (n == null) return "—";
  return Number(n).toLocaleString("pt-BR", {
    maximumFractionDigits: decimals,
  });
}

function animateValue(el, end, duration = 900) {
  if (!el) return;
  const start = 0;
  const startTime = performance.now();
  function frame(now) {
    const t = Math.min(1, (now - startTime) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    const val = start + (end - start) * eased;
    el.textContent = formatNum(val, end >= 100 ? 0 : 1);
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
