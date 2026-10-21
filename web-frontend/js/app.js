import { api } from "./api.js";

const $ = id => document.getElementById(id);
const enc = encodeURIComponent;
const POLL_MS = 5000;
const LABELS = { light: "Licht", doorsensor: "Türsensor", climatesensor: "Klimasensor", thermostat: "Thermostat" };

// ---------------------------------------------------------------
// Hilfsfunktionen
// ---------------------------------------------------------------

// Element bauen. Texte laufen über append(), nie über innerHTML.
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "value") continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (v != null && v !== false) el.setAttribute(k, v === true ? "" : v);
  }
  if ("value" in attrs) el.value = attrs.value; // erst nach min/max setzen
  el.append(...kids.flat().filter(k => k != null && k !== false));
  return el;
}

function toast(message, bad = false) {
  const t = h("div", { class: "toast" + (bad ? " bad" : "") }, message);
  $("toasts").append(t);
  setTimeout(() => t.remove(), 4000);
}

// Befehl senden, Fehler anzeigen, danach kurz warten und neu laden.
async function run(fn, okMessage) {
  try {
    await fn();
    if (okMessage) toast(okMessage);
  } catch (e) {
    toast(e.message, true);
  }
  setTimeout(refresh, 700);
}

// Sperrt das Überschreiben eines Reglers durch das Polling, solange der Nutzer ihn bedient.
function guard() {
  let until = 0;
  return { hold(ms = 3000) { until = Date.now() + ms; }, get held() { return Date.now() < until; } };
}

const debounce = (fn, ms) => { let t; return () => { clearTimeout(t); t = setTimeout(fn, ms); }; };
const num = (v, d = 1) => (typeof v === "number" ? v.toFixed(d) : "–");
const toHex = rgb => "#" + rgb.map(x => x.toString(16).padStart(2, "0")).join("");
const fromHex = hex => hex.slice(1).match(/../g).map(x => parseInt(x, 16));

function xyToRgb(x, y) {
  if (!y) return null;
  const X = x / y, Z = (1 - x - y) / y;
  const lin = [1.6565 * X - 0.3549 - 0.255 * Z, -0.7072 * X + 1.6554 + 0.0362 * Z, 0.0517 * X - 0.1214 + 1.0115 * Z];
  const max = Math.max(...lin, 1e-6);
  return lin.map(v => {
    v = Math.max(0, v) / max;
    v = v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055;
    return Math.round(v * 255);
  });
}

function colorToRgb(c) {
  if (!c) return null;
  if ("x" in c && "y" in c) return xyToRgb(c.x, c.y);
  if ("r" in c) return [c.r, c.g, c.b];
  return null;
}

// Favoritenfarben: nur in diesem Browser (localStorage)
const FAV_KEY = "smarthome.favoriteColors";
function getFavs() {
  try { return (JSON.parse(localStorage.getItem(FAV_KEY)) || []).filter(c => /^#[0-9a-f]{6}$/i.test(c)); }
  catch { return []; }
}
function setFavs(list) {
  try { localStorage.setItem(FAV_KEY, JSON.stringify(list)); } catch { /* Speicher gesperrt */ }
  window.dispatchEvent(new Event("favorites"));
}

// ---------------------------------------------------------------
// Bausteine für Kacheln
// ---------------------------------------------------------------

function frame(emoji, name, label) {
  const badge = h("span", { class: "badge" }, "…");
  const body = h("div", { class: "body" });
  const el = h("article", { class: "tile" },
    h("header", {},
      h("span", { class: "ic", "aria-hidden": "true" }, emoji),
      h("div", { class: "ttl" }, h("h3", { title: name }, name), h("small", {}, label)),
      badge,
      h("button", { class: "x", title: "Gerät entfernen", "aria-label": `${name} entfernen`, onClick: () => askDelete(name) }, "🗑")),
    body);
  return { el, body, status(text, kind = "") { badge.textContent = text; badge.className = "badge " + kind; } };
}

const row = (label, ...value) => h("div", { class: "row" }, h("span", {}, label), h("span", { class: "val" }, ...value));

function battery() {
  const fill = h("i"), text = h("span");
  const el = h("span", {}, h("span", { class: "bar" }, fill), text);
  return {
    el,
    set(percent, low) {
      fill.style.width = (percent ?? 0) + "%";
      text.textContent = (percent == null ? "–" : Math.round(percent) + " %") + (low ? " ⚠" : "");
      el.classList.toggle("low", Boolean(low) || (percent != null && percent < 20));
    },
  };
}

function slider(label, min, max, fmt, send) {
  const g = guard();
  const out = h("output", {}, "–");
  const input = h("input", {
    type: "range", min, max,
    onInput: () => { out.textContent = fmt(input.value); },
    onChange: () => { g.hold(); run(() => send(Number(input.value))); },
  });
  return {
    el: h("label", { class: "sl" }, h("span", { class: "row" }, label, out), input),
    set(v) {
      if (typeof v !== "number" || g.held || document.activeElement === input) return;
      input.value = v;
      out.textContent = fmt(v);
    },
  };
}

// ---------------------------------------------------------------
// Licht
// ---------------------------------------------------------------

function lightTile(d) {
  const n = d.name, f = frame("💡", n, "Licht"), gPower = guard();
  const L = (action, body) => api.post(`/lights/${enc(n)}/${action}`, body);

  const cur = h("span", { class: "cur", title: "Aktuelle Farbe" });
  const power = h("button", {
    class: "btn power",
    onClick: () => {
      const on = !f.el.classList.contains("on");
      f.el.classList.toggle("on", on);
      gPower.hold();
      run(() => L(on ? "turn_on" : "turn_off"));
    },
  }, "⏻ An / Aus");

  const brightness = slider("Helligkeit", 0, 254, v => Math.round(v / 254 * 100) + " %", v => L("brightness", { value: v }));
  const colorTemp = slider("Farbtemperatur", 153, 500, v => Math.round(1e6 / v) + " K", v => L("color_temp", { color_temp: v }));

  // Farbe: Colorpicker + RGB
  const pick = h("input", { type: "color", value: "#ffaa05", "aria-label": "Farbe wählen",
    onInput: () => fill(pick.value),
    onChange: () => run(() => L("color", { color: pick.value })) });
  const rgb = ["R", "G", "B"].map(c => h("input", { type: "number", min: 0, max: 255, value: 0, "aria-label": c,
    onInput: () => { pick.value = toHex(readRgb()); } }));
  const readRgb = () => rgb.map(i => Math.min(255, Math.max(0, Math.round(Number(i.value) || 0))));
  const fill = hex => fromHex(hex).forEach((v, k) => { rgb[k].value = v; });
  fill(pick.value);
  const setRgb = h("button", { class: "btn",
    onClick: () => { const v = readRgb(); pick.value = toHex(v); run(() => L("color", { color: v })); } }, "Setzen");

  // Favoriten
  const favBox = h("div", { class: "favs" });
  const drawFavs = () => favBox.replaceChildren(...getFavs().map(c => h("span", { class: "fav" },
    h("button", { class: "sw", style: `background:${c}`, title: c, "aria-label": `Favorit ${c} anwenden`,
      onClick: () => { pick.value = c; fill(c); run(() => L("color", { color: c })); } }),
    h("button", { class: "fx", title: "Favorit löschen", "aria-label": `Favorit ${c} löschen`,
      onClick: () => setFavs(getFavs().filter(x => x !== c)) }, "×"))));
  window.addEventListener("favorites", drawFavs);
  drawFavs();
  const saveFav = () => { const c = pick.value.toLowerCase(); if (!getFavs().includes(c)) setFavs([...getFavs(), c]); };

  // Timer
  const minutes = h("input", { type: "number", min: 1, value: 10, "aria-label": "Minuten" });
  const startTimer = () => run(() =>
    L("turn_on_with_timed_off", { seconds: Math.max(1, Math.round(Number(minutes.value) || 1)) * 60 }), "Timer gestartet");

  // Wecker
  const at = h("input", { type: "time", value: "07:00" });
  const ad = h("input", { type: "number", min: 1, value: 30 });
  const asb = h("input", { type: "number", min: 0, max: 254, value: 1 });
  const aeb = h("input", { type: "number", min: 0, max: 254, value: 254 });
  const ac = h("input", { type: "color", value: "#ffaa05" });
  const setAlarm = () => {
    if (!at.value) return toast("Bitte eine Uhrzeit wählen", true);
    const time = at.value.length === 5 ? at.value + ":00" : at.value;
    run(() => L("set_light_alarm", {
      start_time: time, duration: Number(ad.value),
      start_brightness: Number(asb.value), end_brightness: Number(aeb.value), color: ac.value,
    }), "Wecker gesetzt");
  };
  const fld = (label, input) => h("label", {}, label, input);

  f.body.append(
    h("div", { class: "row" }, power, cur),
    brightness.el, colorTemp.el,
    h("details", {}, h("summary", {}, "Farbe"), h("div", { class: "inner" },
      h("div", { class: "colors" }, pick, ...rgb, setRgb),
      h("div", { class: "favs-h" }, h("span", {}, "Favoriten"), h("button", { class: "btn sm", onClick: saveFav }, "★ Speichern")),
      favBox)),
    h("details", {}, h("summary", {}, "Timer (Auto-Aus)"), h("div", { class: "inner inline" },
      minutes, "Min.", h("button", { class: "btn", onClick: startTimer }, "Einschalten"))),
    h("details", {}, h("summary", {}, "Wecker"), h("div", { class: "inner" },
      h("div", { class: "fields" }, fld("Uhrzeit", at), fld("Dauer (Min.)", ad), fld("Start (0–254)", asb), fld("Ende (0–254)", aeb), fld("Farbe", ac)),
      h("div", { class: "inline inner" },
        h("button", { class: "btn primary", onClick: setAlarm }, "Wecker setzen"),
        h("button", { class: "btn", onClick: () => run(() => L("cancel_light_alarm"), "Wecker abgebrochen") }, "Abbrechen")))));

  return {
    el: f.el,
    off: () => window.removeEventListener("favorites", drawFavs),
    update(s) {
      f.status(s.is_on == null ? "Unbekannt" : s.is_on ? "An" : "Aus", s.is_on ? "ok" : "");
      if (!gPower.held) f.el.classList.toggle("on", s.is_on === true);
      brightness.set(s.brightness);
      colorTemp.set(s.color_temp);
      const c = colorToRgb(s.color);
      cur.style.background = c ? `rgb(${c})` : "transparent";
    },
  };
}

// ---------------------------------------------------------------
// Türsensor
// ---------------------------------------------------------------

function doorTile(d) {
  const f = frame("🚪", d.name, "Türsensor"), bat = battery();
  const state = h("div", { class: "big" }), tamper = h("span", { class: "val" }), volt = h("span");
  f.body.append(state, row("Manipulation", tamper), row("Batterie", bat.el), row("Spannung", volt));
  return {
    el: f.el,
    update(s) {
      const [text, kind] = s.closed == null ? ["Unbekannt", ""] : s.closed ? ["Geschlossen", "ok"] : ["Offen", "warn"];
      state.textContent = text;
      f.status(text, kind);
      // Annahme: true bedeutet "Manipulation erkannt"
      tamper.textContent = s.tamper_proof == null ? "–" : s.tamper_proof ? "Ausgelöst" : "OK";
      tamper.className = "val " + (s.tamper_proof ? "bad" : s.tamper_proof === false ? "ok" : "");
      bat.set(s.battery, s.battery_low);
      volt.textContent = typeof s.voltage === "number" ? (s.voltage / 1000).toFixed(2) + " V" : "–";
    },
  };
}

// ---------------------------------------------------------------
// Klimasensor
// ---------------------------------------------------------------

function climateTile(d) {
  const f = frame("🌡️", d.name, "Klimasensor"), bat = battery();
  const temp = h("div", { class: "big" }), hum = h("span");
  f.body.append(temp, row("Luftfeuchtigkeit", hum), row("Batterie", bat.el));
  return {
    el: f.el,
    update(s) {
      f.status(s.temperature == null ? "Keine Daten" : "OK", s.temperature == null ? "" : "ok");
      temp.textContent = typeof s.temperature === "number" ? num(s.temperature) + " °C" : "–";
      hum.textContent = typeof s.humidity === "number" ? num(s.humidity) + " %" : "–";
      bat.set(s.battery);
    },
  };
}

// ---------------------------------------------------------------
// Thermostat (wird später erweitert: weitere Einstellungen als <details> unter body)
// ---------------------------------------------------------------

function thermostatTile(d) {
  const n = d.name, f = frame("🔥", n, "Thermostat"), bat = battery();
  const gMode = guard(), gTarget = guard();
  const T = (action, body) => api.post(`/thermostats/${enc(n)}/${action}`, body);

  const current = h("div", { class: "big" });
  const modeButtons = [["off", "Aus"], ["auto", "Auto"], ["heat", "Heizen"]].map(([mode, text]) =>
    h("button", { class: "seg", "data-mode": mode,
      onClick: () => { gMode.hold(); markMode(mode); run(() => T("system_mode", { mode })); } }, text));
  const markMode = mode => modeButtons.forEach(b => b.classList.toggle("on", b.dataset.mode === mode));

  let target = null;
  const out = h("output", {}, "–");
  const showTarget = () => { out.textContent = target == null ? "–" : target.toFixed(1) + " °C"; };
  const send = debounce(() => run(() => T("heating_setpoint", { value: target })), 600);
  const step = delta => {
    target = Math.min(35, Math.max(4, (target ?? 20) + delta));
    showTarget();
    gTarget.hold(5000);
    send();
  };

  f.body.append(
    row("Aktuell", current),
    h("div", { class: "seg-group" }, ...modeButtons),
    h("div", { class: "setpoint" },
      h("button", { class: "btn", "aria-label": "Zieltemperatur senken", onClick: () => step(-0.5) }, "−"),
      out,
      h("button", { class: "btn", "aria-label": "Zieltemperatur erhöhen", onClick: () => step(0.5) }, "+")),
    row("Batterie", bat.el));

  return {
    el: f.el,
    update(s) {
      current.textContent = typeof s.local_temperature === "number" ? num(s.local_temperature) + " °C" : "–";
      if (s.running_state === "heat") f.status("Heizt", "hot");
      else if (s.system_mode === "off") f.status("Aus");
      else f.status(s.running_state ? "Bereit" : "Unbekannt");
      if (!gMode.held) markMode(s.system_mode);
      if (!gTarget.held) { target = s.occupied_heating_setpoint ?? null; showTarget(); }
      bat.set(s.battery);
    },
  };
}

// ---------------------------------------------------------------
// Laden und Rendern
// ---------------------------------------------------------------

const SOURCES = [
  ["light", "/lights", lightTile],
  ["doorsensor", "/sensors/doorSensors", doorTile],
  ["climatesensor", "/sensors/climateSensors", climateTile],
  ["thermostat", "/thermostats", thermostatTile],
];
const tiles = new Map(); // Gerätename -> Kachel
let loading = false;

// Einziger Einstiegspunkt für neue Daten. Beim Umstieg auf SSE ruft das Event applyState auf.
function applyState(index, devices) {
  const [type, , make] = SOURCES[index], seen = new Set();
  for (const d of devices) {
    seen.add(d.name);
    let tile = tiles.get(d.name);
    if (!tile) {
      tile = make(d);
      tile.type = type;
      tiles.set(d.name, tile);
      $("grid").append(tile.el);
    }
    tile.update(d);
  }
  for (const [name, tile] of tiles) {
    if (tile.type === type && !seen.has(name)) {
      tile.off?.();
      tile.el.remove();
      tiles.delete(name);
    }
  }
}

async function refresh() {
  if (loading) return;
  loading = true;
  const results = await Promise.allSettled(SOURCES.map(s => api.get(s[1])));
  let ok = 0;
  results.forEach((r, i) => { if (r.status === "fulfilled") { ok++; applyState(i, r.value); } });
  $("status").textContent = ok ? "Aktualisiert " + new Date().toLocaleTimeString("de-DE") : "Keine Verbindung zum Backend";
  $("status").classList.toggle("bad", !ok);
  $("empty").hidden = tiles.size > 0 || !ok;
  loading = false;
}

let timer;
const startPolling = () => { clearInterval(timer); timer = setInterval(refresh, POLL_MS); };
document.addEventListener("visibilitychange", () => {
  if (document.hidden) clearInterval(timer);
  else { refresh(); startPolling(); }
});

// ---------------------------------------------------------------
// Gerät löschen / hinzufügen
// ---------------------------------------------------------------

function askDelete(name) {
  $("del-name").textContent = name;
  $("del-dialog").returnValue = "";
  $("del-dialog").showModal();
}

$("del-dialog").addEventListener("close", e => {
  if (e.target.returnValue !== "ok") return;
  const name = $("del-name").textContent;
  run(() => api.del(`/remove_device?name=${enc(name)}`), "Gerät entfernt");
});

$("add-btn").addEventListener("click", async () => {
  $("add-error").hidden = true;
  $("add-name").value = "";
  if (!$("add-type").options.length) {
    let types;
    try { types = await api.get("/get_device_types"); }
    catch { types = Object.keys(LABELS); }
    $("add-type").replaceChildren(...types.map(t => h("option", { value: t }, LABELS[t] || t)));
  }
  $("add-dialog").showModal();
  $("add-name").focus();
});

$("add-cancel").addEventListener("click", () => $("add-dialog").close());

$("add-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    await api.post("/add_device", { name: $("add-name").value.trim(), type: $("add-type").value });
    $("add-dialog").close();
    toast("Gerät hinzugefügt");
    refresh();
  } catch (err) {
    $("add-error").textContent = err.message;
    $("add-error").hidden = false;
  }
});

refresh();
startPolling();
