// Alle Aufrufe laufen über den nginx-Proxy: /api/... -> backend:8000/...
const BASE = "/api";

async function call(method, path, body) {
  let res;
  try {
    res = await fetch(BASE + path, {
      method,
      headers: body === undefined ? {} : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error("Backend nicht erreichbar");
  }

  if (!res.ok) {
    let message = `Fehler ${res.status}`;
    try {
      const { detail } = await res.json();
      message = typeof detail === "string"
        ? detail
        : detail.map(e => `${e.loc.slice(1).join(".")}: ${e.msg}`).join("; ");
    } catch { /* keine JSON-Antwort: Standardmeldung bleibt */ }
    throw new Error(message);
  }

  return res.status === 204 ? null : res.json();
}

export const api = {
  get: path => call("GET", path),
  post: (path, body) => call("POST", path, body ?? {}),
  del: path => call("DELETE", path),
};
