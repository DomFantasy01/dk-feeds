/* Dark Knight Live - rebuilt Nov 4-5 2026 after the old page was lost. Nov 5: needs-you panel, alert preview + finder, deadline chips, deep links, keys. Source of truth: dk-feeds/live_page/dark_knight_live.html */
"use strict";
const KEYS = ["MOST", "WINNERS", "HERS&HIS", "NEXTDOOR"];
const DK = {MOST: "DK1", WINNERS: "DK2", "HERS&HIS": "DK3", NEXTDOOR: "DK4"};
const DKP = {MOST: "DK I", WINNERS: "DK II", "HERS&HIS": "DK III", NEXTDOOR: "DK IV"};          /* printed form, as the alerts carry it */
const LGN = {MOST: "Most Important", WINNERS: "Winners Sinners", "HERS&HIS": "Hers His Ver 2.0", NEXTDOOR: "Murrieta NextDoor"};
const LCOL = {MOST: "var(--l1)", WINNERS: "var(--l2)", "HERS&HIS": "var(--l3)", NEXTDOOR: "var(--l4)"};
const HEX = {MOST: "#5B9BF5", WINNERS: "#F0763A", "HERS&HIS": "#A98BFF", NEXTDOOR: "#4FD6CA"};
const SLUG = {MOST: "dk1", WINNERS: "dk2", "HERS&HIS": "dk3", NEXTDOOR: "dk4"};
const BYPRINT = {"DK I": "MOST", "DK II": "WINNERS", "DK III": "HERS&HIS", "DK IV": "NEXTDOOR"};
const LIVE_SYNC_TASK = "trig_014As1cm2kT6H6bXFSbQvJL6";   /* Refresh = pull the latest Dispatch build into this page */
const RSRV = "Claude Code Remote";

let S = null, M = null, A = null, MK = {}, H = null, TR = null, MV = null, DB = null;
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const f1 = (v) => (v === null || v === undefined || isNaN(v)) ? "–" : Number(v).toFixed(1);
const pc = (v) => (v === null || v === undefined || isNaN(v)) ? "–" : Math.round(v * 100) + "%";
const pcs = (v) => (v === null || v === undefined || isNaN(v)) ? "–" : (v * 100 < 1 && v > 0 ? "<1%" : Math.round(v * 100) + "%");
const sgn = (v, d = 1) => (v > 0 ? "+" : v < 0 ? "−" : "±") + Math.abs(v).toFixed(d);
const norm = (n) => (n || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[.']/g, "").replace(/-/g, " ").trim()
  .replace(/\s+(jr|sr|ii|iii|iv|v)\.?$/i, "").toLowerCase().split(/\s+/).join(" ");
const store = {get(k, d){ try { const v = localStorage.getItem("dkl:" + k); return v === null ? d : JSON.parse(v); } catch(_){ return d; } },
               set(k, v){ try { localStorage.setItem("dkl:" + k, JSON.stringify(v)); } catch(_){} }};
const PT = (iso, o) => { try { return new Date(iso).toLocaleString("en-US", {timeZone: "America/Los_Angeles", ...o}); } catch(_){ return ""; } };
const ptTime = (iso) => PT(iso, {weekday: "short", hour: "numeric", minute: "2-digit"});
const ago = (iso) => { const m = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (!(m >= 0)) return ""; if (m < 1) return "just now"; if (m < 60) return m + " min ago"; const h = Math.floor(m / 60);
  if (h < 24) return h + " hr" + (m % 60 >= 30 && h < 6 ? " " + (m % 60) + " min" : "") + " ago"; const d = Math.floor(h / 24); return d + (d === 1 ? " day" : " days") + " ago"; };
const SMOOTH = () => { try { return matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"; } catch(_){ return "auto"; } };
const dueMin = (iso) => (new Date(iso).getTime() - Date.now()) / 6e4;
const DUE = (iso) => { const m = Math.round(dueMin(iso)); if (!(m > 0)) return "now"; const d = Math.floor(m / 1440), h = Math.floor(m % 1440 / 60), mi = m % 60;
  return d ? d + "d " + h + "h" : h ? h + "h " + mi + "m" : mi + "m"; };
const KEYOF = {dk1: "MOST", dk2: "WINNERS", dk3: "HERS&HIS", dk4: "NEXTDOOR"};
const lgS = (k) => S && S.leagues ? S.leagues.find(L => L.key === k) : null;
const lgM = (k) => (M && M.leagues && M.leagues[k]) || {};

/* ---------- game state of a man ---------- */
const isDone = (p) => /^(Fin|Final|Bye|No game)/i.test((p.when || "").trim());
const isLive = (p) => !isDone(p) && /(1st|2nd|3rd|4th|Half|OT|End|Q\d)/i.test(p.when || "");
const isOut = (p) => /^(O|IR|IR-R|NA|SUSP|PUP|COV)$/i.test((p.status || "").trim());
const pts = (p) => (p.actual === null || p.actual === undefined) ? 0 : +p.actual;
const started = (p) => isDone(p) || isLive(p);
/* each source's projected final for one man: Yahoo's live projection, or the expert's number (pm: [Ratcliffe, Clay, Koerner, Vegas]) */
const SRCI = {r: 0, c: 1, k: 2, v: 3};   /* Nov 7 (Dom): v = Vegas props */
function manFinal(p, src, pm){
  if (isDone(p)) return pts(p);
  if (isOut(p)) return pts(p);
  if (src === "y") return Math.max(pts(p), +p.proj || 0);
  const e = pm && pm[norm(p.name)] ? pm[norm(p.name)][SRCI[src]] : null;
  const base = (e === null || e === undefined) ? (+p.proj || 0) : +e;
  return isLive(p) ? pts(p) + Math.max(0, base - pts(p)) : base;
}
const phi = (z) => { const t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2);
  const q = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return z > 0 ? 1 - q : q; };
function chance(L, src){
  const pm = (M && M.pm && M.pm[L.key]) || {};
  const anyStarted = [...L.players, ...L.oppPlayers].some(started);
  if (!anyStarted && src !== "y"){
    const set = (M && M.best && M.best[L.key] && M.best[L.key].set) || {};
    const v = src === "r" ? set.ratcliffe : src === "k" ? set.koerner : src === "v" ? set.vegas : (set.clay ?? set.gotham);   /* the build's best-lineup number, both sides */
    if (v !== null && v !== undefined) return +v;
  }
  if (src === "y") return +L.pct;
  const me = L.players.reduce((a, p) => a + manFinal(p, src, pm), 0), op = L.oppPlayers.reduce((a, p) => a + manFinal(p, src, pm), 0);
  const remain = [...L.players, ...L.oppPlayers].reduce((a, p) => a + (isDone(p) || isOut(p) ? 0 : Math.max(0, manFinal(p, src, pm) - pts(p))), 0);
  const full = [...L.players, ...L.oppPlayers].reduce((a, p) => a + Math.max(1, manFinal(p, src, pm)), 0) || 1;
  const sd = Math.max(1.5, 30 * Math.sqrt(Math.min(1, remain / full)));   /* the spread shrinks as the week is played */
  if (remain < .05) return me > op ? 100 : me < op ? 0 : 50;
  return Math.round(phi((me - op) / sd) * 100);
}
const finals = (L) => ({me: L.players.reduce((a, p) => a + manFinal(p, "y"), 0), op: L.oppPlayers.reduce((a, p) => a + manFinal(p, "y"), 0)});
const score = (list) => list.reduce((a, p) => a + pts(p), 0);
const emptySeats = (L) => L.players.filter(p => !isDone(p) && (isOut(p) || /^D$/i.test(p.status || "") || ((+p.proj || 0) === 0 && !isLive(p))));
const leftOf = (list) => list.filter(p => !isDone(p) && !isOut(p));
const settled = (L) => leftOf(L.players).length === 0 && leftOf(L.oppPlayers).length === 0;
function verdict(m){ const a = Math.abs(m);
  if (m >= 0) return a <= 3 ? "SURVIVED" : a <= 15 ? "WON" : a <= 40 ? "WON BIG" : "ROUT";
  return a <= 3 ? "ROBBED" : a <= 15 ? "LOST" : a <= 40 ? "BEATEN" : "BLOWN OUT"; }

/* ---------- alerts ---------- */
const AL_ORD = {red: 0, gold: 1, grey: 2, green: 3};
const AL_TAG = {red: "ACT NOW", gold: "MONITOR", grey: "NOTED", green: "RESOLVED"};
const WEEK = 7 * 864e5;
const mk = (id) => MK[id] || {};
function alertsAll(){ return (A && A.items) || []; }
function aLive(x){ const m = mk(x.id); if (m.deleted || m.cleared) return false;
  if (Date.now() - new Date(x.first_seen).getTime() > WEEK) return false; return x.active !== false || x.color === "green"; }
function aSep(x){ const m = mk(x.id); return !m.deleted && m.cleared && Date.now() - new Date(m.cleared).getTime() <= WEEK; }
const aSort = (a, b) => (AL_ORD[a.color] - AL_ORD[b.color]) || (new Date(b.first_seen) - new Date(a.first_seen));
const aFor = (k, fn) => alertsAll().filter(x => BYPRINT[x.lg] === k && fn(x)).sort(aSort);
function worst(list){ return list.length ? list.slice().sort(aSort)[0].color : "none"; }
async function writeMarks(up){
  Object.assign(MK, up); renderAlertsOnly();
  if (!DB) return;
  try { await DB.doc("live/alert_marks").update(up); }
  catch(_){ try { await DB.doc("live/alert_marks").set(Object.assign({}, MK)); } catch(__){ rmsg("Couldn't save that on the page's database - it will come back on the next load.", 1); } }
}
let ARM = null, ARMT = null;
function armed(id){ if (ARM === id){ ARM = null; clearTimeout(ARMT); return true; }
  ARM = id; clearTimeout(ARMT); ARMT = setTimeout(() => { ARM = null; renderAll(); }, 5000); renderAll(); return false; }
const OPEN = new Set(), SHOWNOTED = new Set();

function alertCard(x, sep){
  const m = mk(x.id), op = OPEN.has(x.id), d = Math.floor((Date.now() - new Date(x.first_seen).getTime()) / 864e5);
  const age = d >= 1 ? d + (d === 1 ? " DAY" : " DAYS") : "NEW";
  return `<div class="al ${x.color}${m.read ? " read" : ""}${op ? " open" : ""}" data-aid="${esc(x.id)}" tabindex="0" role="button" aria-expanded="${op}">
    <div class="row"><div class="tag">${AL_TAG[x.color] || "NOTED"}</div>
      <div class="main"><div class="w"><span class="age">${age}</span>${esc(PT(x.first_seen, {month: "short", day: "numeric", hour: "numeric", minute: "2-digit"}))}${x.deadline_utc && dueMin(x.deadline_utc) > 0 ? `<span class="dl${dueMin(x.deadline_utc) < 180 ? " hot" : ""}">${DUE(x.deadline_utc)} LEFT</span>` : ""}</div><div class="t">${esc(x.title)}</div><div class="w">${esc(x.own || "")}${x.by ? " · " + esc(x.by) : ""}</div></div></div>
    <div class="b">${x.tie ? `<p><b>What it means:</b> ${esc(x.tie)}</p>` : ""}${x.fix ? `<p><b>Next:</b> ${esc(x.fix)}</p>` : ""}
      ${(x.receipts || []).length ? `<ul>${x.receipts.map(r => `<li>${esc(r)}</li>`).join("")}</ul>` : ""}
      <p class="note">Source: ${esc(x.src || "the Dispatch build")}${x.feed ? " · " + esc(x.feed) : ""} · built ${esc(x.built || "")}</p>
      <div class="acts"><button type="button" class="del" data-ado="del">Delete</button>${sep ? "" : `<button type="button" data-ado="sep">Separate</button>`}<button type="button" data-ado="close">Close</button></div></div>
  </div>`;
}
function alertsBlock(k){
  const list = aFor(k, aLive); if (!list.length) return `<div class="empty">No open alerts in ${DK[k]}.</div>`;
  const loud = list.filter(x => x.color !== "grey"), quiet = list.filter(x => x.color === "grey");
  const cnt = (c) => list.filter(x => x.color === c).length;
  return `<div class="ahd"><span class="tal">${cnt("red")} act now · ${cnt("gold")} monitor · ${cnt("grey")} noted</span>
    <button type="button" class="abtn${ARM === "del:" + k ? " arm" : ""}" data-abulk="del:${k}">${ARM === "del:" + k ? "Tap again to delete " + list.length : "Delete all"}</button>
    <button type="button" class="abtn sep${ARM === "sep:" + k ? " arm" : ""}" data-abulk="sep:${k}">${ARM === "sep:" + k ? "Tap again to separate " + list.length : "Separate all"}</button></div>
    <div class="alist">${loud.map(x => alertCard(x)).join("")}
    ${quiet.length ? (SHOWNOTED.has(k) ? quiet.map(x => alertCard(x)).join("") + `<button type="button" class="amore" data-noted="${k}">Hide the ${quiet.length} noted</button>`
       : `<button type="button" class="amore" data-noted="${k}">Show ${quiet.length} noted (under the 2-point line, opponents, bench news)</button>`) : ""}</div>`;
}

/* ---------- clearing a league's other items until something real changes ---------- */
const xmk = (id) => MK["x:" + id] || null;
const shown = (id, sig) => { const c = xmk(id); return !c || c.sig !== sig; };
const sigMove = (m) => `${m.drop}|${Math.round((m.d_playoff || 0) * 100 / 3)}|${(m.d_playoff || 0) >= .25}`;
const sigCall = (c) => `${c.status}`;
const sigTrade = (t) => `${(t.give || []).join("+")}>${t.get}|${Math.round((t.d_playoff || 0) * 100 / 3)}`;
const moveId = (k, m) => `mv:${k}:${m.add}`, callId = (k, c) => `call:${k}:${c.starter}`, tradeId = (k, t) => `tr:${k}:${t.get}`;

/* ---------- the trail: one entry per Yahoo read, written by the page ---------- */
function trailEntries(){ return (TR && TR.entries) || []; }
function snap(){
  if (!S || !S.leagues) return null;
  const e = {t: S.stamp, w: S.week, lg: {}};
  for (const L of S.leagues){
    const pl = {}; for (const p of [...L.players, ...L.oppPlayers]) pl[p.name] = Math.round(pts(p) * 100) / 100;
    e.lg[L.key] = {y: chance(L, "y"), r: chance(L, "r"), k: chance(L, "k"), c: chance(L, "c"), v: chance(L, "v"), me: +score(L.players).toFixed(2), op: +score(L.oppPlayers).toFixed(2), pl};
  }
  return e;
}
let trailBusy = false;
async function trailAdd(){
  if (!DB || !S || trailBusy || !TR) return;
  const es = trailEntries(); if (es.length && es[es.length - 1].t >= S.stamp) return;
  const e = snap(); if (!e) return;
  const next = es.concat([e]).slice(-160).map((x, i, arr) => i < arr.length - 3 ? {...x, lg: Object.fromEntries(Object.entries(x.lg).map(([k, v]) => [k, {...v, pl: undefined}]))} : x);
  trailBusy = true;
  try { await DB.doc("live/trail").set({entries: JSON.parse(JSON.stringify(next))}); TR = {entries: next}; }
  catch(_){} finally { trailBusy = false; }
}
/* the week's first read (Dom, Nov 5: "where we started to where we are now") */
function weekStart(k, src){ const w0 = M && M.wk0; if (w0 && S && w0.week === S.week && w0.lg && w0.lg[k] && w0.lg[k][src] !== null && w0.lg[k][src] !== undefined) return w0.lg[k][src];
  const e = trailEntries().find(e => S && e.w === S.week && e.lg[k] && e.lg[k][src] !== undefined && e.lg[k][src] !== null); return e ? e.lg[k][src] : null; }
function prevEntry(){ const es = trailEntries().filter(e => S && e.t < S.stamp && e.w === S.week); return es.length ? es[es.length - 1] : null; }

/* ---------- small charts ---------- */
function dial(v, col, id, v0){
  /* Nov 5 v2: the Yahoo needle - graded arc (red-amber-green behind a league-colored fill), 10-point ticks, glowing needle */
  v = Math.max(0, Math.min(100, +v || 0));
  const cx = 60, cy = 54, r = 44, A = (p) => Math.PI * (1 - p), P = (p, rr) => [cx + rr * Math.cos(A(p)), cy - rr * Math.sin(A(p))];
  const arc = (p0, p1, rr) => { const [x0, y0] = P(p0, rr), [x1, y1] = P(p1, rr); return `M${x0.toFixed(1)} ${y0.toFixed(1)} A${rr} ${rr} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`; };
  let ticks = ""; for (let t = 0; t <= 10; t++){ const [a0, b0] = P(t / 10, r + 6), [a1, b1] = P(t / 10, r + (t % 5 ? 9 : 11)); ticks += `<line x1="${a0.toFixed(1)}" y1="${b0.toFixed(1)}" x2="${a1.toFixed(1)}" y2="${b1.toFixed(1)}" stroke="${t === 5 ? "#C9CFDB" : "#3A4A6E"}" stroke-width="${t % 5 ? 1 : 1.6}"/>`; }
  const [nx, ny] = P(v / 100, r - 4), g = "g" + (id || "x");
  let ghost = ""; if (v0 !== null && v0 !== undefined && !isNaN(v0) && Math.round(v0) !== Math.round(v)){ const w0 = Math.max(0, Math.min(100, v0)), [gx, gy] = P(w0 / 100, r - 4), up = v > w0;
    ghost = `<path d="${arc(Math.min(w0, v) / 100, Math.max(w0, v) / 100, r + 9)}" stroke="${up ? "#4FD08A" : "#FF6B72"}" stroke-width="2.4" fill="none" stroke-linecap="round"/>
      <line x1="${cx}" y1="${cy}" x2="${gx.toFixed(1)}" y2="${gy.toFixed(1)}" stroke="#C9CFDB" stroke-width="1.6" stroke-dasharray="2.5 2.5" opacity=".75"/><circle cx="${gx.toFixed(1)}" cy="${gy.toFixed(1)}" r="2.6" fill="#0B1222" stroke="#C9CFDB" stroke-width="1.2"/>`; }
  return `<svg viewBox="0 0 120 64" aria-hidden="true"><defs><linearGradient id="${g}" x1="0" x2="1"><stop offset="0" stop-color="#FF4D57"/><stop offset=".5" stop-color="#F7B32B"/><stop offset="1" stop-color="#4FD08A"/></linearGradient>
    <filter id="${g}f" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>${ticks}
    <path d="${arc(0, 1, r)}" stroke="url(#${g})" stroke-opacity=".22" stroke-width="10" fill="none"/>
    <path d="${arc(0, Math.max(.01, v / 100), r)}" stroke="${col}" stroke-width="10" fill="none" stroke-linecap="round"/>${ghost}
    <line x1="${cx}" y1="${cy}" x2="${nx.toFixed(1)}" y2="${ny.toFixed(1)}" stroke="${col}" stroke-width="5" stroke-linecap="round" opacity=".55" filter="url(#${g}f)"/>
    <line x1="${cx}" y1="${cy}" x2="${nx.toFixed(1)}" y2="${ny.toFixed(1)}" stroke="#F4F6FA" stroke-width="2.2" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="4.5" fill="#F4F6FA"/><circle cx="${cx}" cy="${cy}" r="2" fill="${col}"/></svg>`;
}
/* Nov 7 (Dom: "a little round looking glass with the numbers in there ... showing up or down ... make it look creatively excellent"):
   one glass orb per source, stacked top to bottom under the Yahoo dial, Vegas first. The bezel ring fills clockwise to the chance
   and takes its color from the red-amber-green scale; a small dot on the bezel marks where the week started; the number sits
   behind a glass sheen; the week's change rides beside it. */
const heat = (v) => { v = Math.max(0, Math.min(100, +v || 0)); const L = (a, b, t) => Math.round(a + (b - a) * t);
  const [c0, c1, t] = v < 50 ? [[255, 77, 87], [247, 179, 43], v / 50] : [[247, 179, 43], [79, 208, 138], (v - 50) / 50];
  return `rgb(${L(c0[0], c1[0], t)},${L(c0[1], c1[1], t)},${L(c0[2], c1[2], t)})`; };
function glassOrb(v, v0, tint, id, gold){
  v = Math.max(0, Math.min(100, +v || 0)); const c = 18, r = 15.2, C = 2 * Math.PI * r, col = heat(v), g = "o" + id;
  let dot = ""; if (v0 !== null && v0 !== undefined && !isNaN(v0)){ const a = (Math.max(0, Math.min(100, v0)) / 100) * 2 * Math.PI - Math.PI / 2;
    dot = `<circle cx="${(c + r * Math.cos(a)).toFixed(2)}" cy="${(c + r * Math.sin(a)).toFixed(2)}" r="1.9" fill="#0B1222" stroke="#EEF1F6" stroke-width=".9"/>`; }
  return `<svg viewBox="0 0 36 36" aria-hidden="true"><defs>
    <radialGradient id="${g}b" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="${tint}" stop-opacity=".55"/><stop offset=".55" stop-color="#14203A"/><stop offset="1" stop-color="#070C18"/></radialGradient>
    <linearGradient id="${g}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="${g}f" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.3"/></filter></defs>
    ${gold ? `<circle cx="${c}" cy="${c}" r="17.3" fill="none" stroke="#EFD23E" stroke-opacity=".45" stroke-width=".8"/>` : ""}
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#1C2A48" stroke-width="2.8"/>
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${col}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="${(C * v / 100).toFixed(2)} ${C.toFixed(2)}" transform="rotate(-90 ${c} ${c})" opacity=".55" filter="url(#${g}f)"/>
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${col}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="${(C * v / 100).toFixed(2)} ${C.toFixed(2)}" transform="rotate(-90 ${c} ${c})"/>${dot}
    <circle cx="${c}" cy="${c}" r="12.4" fill="url(#${g}b)" stroke="rgba(255,255,255,.16)" stroke-width=".7"/>
    <text x="${c}" y="${c + 4.6}" text-anchor="middle" font-family="Bebas Neue,Arial Narrow,sans-serif" font-size="13.5" fill="#fff" letter-spacing=".3">${Math.round(v)}</text>
    <ellipse cx="${c - 2.6}" cy="${c - 6.4}" rx="7.6" ry="3.9" fill="url(#${g}s)"/>
    <path d="M${c - 7.5} ${c + 6.5} Q${c} ${c + 10.6} ${c + 7.5} ${c + 6.5}" stroke="${tint}" stroke-opacity=".5" stroke-width=".8" fill="none"/></svg>`;
}
/* a small expert needle: half arc, number underneath */
function miniDial(v, col, v0){
  v = Math.max(0, Math.min(100, +v || 0)); const cx = 20, cy = 19, r = 15, A = Math.PI * (1 - v / 100);
  let ghost = ""; if (v0 !== null && v0 !== undefined && !isNaN(v0) && Math.round(v0) !== Math.round(v)){ const B = Math.PI * (1 - Math.max(0, Math.min(100, v0)) / 100);
    ghost = `<line x1="${cx}" y1="${cy}" x2="${(cx + (r - 2) * Math.cos(B)).toFixed(1)}" y2="${(cy - (r - 2) * Math.sin(B)).toFixed(1)}" stroke="#C9CFDB" stroke-width="1.1" stroke-dasharray="1.6 1.6" opacity=".8"/>`; }
  const x1 = cx + r * Math.cos(A), y1 = cy - r * Math.sin(A);
  return `<svg viewBox="0 0 40 22" aria-hidden="true"><path d="M5 19 A15 15 0 0 1 35 19" stroke="#26365A" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path d="M5 19 A15 15 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}" stroke="${col}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <line x1="${cx}" y1="${cy}" x2="${(cx + (r - 3) * Math.cos(A)).toFixed(1)}" y2="${(cy - (r - 3) * Math.sin(A)).toFixed(1)}" stroke="#EEF1F6" stroke-width="1.4" stroke-linecap="round"/>${ghost}<circle cx="${cx}" cy="${cy}" r="2" fill="#EEF1F6"/></svg>`;
}
/* sparkline of the Yahoo chance read by read this week; 50% line dashed, last point marked */
function spark(vals, col){
  const P = vals.filter(v => v !== null && v !== undefined && !isNaN(v)); if (P.length < 2) return "";
  const W = 100, H = 22, X = (i) => 2 + (W - 4) * i / (P.length - 1), Y = (v) => 2 + (H - 4) * (1 - v / 100);
  const pts = P.map((v, i) => X(i).toFixed(1) + "," + Y(v).toFixed(1)).join(" ");
  return `<svg class="spk" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"><line x1="2" x2="${W - 2}" y1="${Y(50)}" y2="${Y(50)}" stroke="#3A4A6E" stroke-dasharray="2 2" stroke-width="1" vector-effect="non-scaling-stroke"/>
    <polygon points="2,${H - 2} ${pts} ${X(P.length - 1).toFixed(1)},${H - 2}" fill="${col}" opacity=".18"/><polyline points="${pts}" fill="none" stroke="${col}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>
    <circle cx="${X(P.length - 1).toFixed(1)}" cy="${Y(P[P.length - 1]).toFixed(1)}" r="2.2" fill="#fff"/></svg>`;
}
const bellSvg = `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5c-2.5 0-4.2 2-4.2 4.4v2.6L2.5 11h11l-1.3-2.5V5.9C12.2 3.5 10.5 1.5 8 1.5Z" fill="currentColor"/><path d="M6.3 12.3a1.8 1.8 0 0 0 3.4 0" stroke="currentColor" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg>`;
/* a line chart, 0-100 on Y, any number of series [{pts:[[x,y]], col, dash}] over x labels */
function lineChart(series, xlabels, h = 110){
  const W = 340, Ht = h, pl = 26, pr = 8, pt = 8, pb = 18, n = Math.max(2, xlabels.length);
  const X = (i) => pl + (W - pl - pr) * (n === 1 ? 0 : i / (n - 1)), Y = (v) => pt + (Ht - pt - pb) * (1 - v / 100);
  let g = "";
  for (const v of [0, 50, 100]) g += `<line x1="${pl}" x2="${W - pr}" y1="${Y(v)}" y2="${Y(v)}" stroke="${v === 50 ? "#3A4A6E" : "#1F2E50"}" stroke-width="1" ${v === 50 ? 'stroke-dasharray="3 3"' : ""}/><text x="${pl - 4}" y="${Y(v) + 3}" font-size="8.5" text-anchor="end" fill="#8A93A6" font-family="IBM Plex Mono,monospace">${v}</text>`;
  const step = Math.max(1, Math.ceil(n / 6));
  xlabels.forEach((t, i) => { if (i % step === 0 || i === n - 1) g += `<text x="${X(i)}" y="${Ht - 4}" font-size="8" text-anchor="middle" fill="#8A93A6" font-family="Poppins,sans-serif">${esc(t)}</text>`; });
  for (const s of series){
    const P = s.pts.filter(p => p[1] !== null && p[1] !== undefined && !isNaN(p[1]));
    if (!P.length) continue;
    g += `<polyline fill="none" stroke="${s.col}" stroke-width="${s.w || 2}" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""} stroke-linejoin="round" points="${P.map(p => X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1)).join(" ")}"/>`;
    const L = P[P.length - 1]; g += `<circle cx="${X(L[0]).toFixed(1)}" cy="${Y(L[1]).toFixed(1)}" r="3" fill="${s.col}"/>`;
  }
  return `<svg viewBox="0 0 ${W} ${Ht}" role="img">${g}</svg>`;
}
/* WEEKLY PROGRESS (Nov 5 v10, Dom: "it's not win probability once the games start... it's about progress in the games").
   Modeled on the Dispatch overview's mountains. The frame never moves: kickoff windows across the bottom, one fixed height.
   Each window is a triangle peak as tall as the points scored in it (yours in the league color, the opponent's silver);
   windows still to come show only as a faint outline. A gold NOW bar sweeps across the week. Under it, two fixed points
   tracks with a triangle marker at each side's actual points, then every game in this matchup with four quarter boxes
   that light up as quarters finish. No projections printed and no win chance - that lives on the meters. */
const QTXT = (t) => { t = String(t || "");
  if (/^(Fin|Final)/i.test(t)) return {done: 4, live: false};
  if (/OT/i.test(t)) return {done: 4, live: true};
  if (/Half/i.test(t)) return {done: 2, live: true};
  const e = /End\s*(?:of\s*)?(1st|2nd|3rd|4th|Q[1-4])/i.exec(t); if (e) return {done: {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, q1: 1, q2: 2, q3: 3, q4: 4}[e[1].toLowerCase()], live: true};
  const q = /(1st|2nd|3rd|4th|Q[1-4])/i.exec(t); if (q) return {done: {"1st": 0, "2nd": 1, "3rd": 2, "4th": 3, q1: 0, q2: 1, q3: 2, q4: 3}[q[1].toLowerCase()], live: true};
  return null; };
const TALIAS = {LAR: "LA", LA: "LAR", WSH: "WAS", WAS: "WSH", JAC: "JAX", JAX: "JAC", LV: "OAK", ARZ: "ARI", ARI: "ARZ"};
function wxOf(tm){ const T = (M && M.wx && M.wx.teams) || {}, t = (tm || "").toUpperCase(); return T[t] || T[TALIAS[t]] || null; }
function teamKo(tm){ const w = wxOf(tm); return w && w.ko ? new Date(w.ko).getTime() : null; }
function gameOf(tm){ const w = wxOf(tm); return w ? w.game : null; }
function windowsNow(){
  const ks = ((M && M.kicks) || []).map(x => new Date(Array.isArray(x) ? x[0] : x).getTime()).filter(t => !isNaN(t)).sort((a, b) => a - b);
  const lab = (M && M.windows) || ks.map(t => PT(new Date(t).toISOString(), {weekday: "short", hour: "numeric", minute: "2-digit"}).toUpperCase());
  return {ks, lab}; }
function winIdx(p, ks){
  const t = teamKo(p.tm); if (t !== null && ks.length){ let i = 0; ks.forEach((k, j) => { if (k <= t + 6e4) i = j; }); return i; }
  const lab = (M && M.windows) || [], r = whenRank(p.when); let i = -1; lab.forEach((l, j) => { if (whenRank(l) <= r) i = j; }); return i < 0 ? 0 : i; }
function gameState(game, ko){
  for (const k of KEYS){ const L = lgS(k); if (!L) continue;
    for (const p of [...L.players, ...L.oppPlayers]) if (gameOf(p.tm) === game){ const q = QTXT(p.when); if (q) return q; } }
  if (ko && Date.now() > ko + 3.4 * 36e5) return {done: 4, live: false, est: true};
  if (ko && Date.now() > ko){ const d = Math.min(3, Math.floor((Date.now() - ko) / (50 * 6e4))); return {done: d, live: true, est: true}; }
  return {done: 0, live: false}; }
function progress(L, k){
  const {ks, lab} = windowsNow(); const nW = Math.max(1, lab.length || ks.length);
  const me = score(L.players), op = score(L.oppPlayers), meL = leftOf(L.players).length, opL = leftOf(L.oppPlayers).length, col = HEX[k], id = gid();
  const sum = (list, fn) => { const a = Array(nW).fill(0); for (const p of list){ const i = Math.min(nW - 1, winIdx(p, ks)); a[i] += fn(p); } return a; };
  const playedA = sum(L.players, p => started(p) ? pts(p) : 0), playedB = sum(L.oppPlayers, p => started(p) ? pts(p) : 0);
  const fullA = sum(L.players, p => Math.max(0, started(p) ? pts(p) : manFinal(p, "y"))), fullB = sum(L.oppPlayers, p => Math.max(0, started(p) ? pts(p) : manFinal(p, "y")));
  const W = 340, H = 204, pl = 16, pr = 16, top = 50, base = 136, sp = (W - pl - pr) / Math.max(1, nW - 1), X = (i) => nW === 1 ? W / 2 : pl + i * sp, hw = Math.max(26, sp * .95);
  const sg = Math.max(14, sp * .4);   /* Nov 5 (Dom: "these are just pointed and they look stupid"): smooth hills, not triangles */
  const ridge = (arr) => { const n = 160, pts2 = []; for (let s2 = 0; s2 <= n; s2++){ const x = pl - 8 + (W - pl - pr + 16) * s2 / n; let v = 0; arr.forEach((h, i) => { v += h * Math.exp(-.5 * ((x - X(i)) / sg) ** 2); }); pts2.push([x, v]); } return pts2; };
  const peakOf = (arr) => Math.max(0, ...ridge(arr).map(q => q[1]));
  const yMax = Math.max(20, peakOf(fullA), peakOf(fullB), peakOf(playedA), peakOf(playedB)) * 1.1, Y = (v) => base - (base - top) * v / yMax;
  const area = (arr) => { const r = ridge(arr); return `M${r[0][0].toFixed(1)} ${base} ` + r.map(([x, v]) => `L${x.toFixed(1)} ${Y(v).toFixed(1)}`).join(" ") + ` L${r[r.length - 1][0].toFixed(1)} ${base} Z`; };
  const line = (arr) => ridge(arr).map(([x, v], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
  /* the NOW bar: where this moment sits among the kickoff windows */
  const now = Date.now(); let nx = pl - 8;
  if (ks.length){ if (now >= ks[ks.length - 1] + 3.4 * 36e5) nx = W - pr + 8; else if (now >= ks[0]){ let i = ks.findIndex((t, j) => now >= t && (j === ks.length - 1 || now < ks[j + 1]));
      const t0 = ks[i], t1 = i < ks.length - 1 ? ks[i + 1] : ks[i] + 3.4 * 36e5; nx = X(i) + (i < ks.length - 1 ? sp : 18) * Math.min(1, (now - t0) / (t1 - t0)); } }
  const mg = me - op, anyGo = [...L.players, ...L.oppPlayers].some(started);
  const tMax = Math.ceil(Math.max(60, finals(L).me, finals(L).op, me, op) * 1.15 / 20) * 20, TX = (v) => pl + (W - pl - pr) * Math.min(1, v / tMax);
  const track = (y, v, c, labTxt) => `<text x="${pl}" y="${y - 6}" font-size="8" font-weight="700" fill="${c}" font-family="Poppins,sans-serif" letter-spacing=".08em">${labTxt}</text>
    <rect x="${pl}" y="${y - 2.5}" width="${W - pl - pr}" height="5" rx="2.5" fill="#1C2A48"/><rect x="${pl}" y="${y - 2.5}" width="${Math.max(0, TX(v) - pl).toFixed(1)}" height="5" rx="2.5" fill="${c}"/>
    <path d="M${TX(v).toFixed(1)} ${y + 3} l-5 -9 h10 z" fill="${c}" stroke="#0B1222" stroke-width="1"/>`;
  let ax = ""; lab.forEach((t, i) => { const p2 = String(t).replace(/:00/, "").replace(/ (AM|PM)$/i, (m0) => m0.trim()[0].toLowerCase()); ax += `<text x="${X(i).toFixed(1)}" y="${base + 11}" text-anchor="${i === 0 ? "start" : i === nW - 1 ? "end" : "middle"}" font-size="7.6" fill="#8A93A6" font-family="Poppins,sans-serif">${esc(p2)}</text>`; });
  for (let v = 20; v < yMax; v += yMax > 90 ? 40 : 20) ax += `<line x1="${pl}" x2="${W - pr}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}" stroke="#17233F" stroke-dasharray="2 3"/><text x="${W - pr}" y="${(Y(v) - 2).toFixed(1)}" text-anchor="end" font-size="7" fill="#4F5B75" font-family="IBM Plex Mono,monospace">${v}</text>`;
  const svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(`You ${f1(me)} with ${meL} left, opponent ${f1(op)} with ${opL} left`)}">
    <defs><linearGradient id="${id}a" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity=".95"/><stop offset="1" stop-color="${col}" stop-opacity=".25"/></linearGradient>
      <linearGradient id="${id}b" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#C9CFDB" stop-opacity=".7"/><stop offset="1" stop-color="#C9CFDB" stop-opacity=".12"/></linearGradient>
      <linearGradient id="${id}fa" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity=".30"/><stop offset="1" stop-color="#16213A" stop-opacity=".2"/></linearGradient>
      <linearGradient id="${id}fb" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5C677D" stop-opacity=".45"/><stop offset="1" stop-color="#16213A" stop-opacity=".2"/></linearGradient>
      <linearGradient id="${id}sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${col}" stop-opacity="0"/><stop offset="1" stop-color="${col}" stop-opacity=".10"/></linearGradient>
      <filter id="${id}g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter></defs>
    <rect x="0" y="${top - 10}" width="${W}" height="${base - top + 10}" fill="url(#${id}sky)"/>
    <text x="${pl}" y="15" font-size="22" fill="${col}" font-family="Bebas Neue,Arial Narrow,sans-serif" letter-spacing=".03em">YOU ${f1(me)}</text>
    <text x="${pl}" y="27" font-size="8" fill="#C9CFDB" font-family="Poppins,sans-serif" font-weight="600">${meL} LEFT TO PLAY</text>
    <text x="${W - pr}" y="15" text-anchor="end" font-size="22" fill="#E3E7EF" font-family="Bebas Neue,Arial Narrow,sans-serif" letter-spacing=".03em">OPP ${f1(op)}</text>
    <text x="${W - pr}" y="27" text-anchor="end" font-size="8" fill="#C9CFDB" font-family="Poppins,sans-serif" font-weight="600">${opL} LEFT TO PLAY</text>
    <text x="${W / 2}" y="15" text-anchor="middle" font-size="15" fill="${!anyGo || Math.abs(mg) < .05 ? "#EFD23E" : mg > 0 ? "#4FD08A" : "#FF6B72"}" font-family="Bebas Neue,Arial Narrow,sans-serif" letter-spacing=".05em">${!anyGo || Math.abs(mg) < .05 ? "EVEN" : (mg > 0 ? "UP " : "DOWN ") + Math.abs(mg).toFixed(1)}</text>
    ${ax}<line x1="${pl - 8}" x2="${W - pr + 8}" y1="${base}" y2="${base}" stroke="#2A3A5E"/>
    <path d="${area(fullB)}" fill="url(#${id}fb)"/><path d="${line(fullB)}" fill="none" stroke="#8A93A6" stroke-width="1" opacity=".45"/>
    <path d="${area(fullA)}" fill="url(#${id}fa)"/><path d="${line(fullA)}" fill="none" stroke="${col}" stroke-width="1" opacity=".5"/>
    <path d="${area(playedB)}" fill="url(#${id}b)"/><path d="${line(playedB)}" fill="none" stroke="#E3E7EF" stroke-width="1.4" opacity=".9"/>
    <path d="${area(playedA)}" fill="url(#${id}a)" opacity=".92"/><path d="${line(playedA)}" fill="none" stroke="${col}" stroke-width="5" opacity=".45" filter="url(#${id}g)"/><path d="${line(playedA)}" fill="none" stroke="${col}" stroke-width="2"/>
    ${lab.map((_, i) => `<circle cx="${X(i).toFixed(1)}" cy="${base}" r="2.2" fill="${ks[i] && now >= ks[i] ? "#EFD23E" : "#3A4A6E"}"/>`).join("")}
    <line x1="${nx.toFixed(1)}" x2="${nx.toFixed(1)}" y1="${top - 6}" y2="${base}" stroke="#EFD23E" stroke-width="5" opacity=".35" filter="url(#${id}g)"/>
    <line x1="${nx.toFixed(1)}" x2="${nx.toFixed(1)}" y1="${top - 6}" y2="${base}" stroke="#EFD23E" stroke-width="1.6"/>
    <text x="${Math.max(pl - 6, Math.min(W - pr + 6, nx)).toFixed(1)}" y="${top - 9}" text-anchor="${nx < pl + 20 ? "start" : nx > W - pr - 20 ? "end" : "middle"}" font-size="7.5" font-weight="700" fill="#EFD23E" font-family="Poppins,sans-serif" letter-spacing=".1em">NOW</text>
    ${track(base + 31, me, col, "YOU")}${track(base + 56, op, "#C9CFDB", "OPP")}
    <text x="${W - pr}" y="${base + 25}" text-anchor="end" font-size="7" fill="#4F5B75" font-family="IBM Plex Mono,monospace">0 – ${tMax} pts</text></svg>`;
  /* every game in this matchup, four quarter boxes each */
  const gm = {};
  for (const [side, list] of [["me", L.players], ["op", L.oppPlayers]]) for (const p of list){ const g = gameOf(p.tm) || (p.tm ? p.tm + " game" : null); if (!g) continue;
    const e = gm[g] = gm[g] || {g, ko: teamKo(p.tm), when: p.when, me: 0, op: 0}; e[side]++; }
  const games = Object.values(gm).sort((a, b) => (a.ko ?? 9e15) - (b.ko ?? 9e15) || a.g.localeCompare(b.g));
  const gHtml = games.map(x => { const q = gameState(x.g, x.ko), d = q.done, fin = d >= 4 && !q.live;
    const box = [0, 1, 2, 3].map(i => `<i class="${i < d ? "on" : q.live && i === d ? "go" : ""}"></i>`).join("");
    const kt = x.ko ? PT(new Date(x.ko).toISOString(), {weekday: "short", hour: "numeric", minute: "2-digit"}) : (x.when || "");
    return `<div class="gm${fin ? " fin" : q.live ? " live" : ""}" title="${esc(x.g)} · ${esc(kt)}${fin ? " · final" : q.live ? " · live" : ""} · ${x.me} yours, ${x.op} his"><b>${esc(x.g.replace(/ game$/, "").replace(/ @ /, "@"))}</b><span class="qb">${box}</span><span class="gw">${x.me ? `<span class="me">${x.me}</span>` : ""}${x.me && x.op ? "/" : ""}${x.op ? `<span class="op">${x.op}</span>` : ""}</span></div>`; }).join("");
  return `<div class="chartbox prog"><div class="ct">Weekly progress</div>${svg}
    <div class="gms">${gHtml}</div></div>`;
}
/* score range: p10-p90 bars for both sides on one scale, median marked, live score as a tick */
function rangeChart(sc, live){
  if (!sc || !sc.me || !sc.opp) return "";
  const all = [...sc.me, ...sc.opp, ...(live.me > 0 || live.op > 0 ? [live.me, live.op] : [])].filter(v => v !== null && !isNaN(v));
  const lo = Math.floor(Math.min(...all) / 10) * 10 - 5, hi = Math.ceil(Math.max(...all) / 10) * 10 + 5;
  const W = 340, X = (v) => 10 + (W - 20) * (v - lo) / (hi - lo);
  const row = (y, s, col, lab) => `<text x="10" y="${y - 7}" font-size="9" fill="#C9CFDB" font-family="Poppins,sans-serif" font-weight="700">${lab}</text>
    <rect x="${X(s[0])}" y="${y - 4}" width="${Math.max(2, X(s[2]) - X(s[0]))}" height="9" rx="2" fill="${col}" opacity=".35"/>
    <line x1="${X(s[1])}" x2="${X(s[1])}" y1="${y - 7}" y2="${y + 8}" stroke="${col}" stroke-width="3"/>
    <text x="${X(s[1])}" y="${y + 18}" font-size="8.5" text-anchor="middle" fill="#EEF1F6" font-family="IBM Plex Mono,monospace">${s[1].toFixed(0)}</text>`;
  let g = row(22, sc.me, "#EEF1F6", "YOU") + row(58, sc.opp, "#8A93A6", "OPPONENT");
  for (let v = Math.ceil(lo / 20) * 20; v <= hi; v += 20) g += `<text x="${X(v)}" y="86" font-size="8" text-anchor="middle" fill="#5C677D" font-family="IBM Plex Mono,monospace">${v}</text>`;
  return `<svg viewBox="0 0 ${W} 90" role="img">${g}</svg>`;
}

/* ---------- status line ---------- */
const SCHED = {   /* Pacific schedule the page knows: Yahoo reads and the hourly Live sync */
  yahoo(d){ return d === 0 ? [[3, 50], ...Array.from({length: 13}, (_, i) => [8 + i, 50])] : d === 7 ? [] : [[3, 25], [9, 25], [13, 25], [16, 25], [18, 25], [21, 25]]; },
  sync(){ return Array.from({length: 20}, (_, i) => [4 + i, 18]); }
};
function pacNow(){ const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", {timeZone: "America/Los_Angeles", weekday: "short", hour: "numeric", minute: "numeric", hour12: false}).formatToParts(new Date()).map(x => [x.type, x.value]));
  return {d: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(p.weekday), m: (+p.hour % 24) * 60 + (+p.minute)}; }
function nextRun(){ const n = pacNow(); let best = null;
  for (let add = 0; add < 2 && best === null; add++){ const d = (n.d + add) % 7;
    for (const [lab, fn] of [["Yahoo read", SCHED.yahoo], ["Live sync", SCHED.sync]]) for (const [h, mi] of fn(d)){ const t = h * 60 + mi + add * 1440;
      if (t > n.m && (best === null || t < best.t)) best = {t, lab}; } }
  if (!best) return ""; const t = best.t % 1440, h = Math.floor(t / 60), mi = t % 60;
  return `${best.t >= 1440 ? "tomorrow " : ""}${(h % 12) || 12}:${String(mi).padStart(2, "0")} ${h < 12 ? "AM" : "PM"} (${best.lab})`; }
function lastYahooSlotMin(){ const n = pacNow(); let best = null;
  for (let back = 0; back < 2; back++){ const d = (n.d - back + 7) % 7; for (const [h, mi] of SCHED.yahoo(d)){ const t = h * 60 + mi - back * 1440; if (t <= n.m && (best === null || t > best)) best = t; } }
  return best === null ? null : n.m - best; }
function lights(){
  const st = (M && M.status) || {}, age = S ? (Date.now() - new Date(S.stamp).getTime()) / 6e4 : 1e9, since = lastYahooSlotMin();
  let y = "grey"; if (S){ y = age < 14 * 60 ? "green" : age < 26 * 60 ? "yellow" : "red"; if (since !== null && age > since + 75) y = age < 26 * 60 ? "yellow" : "red"; if (st.yahoo && st.yahoo.ok === false) y = "red"; }
  const d = H ? (H.worst === "red" ? "red" : H.worst === "yellow" ? "yellow" : "green") : "grey";
  return {y, d, late: S && since !== null && age > since + 75};
}
function renderStatus(){
  const l = lights(); $("#ltY").className = "lt " + l.y; $("#ltD").className = "lt " + l.d;
  if (!S){ $("#statTxt").innerHTML = "Waiting for the first read."; return; }
  $("#statTxt").innerHTML = l.late ? `<span class="late">Late · ${esc(ptTime(S.stamp))} · ${esc(ago(S.stamp))}</span>`
    : `Updated <b>${esc(ptTime(S.stamp))}</b> <span class="mute">· ${esc(ago(S.stamp))}</span>`;
  const kk = nextKick(), hn = $("#hcNext"); if (hn) hn.innerHTML = `Next update ${esc(nextRun())}${kk ? ` · next kickoff in <b>${esc(kk)}</b>` : ""}.`;
  if (FEED_ERR.size) $("#statTxt").innerHTML += ` · <span class="late">Live feed dropped, reconnecting</span>`;
  $("#wk").textContent = "NFL WEEK " + (S.week || "");
  const fb = $("#sfail"), AL = S.alert;
  if (AL && (typeof AL === "string" ? AL.trim() : (AL.msg || AL.message || AL.text || AL.error))){
    const msg = typeof AL === "string" ? AL : (AL.msg || AL.message || AL.text || AL.error);
    const at = typeof AL === "object" ? (AL.at || AL.time || AL.when || "") : "";
    fb.innerHTML = `<b>RUN FAILED${at ? " · " + esc(ptTime(at)) : ""}</b>${esc(msg)}`; fb.hidden = false;
  } else { fb.hidden = true; fb.innerHTML = ""; }
}
let HC_ALL = false;
const FEED_ERR = new Set();
function renderHealth(){
  if ($("#hc").hidden) return; const box = $("#hcBody");
  if (!H){ box.innerHTML = `<div class="hh">No system check on this page yet.</div><p class="note">The chain writes one after every run.</p>`; return; }
  const cut = (s, n) => { s = String(s || ""); return HC_ALL || s.length <= n ? s : s.slice(0, n - 1) + "…"; };
  const groups = {}; for (const r of H.rows || []) (groups[r.group] = groups[r.group] || []).push(r);
  const st = (M && M.status) || {};
  box.innerHTML = `<div class="hh">System check ${esc(H.checked_pt || "")}: ${esc(H.headline || "")}</div>
    <div class="note">Yahoo read ${esc(S ? ptTime(S.stamp) : "–")} · Ratcliffe ${esc(st.ratcliffe ? ptTime(st.ratcliffe.last) : "–")} · Koerner ${esc(st.koerner ? ptTime(st.koerner.last) : "–")} · build ${esc(st.build ? ptTime(st.build.last) : "–")} · Radar ${esc(st.radar ? ptTime(st.radar.last) : "–")}</div>
    ${Object.entries(groups).map(([g, rs]) => `<div class="hg">${esc(g)}</div>` + rs.map(r =>
      `<div class="hr ${esc(r.status)}"><i></i><div class="row2"><b>${esc(r.name)}</b> <em>${esc([r.when, r.age].filter(Boolean).join(" · "))}</em><br>${esc(cut(r.detail, 160))}</div></div>`).join("")).join("")}
    ${(H.first || []).length ? (HC_ALL ? `<div class="hg">Known issues</div>` + H.first.map(t => `<div class="hr yellow"><i></i><div class="row2">${esc(t)}</div></div>`).join("") : "") : ""}
    <button type="button" class="linkbtn" id="hcAll">${HC_ALL ? "Show less" : "Show all (with known issues)"}</button>`;
}

/* ---------- meters + sticky scoreboard ---------- */
const LASTY = {};
function meters(){
  if (!S || !S.leagues){ return; }
  const prev = prevEntry();
  $("#meters").innerHTML = KEYS.map(k => { const L = lgS(k); if (!L) return "";
    const m = lgM(k), y = chance(L, "y"), live = aFor(k, aLive), w = worst(live);
    const arrow = (src, v) => { const pv = prev && prev.lg[k] ? prev.lg[k][src] : null; if (pv === null || pv === undefined || v === pv) return ""; return v > pv ? `<em class="up">▲</em>` : `<em class="dn">▼</em>`; };
    const po = m.champ && m.champ.base ? m.champ.base.playoff : (m.sim ? m.sim.playoff : null);
    const goNow = [...L.players, ...L.oppPlayers].some(started), F = finals(L), mg = goNow ? score(L.players) - score(L.oppPlayers) : F.me - F.op;
    const es = emptySeats(L).length, fl = LASTY[k] !== undefined && LASTY[k] !== y; LASTY[k] = y;
    const say = `${DK[k]}, ${LGN[k]}: ${y}% to win this week on Yahoo, Ratcliffe ${chance(L, "r")}%, Koerner ${chance(L, "k")}%, Clay ${chance(L, "c")}%, Vegas ${chance(L, "v")}%. ${goNow ? "Live margin" : "Projected margin"} ${sgn(mg)}. Playoff odds ${pcs(po)}. ${live.length} open alerts${es ? ", " + es + " empty seat" + (es > 1 ? "s" : "") : ""}. Opens the league card.`;
    const dlt = (src, v) => { const v0 = weekStart(k, src); if (v0 === null || Math.round(v0) === Math.round(v)) return ""; const d = Math.round(v - v0); return `<em class="${d > 0 ? "up" : "dn"}">${d > 0 ? "▲" : "▼"}${Math.abs(d)}</em>`; };
    return `<div class="mtr${fl ? " flash" : ""}" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}" role="button" tabindex="0" aria-label="${esc(say)}">
      <div class="mtop"><b>${DK[k]}</b><span>${esc(LGN[k])}</span></div><span class="bell mb ${w}" title="${live.length} open alerts">${bellSvg}${live.length}</span>${dial(y, HEX[k], SLUG[k], weekStart(k, "y"))}
      <div class="pct">${y}%${arrow("y", y)}</div><div class="wkd">${weekStart(k, "y") === null ? "YAHOO" : `YAHOO ${dlt("y", y) || "±0"} <span>WK</span>`}</div>
      <div class="orbs">${[["v", "VEGAS", "VEG"], ["r", "RATCLIFFE", "RAT"], ["k", "KOERNER", "KOE"], ["c", "CLAY", "CLAY"]].map(([s2, lab, sh]) => { const v = chance(L, s2), v0 = weekStart(k, s2), d = v0 === null ? null : Math.round(v - v0);
        return `<div class="ob${s2 === "v" ? " vg" : ""}" title="${s2 === "v" ? "Vegas props" : lab.charAt(0) + lab.slice(1).toLowerCase()} ${v}% chance to win this week${v0 === null ? "" : ` · started the week at ${Math.round(v0)}%`}">${glassOrb(v, v0, HEX[k], SLUG[k] + s2, s2 === "v")}<span class="ot"><b><span class="lf">${lab}</span><span class="ls">${sh}</span></b>${d === null ? `<em class="z">–</em>` : d === 0 ? `<em class="z">±0</em>` : `<em class="${d > 0 ? "up" : "dn"}">${d > 0 ? "▲" : "▼"}${Math.abs(d)}</em>`}</span></div>`; }).join("")}</div>
      <div class="mrow"><span class="mgn ${mg > 0 ? "up" : mg < 0 ? "dn" : ""}" title="${goNow ? "live margin" : "projected margin"}">${sgn(mg)}</span><span class="pof">PO <b>${pcs(po)}</b></span></div>
      <div class="tube"><div class="tb"><i style="width:${po === null ? 0 : Math.max(2, po * 100)}%"></i></div></div>${es ? `<div class="seatb">${es} EMPTY SEAT${es > 1 ? "S" : ""}</div>` : ""}</div>`; }).join("");
  const kick = nextKick();
  $("#sch").innerHTML = KEYS.map(k => { const L = lgS(k); if (!L) return ""; const y = chance(L, "y"), pv = prev && prev.lg[k] ? prev.lg[k].y : null;
    const mv = pv === null || pv === undefined ? "" : y === pv ? "" : `<span class="${y > pv ? "up" : "dn"}">${y > pv ? "▲" : "▼"}${Math.abs(y - pv)}</span>`;
    return `<button type="button" class="sc" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}"><div class="t">${DK[k]}</div><div class="s ${score(L.players) > score(L.oppPlayers) ? "ahead" : score(L.players) < score(L.oppPlayers) ? "behind" : ""}">${f1(score(L.players))}–${f1(score(L.oppPlayers))}</div>
      <div class="p"><b>${y}%</b> ${mv}</div><div class="p">${leftOf(L.players).length}/${leftOf(L.oppPlayers).length} left</div></button>`; }).join("");
  $("#sbar").innerHTML = `<span>Yahoo read ${esc(ago(S.stamp))}</span><span>${kick ? "Next kickoff " + esc(kick) : "No games left this week"}</span><button type="button" data-jump="top">Top</button>`;
}
function nextKick(){ const ks = ((M && M.kicks) || []).map(x => new Date(Array.isArray(x) ? x[0] : x).getTime()).filter(t => t > Date.now()).sort((a, b) => a - b);
  if (!ks.length) return ""; const m = Math.round((ks[0] - Date.now()) / 6e4); const d = Math.floor(m / 1440), h = Math.floor(m % 1440 / 60), mi = m % 60;
  return (d ? d + "d " : "") + (h || d ? h + "h " : "") + mi + "m"; }

/* ---------- folds: closed by default, remembered per device ---------- */
const FOLDS = store.get("folds", {});
const fold = (id, title, cnt, body, hot) => `<details class="fold" data-fold="${id}"${FOLDS[id] ? " open" : ""}><summary>${title}${cnt !== "" && cnt !== undefined ? ` <span class="cnt${hot ? " hot" : ""}">${cnt}</span>` : ""}</summary><div class="fb">${body}</div></details>`;

/* Nov 5 v9 (Dom): the page-wide boards (Climb, On the line, ride, Who's left, Rooting guide, Next up) are gone - each
   league card now carries its own version, and the Rooting guide is dropped. */
function whenRank(w){ const m = /(Thu|Fri|Sat|Sun|Mon|Tue)\s+(\d+):(\d+)\s*(am|pm)/i.exec(w || ""); if (!m) return 9999;
  const d = {Thu: 0, Fri: 1, Sat: 2, Sun: 3, Mon: 4, Tue: 5}[m[1].slice(0, 1).toUpperCase() + m[1].slice(1, 3).toLowerCase()];
  return d * 1440 + ((+m[2] % 12) + (/pm/i.test(m[4]) ? 12 : 0)) * 60 + (+m[3]); }

/* ---------- your moves ---------- */
function movesItems(k){ return ((MV && MV.items) || []).filter(x => (!k || BYPRINT[x.lg] === k || x.lg === DK[k]) && !MK["mvd:" + x.id]); }
function movesHtml(k){
  const xs = movesItems(k); if (!xs.length) return `<div class="empty">${k ? "Nothing decided for " + DK[k] + " this week." : "No decided moves on the list."}</div>`;
  const KC = {done: ["DONE", "g"], decide: ["TO DECIDE", "y"], watch: ["WATCH", "n"], act: ["ACT", "r"]};
  return xs.map(x => { const [lab, cls] = KC[x.kind] || ["NOTE", "n"]; const lk = BYPRINT[x.lg] || Object.keys(DK).find(q => DK[q] === x.lg);
    return `<div class="mv"><span class="k">${k ? "" : `<span class="lgtag" style="color:${LCOL[lk] || "var(--ink)"}">${esc(DK[lk] || x.lg)}</span> `}<span class="chip ${cls}">${lab}</span></span><span class="t">${esc(x.text)}${x.due ? ` <span class="mute">· ${esc(x.due)}</span>` : ""}</span><button type="button" class="x" data-mvx="${esc(x.id)}" aria-label="Remove this line">×</button></div>`; }).join("") +
    (k ? "" : `<p class="note">Your decided plan, kept by Claude${MV && MV.updated ? " · updated " + esc(MV.updated) : ""}. × hides a line on every device.</p>`);
}

/* ---------- Nov 5 v9 charts (Dom: "improve the graphics... super cool", "charts are very important") ---------- */
let GID = 0; const gid = () => "z" + (++GID);
const heatCol = (v) => { const t = Math.max(0, Math.min(1, (v - .25) / .5)); const a = [255, 107, 114], b = [247, 197, 49], c = [79, 208, 138];
  const m = t < .5 ? a.map((x, i) => x + (b[i] - x) * t * 2) : b.map((x, i) => x + (c[i] - x) * (t - .5) * 2); return `rgb(${m.map(Math.round).join(",")})`; };
/* area line chart: like lineChart, the first series gets a glowing gradient fill */
function areaChart(series, xlabels, h = 120, fmt = (v) => v){
  const W = 340, pl = 28, pr = 10, pt = 10, pb = 18, n = Math.max(2, xlabels.length), id = gid();
  const X = (i) => pl + (W - pl - pr) * (i / (n - 1)), Y = (v) => pt + (h - pt - pb) * (1 - v / 100);
  let g = `<defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${series[0].col}" stop-opacity=".55"/><stop offset="1" stop-color="${series[0].col}" stop-opacity="0"/></linearGradient>
    <filter id="${id}f" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>`;
  for (const v of [0, 25, 50, 75, 100]) g += `<line x1="${pl}" x2="${W - pr}" y1="${Y(v)}" y2="${Y(v)}" stroke="${v === 50 ? "#3A4A6E" : "#17233F"}" ${v === 50 ? 'stroke-dasharray="3 3"' : ""}/>` + (v % 50 === 0 ? `<text x="${pl - 5}" y="${Y(v) + 3}" font-size="8.5" text-anchor="end" fill="#8A93A6" font-family="IBM Plex Mono,monospace">${v}</text>` : "");
  const step = Math.max(1, Math.ceil(n / 6));
  xlabels.forEach((t, i) => { if ((i % step === 0 && n - 1 - i >= step / 2) || i === n - 1) g += `<text x="${X(i)}" y="${h - 4}" font-size="8" text-anchor="${i === n - 1 ? "end" : i === 0 ? "start" : "middle"}" fill="#8A93A6" font-family="Poppins,sans-serif">${esc(t)}</text>`; });
  series.forEach((s, si) => { const P = s.pts.filter(p => p[1] !== null && p[1] !== undefined && !isNaN(p[1])); if (!P.length) return;
    const line = P.map(p => X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1)).join(" ");
    if (si === 0){ g += `<polygon points="${X(P[0][0]).toFixed(1)},${Y(0)} ${line} ${X(P[P.length - 1][0]).toFixed(1)},${Y(0)}" fill="url(#${id})"/>`;
      g += `<polyline points="${line}" fill="none" stroke="${s.col}" stroke-width="5" opacity=".45" filter="url(#${id}f)"/>`; }
    g += `<polyline points="${line}" fill="none" stroke="${s.col}" stroke-width="${s.w || 2}" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""} stroke-linejoin="round" stroke-linecap="round"/>`;
    const L = P[P.length - 1]; g += `<circle cx="${X(L[0]).toFixed(1)}" cy="${Y(L[1]).toFixed(1)}" r="${si ? 2.6 : 4}" fill="${s.col}" stroke="#0B1222" stroke-width="1.2"/>`;
    if (si === 0) g += `<text x="${Math.min(W - pr - 2, X(L[0]) - 6).toFixed(1)}" y="${(Y(L[1]) - 8).toFixed(1)}" font-size="11" text-anchor="end" fill="#fff" font-family="Bebas Neue,Arial Narrow,sans-serif" letter-spacing=".04em">${esc(fmt(L[1]))}</text>`; });
  return `<svg viewBox="0 0 ${W} ${h}" role="img">${g}</svg>`;
}
/* the drawn road to the title: five rings (playoffs, round 1, semis, final, title), each filled to its chance, linked by
   tubes as thick as the chance of getting that far; likeliest opponent in each round under its ring */
function bracketChart(c, k){
  const b = c.base || {}, br = c.bracket || {}, col = HEX[k], id = gid();
  const st = [["PLAYOFFS", b.playoff, null], ["ROUND 1", b.playoff, (br.r1 || [])[0]], ["SEMIS", b.semis, (br.r2 || [])[0]], ["FINAL", b.final, (br.final || [])[0]], ["TITLE", b.title, null]];
  if (st.some(s => s[1] === undefined || s[1] === null)) return "";
  const W = 340, H = 146, cy = 54, R = 23, xs = st.map((_, i) => 34 + i * 68);
  let g = `<defs><filter id="${id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
    <linearGradient id="${id}t" gradientUnits="userSpaceOnUse" x1="0" x2="${W}" y1="0" y2="0"><stop offset="0" stop-color="${col}"/><stop offset="1" stop-color="#EFD23E"/></linearGradient></defs>`;
  for (let i = 0; i < 4; i++){ const w = Math.max(1.5, 14 * (st[i + 1][1] || 0) / Math.max(.01, st[0][1] || .01) ); 
    g += `<line x1="${xs[i] + R}" x2="${xs[i + 1] - R}" y1="${cy}" y2="${cy}" stroke="#1C2A48" stroke-width="14" stroke-linecap="round"/><line x1="${xs[i] + R}" x2="${xs[i + 1] - R}" y1="${cy}" y2="${cy}" stroke="url(#${id}t)" stroke-width="${w.toFixed(1)}" stroke-linecap="round" opacity=".9"/>`; }
  st.forEach(([lab, p, opp], i) => { const x = xs[i], a = Math.max(.001, Math.min(.999, p)), A = -Math.PI / 2 + a * 2 * Math.PI, last = i === 4, cc = last ? "#EFD23E" : col;
    const x1 = x + R * Math.cos(A), y1 = cy + R * Math.sin(A);
    g += `<circle cx="${x}" cy="${cy}" r="${R}" fill="#0E1628" stroke="#24304C" stroke-width="5"/>`;
    g += `<path d="M${x} ${cy - R} A${R} ${R} 0 ${a > .5 ? 1 : 0} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}" fill="none" stroke="${cc}" stroke-width="5" stroke-linecap="round"/>`;
    if (last) g += `<path d="M${x - 7} ${cy - 12} h14 v5 a7 7 0 0 1 -14 0 z M${x - 2} ${cy - 1} h4 v4 h3 v3 h-10 v-3 h3 z" fill="#EFD23E" opacity=".9"/>`;
    g += `<text x="${x}" y="${cy + (last ? 18 : 5)}" text-anchor="middle" font-size="${last ? 11 : 15}" fill="#fff" font-family="Bebas Neue,Arial Narrow,sans-serif" letter-spacing=".03em">${pcs(p)}</text>`;
    g += `<text x="${x}" y="16" text-anchor="middle" font-size="8.5" font-weight="700" fill="${last ? "#EFD23E" : "#C9CFDB"}" font-family="Poppins,sans-serif" letter-spacing=".08em">${lab}</text>`;
    if (opp){ const nm = String(opp.team || ""); g += `<text x="${x}" y="${cy + R + 16}" text-anchor="middle" font-size="7.5" fill="#8A93A6" font-family="Poppins,sans-serif">likeliest</text><text x="${x}" y="${cy + R + 26}" text-anchor="middle" font-size="8" fill="#C9CFDB" font-family="Poppins,sans-serif" font-weight="600">${esc(nm.length > 13 ? nm.slice(0, 12) + "…" : nm)}</text><text x="${x}" y="${cy + R + 36}" text-anchor="middle" font-size="7.5" fill="#8A93A6" font-family="IBM Plex Mono,monospace">${pcs(opp.p)}</text>`; } });
  if (b.first || br.bye) g += `<text x="${xs[1]}" y="${cy + R + 48}" text-anchor="middle" font-size="7.5" fill="#EFD23E" font-family="Poppins,sans-serif">first-round bye ${pcs(br.bye ?? b.first)}</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(`Playoffs ${pcs(b.playoff)}, semis ${pcs(b.semis)}, final ${pcs(b.final)}, title ${pcs(b.title)}`)}">${g}</svg>`;
}
/* where you finish: one bar per seed, playoff seeds in the league color, a gold cut line at the last playoff seat */
function seedChart(c, k){
  const s = (c.base || {}).seeds; if (!s || !s.length) return "";
  const N = Math.round((c.race || []).reduce((a, r) => a + (r.playoff || 0), 0)) || 6, W = 340, H = 112, pl = 6, pr = 6, base = 88, top = 26;
  const bw = (W - pl - pr) / s.length, mx = Math.max(...s, .01), id = gid(), best = s.indexOf(Math.max(...s));
  let g = `<defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${HEX[k]}"/><stop offset="1" stop-color="${HEX[k]}" stop-opacity=".35"/></linearGradient></defs>`;
  s.forEach((p, i) => { const x = pl + i * bw + 3, h = (base - top) * p / mx, y = base - h, inn = i < N;
    g += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(bw - 6).toFixed(1)}" height="${Math.max(1, h).toFixed(1)}" rx="2.5" fill="${inn ? `url(#${id})` : "#3A4664"}"${i === best ? ' stroke="#fff" stroke-width="1.2"' : ""}/>`;
    if (p >= .03) g += `<text x="${(x + (bw - 6) / 2).toFixed(1)}" y="${(y - 3).toFixed(1)}" text-anchor="middle" font-size="7.5" fill="#C9CFDB" font-family="IBM Plex Mono,monospace">${Math.round(p * 100)}</text>`;
    g += `<text x="${(x + (bw - 6) / 2).toFixed(1)}" y="${base + 11}" text-anchor="middle" font-size="8.5" fill="${inn ? "#EEF1F6" : "#6C7790"}" font-family="Bebas Neue,Arial Narrow,sans-serif">${i + 1}</text>`; });
  const cx = pl + N * bw; g += `<line x1="${cx.toFixed(1)}" x2="${cx.toFixed(1)}" y1="6" y2="${base + 2}" stroke="#EFD23E" stroke-width="1.4" stroke-dasharray="3 2"/><text x="${(cx - 4).toFixed(1)}" y="12" text-anchor="end" font-size="7.5" fill="#EFD23E" font-family="Poppins,sans-serif" font-weight="700" letter-spacing=".06em">PLAYOFF LINE</text>`;
  g += `<text x="${W / 2}" y="${H - 2}" text-anchor="middle" font-size="7.5" fill="#6C7790" font-family="Poppins,sans-serif">FINAL SEED · % OF SIMULATED SEASONS</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img">${g}</svg>`;
}
/* how many wins: histogram of simulated final win totals, the usual playoff cut marked */
function winsChart(c, k){
  const h = c.wins_hist; if (!h || !h.length) return ""; const tot = h.reduce((a, v) => a + v, 0) || 1;
  const lo = h.findIndex(v => v > 0), hi = h.length - 1 - [...h].reverse().findIndex(v => v > 0); if (lo < 0) return "";
  const cut = c.line && c.line.median, W = 340, H = 106, pl = 6, pr = 6, base = 84, top = 26, n = hi - lo + 1, bw = (W - pl - pr) / n, mx = Math.max(...h);
  let g = "";
  for (let w = lo; w <= hi; w++){ const p = h[w] / tot, x = pl + (w - lo) * bw + 3, ht = (base - top) * h[w] / mx, ok = cut !== undefined && w >= cut;
    g += `<rect x="${x.toFixed(1)}" y="${(base - ht).toFixed(1)}" width="${(bw - 6).toFixed(1)}" height="${Math.max(1, ht).toFixed(1)}" rx="2.5" fill="${ok ? HEX[k] : "#3A4664"}" opacity="${ok ? 1 : .9}"/>`;
    if (p >= .02) g += `<text x="${(x + (bw - 6) / 2).toFixed(1)}" y="${(base - ht - 3).toFixed(1)}" text-anchor="middle" font-size="7.5" fill="#C9CFDB" font-family="IBM Plex Mono,monospace">${Math.round(p * 100)}</text>`;
    g += `<text x="${(x + (bw - 6) / 2).toFixed(1)}" y="${base + 11}" text-anchor="middle" font-size="9" fill="#EEF1F6" font-family="Bebas Neue,Arial Narrow,sans-serif">${w}</text>`; }
  if (cut !== undefined && cut >= lo && cut <= hi){ const x = pl + (cut - lo) * bw; g += `<line x1="${x.toFixed(1)}" x2="${x.toFixed(1)}" y1="14" y2="${base + 2}" stroke="#EFD23E" stroke-width="1.4" stroke-dasharray="3 2"/><text x="${Math.min(x + 4, 150).toFixed(1)}" y="10" font-size="7.5" fill="#EFD23E" font-family="Poppins,sans-serif" font-weight="700" letter-spacing=".06em">USUAL CUT · ${cut} W${c.line.reach !== undefined ? " · YOU REACH IT " + pcs(c.line.reach) : ""}</text>`; }
  g += `<text x="${W / 2}" y="${H - 2}" text-anchor="middle" font-size="7.5" fill="#6C7790" font-family="Poppins,sans-serif">FINAL WINS · % OF SIMULATED SEASONS</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img">${g}</svg>`;
}
/* on the line: playoff odds now, if you win, if you lose, on one 0-100 track */
function swingChart(c, k){
  const sw = (c.swing || [])[0], now = (c.base || {}).playoff; if (!sw || now === undefined) return "";
  const W = 340, H = 70, X = (v) => 14 + (W - 28) * v, y = 34, id = gid();
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(`Playoff odds ${pc(now)} now, ${pc(sw.po_w)} with a win, ${pc(sw.po_l)} with a loss`)}"><defs><linearGradient id="${id}" x1="0" x2="1"><stop offset="0" stop-color="#FF6B72"/><stop offset="1" stop-color="#4FD08A"/></linearGradient></defs>
    <rect x="14" y="${y - 4}" width="${W - 28}" height="8" rx="4" fill="#1C2A48"/>
    <rect x="${X(sw.po_l).toFixed(1)}" y="${y - 4}" width="${Math.max(2, X(sw.po_w) - X(sw.po_l)).toFixed(1)}" height="8" rx="4" fill="url(#${id})"/>
    ${[0, .5, 1].map(v => `<text x="${X(v)}" y="${H - 4}" text-anchor="middle" font-size="7.5" fill="#6C7790" font-family="IBM Plex Mono,monospace">${v * 100}%</text>`).join("")}
    <circle cx="${X(sw.po_l).toFixed(1)}" cy="${y}" r="6" fill="#FF6B72" stroke="#0B1222" stroke-width="2"/><text x="${X(sw.po_l).toFixed(1)}" y="${y - 11}" text-anchor="middle" font-size="12" fill="#FF6B72" font-family="Bebas Neue,Arial Narrow,sans-serif">LOSE ${pc(sw.po_l)}</text>
    <circle cx="${X(sw.po_w).toFixed(1)}" cy="${y}" r="6" fill="#4FD08A" stroke="#0B1222" stroke-width="2"/><text x="${X(sw.po_w).toFixed(1)}" y="${y - 11}" text-anchor="middle" font-size="12" fill="#4FD08A" font-family="Bebas Neue,Arial Narrow,sans-serif">WIN ${pc(sw.po_w)}</text>
    <path d="M${X(now).toFixed(1)} ${y + 6} l-5 8 h10 z" fill="#fff"/><text x="${X(now).toFixed(1)}" y="${y + 24}" text-anchor="middle" font-size="8" fill="#fff" font-family="Poppins,sans-serif" font-weight="700">NOW ${pc(now)}</text></svg>`;
}
/* the road ahead: one glowing tile per remaining game, colored by your chance to win it */
function roadTiles(c, m){
  const g = (c.path && c.path.length ? c.path : Object.entries((m.viz || {}).weeks || {}).map(([wk, win]) => ({wk, win, opp: ""})));
  if (!g.length) return "";
  return `<div class="road">${g.map(x => { const nm = String(x.opp || ""); return `<div style="--hc:${heatCol(x.win)}" title="${esc(`Week ${x.wk} vs ${nm}: ${pc(x.win)}`)}"><span>WK ${esc(x.wk)}</span><b>${pc(x.win)}</b><em>${esc(nm.length > 11 ? nm.slice(0, 10) + "…" : nm)}</em></div>`; }).join("")}</div>`;
}
/* every expert, every starter: five thin bars per man - Yahoo, Ratcliffe, Koerner, Clay, Vegas - in this league's scoring */
function expertBars(L, m, k){
  const xp = (m.xp && m.xp.players) || {}, rows = [];
  for (const p of L.players){ const v = xp[p.name] || {}; const vals = {y: +p.proj || null, r: v.r ?? null, k: v.k ?? null, c: v.c ?? null, v: v.v ?? null};
    if ([vals.r, vals.k, vals.c].every(x => x === null)) continue; const ns = [vals.y, vals.r, vals.k, vals.c].filter(x => x !== null); rows.push({n: p.name, slot: p.slot, ...vals, sp: Math.max(...ns) - Math.min(...ns)}); }
  if (!rows.length) return "";
  const mx = Math.max(...rows.flatMap(r => [r.y, r.r, r.k, r.c, r.v]).filter(x => x !== null), 5), W = 340, rh = 48, nl = 104, bx = nl + 4, bwid = W - bx - 34;
  const S4 = [["y", "#EEF1F6", "Y"], ["r", HEX[k], "R"], ["k", HEX[k] + "AA", "K"], ["c", "#8A93A6", "C"], ["v", "#E0A84A", "V"]];
  let g = "";
  rows.forEach((r, i) => { const y0 = 4 + i * rh;
    if (i % 2 === 0) g += `<rect x="0" y="${y0 - 2}" width="${W}" height="${rh}" fill="#ffffff" opacity=".025" rx="4"/>`;
    g += `<text x="4" y="${y0 + 11}" font-size="9.5" fill="#fff" font-family="Poppins,sans-serif" font-weight="600">${esc(r.n.length > 17 ? r.n.slice(0, 16) + "…" : r.n)}</text><text x="4" y="${y0 + 22}" font-size="7.5" fill="#8A93A6" font-family="Poppins,sans-serif">${esc(r.slot || "")}${r.sp >= 3 ? ' · <tspan fill="#EFD23E" font-weight="700">SPLIT ' + r.sp.toFixed(1) + "</tspan>" : ""}</text>`;
    S4.forEach(([s, col], j) => { const v = r[s]; if (v === null) return; const y = y0 + 1 + j * 8.6, w = Math.max(1.5, bwid * v / mx);
      g += `<rect x="${bx}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="5.6" rx="2.8" fill="${col}"/><text x="${(bx + w + 3).toFixed(1)}" y="${(y + 5.6).toFixed(1)}" font-size="7.4" fill="#C9CFDB" font-family="IBM Plex Mono,monospace">${v.toFixed(1)}</text>`; }); });
  return `<svg viewBox="0 0 ${W} ${rows.length * rh + 6}" role="img">${g}</svg><div class="key"><span><i style="border-color:#EEF1F6"></i>Yahoo</span><span><i style="border-color:${HEX[k]}"></i>Ratcliffe (leads)</span><span><i style="border-color:${HEX[k]}AA"></i>Koerner</span><span><i style="border-color:#8A93A6"></i>Clay</span><span><i style="border-color:#E0A84A"></i>Vegas</span></div>`;
}
/* Nov 7 (Dom: "it's gonna let us know if there's a disagreement ... compare it and talk about it"): Vegas against Ratcliffe on
   every man the cards cover. Props run low on touchdowns, so each Vegas number is first lifted by this league's typical
   Vegas-to-Ratcliffe ratio; a man is flagged when the lifted number still differs from Ratcliffe by 25%+ and 2+ points. */
function vegHtml(L, m, k, yv){
  const xp = (m.xp && m.xp.players) || {}, both = Object.entries(xp).filter(([n, v]) => v && v.v != null && v.r != null && v.r > 1 && !v.out && v.pos !== "K");
  if (!both.length) return "";
  const rat = both.map(([, v]) => v.v / v.r).sort((a, b) => a - b), med = rat[Math.floor(rat.length / 2)] || 1;
  const rows = both.map(([n, v]) => { const adj = v.v / med, d = adj - v.r; return {n, v, adj, d, pct: d / v.r}; })
    .filter(x => Math.abs(x.d) >= 2 && Math.abs(x.pct) >= .25).sort((a, b) => Math.abs(b.d) - Math.abs(a.d)).slice(0, 8);
  const gapTxt = (v) => v.vrk ? `Vegas #${v.vrk}${v.vgap ? ` (${v.vgap > 0 ? "+" : ""}${v.vgap} vs experts)` : ""}` : "";
  return `<div class="sub">Vegas vs Ratcliffe${yv != null ? ` · Vegas needle ${yv}%` : ""}</div>` + (rows.length ? rows.map(x => `<div class="mv"><span class="k ${x.d > 0 ? "up" : "dn"}">${x.d > 0 ? "▲ HIGHER" : "▼ LOWER"}</span><span class="t">${esc(x.n)} <span class="mute">${esc(x.v.why || "")} · ${esc(gapTxt(x.v))}</span></span><span class="num">R ${f1(x.v.r)} · V ${f1(x.v.v)}</span></div>`).join("")
    : `<p class="note">No big disagreements: Vegas and Ratcliffe line up on every man the cards cover.</p>`) +
    `<p class="note">Across your men Vegas runs ${Math.abs(Math.round((med - 1) * 100)) < 2 ? "even with" : "about " + Math.abs(Math.round((med - 1) * 100)) + "% " + (med > 1 ? "above" : "below")} Ratcliffe in ${DK[k]} scoring, so each Vegas number is evened out by that before comparing; kickers use the site's own points. Flag = 25%+ and 2+ points apart. Talk it through - Ratcliffe still leads.</p>`;
}
/* who's been closest: season average points missed per man, shortest bar wins */
function accBars(){
  const acc = (M && M.acc && M.acc.src) || {}, rows = Object.entries(acc).map(([s, wk]) => { const ws = Object.values(wk); const n = ws.reduce((a, v) => a + (v[1] || 1), 0);
    return {s, avg: ws.reduce((a, v) => a + v[0] * (v[1] || 1), 0) / (n || 1), wks: ws.length, men: n}; }).sort((a, b) => a.avg - b.avg);
  if (!rows.length) return ""; const W = 340, rh = 22, lo = Math.floor(Math.min(...rows.map(r => r.avg)) - 1), hi = Math.ceil(Math.max(...rows.map(r => r.avg)) + .3), X = (v) => 86 + (W - 130) * (v - lo) / (hi - lo);
  const NM = {yahoo: "Yahoo", gotham: "Gotham", ratcliffe: "Ratcliffe", koerner: "Koerner", clay: "Clay", vegas: "Vegas", sleeper: "Sleeper"};
  return `<svg viewBox="0 0 ${W} ${rows.length * rh + 16}" role="img">${rows.map((r, i) => { const y = 4 + i * rh, best = i === 0;
    return `<text x="4" y="${y + 12}" font-size="10" fill="${best ? "#EFD23E" : "#EEF1F6"}" font-family="Poppins,sans-serif" font-weight="600">${esc(NM[r.s] || r.s)}</text>
      <rect x="86" y="${y + 3}" width="${(X(r.avg) - 86).toFixed(1)}" height="11" rx="5.5" fill="${best ? "#EFD23E" : "#3F5785"}"/>
      <text x="${(X(r.avg) + 5).toFixed(1)}" y="${y + 12}" font-size="9" fill="#C9CFDB" font-family="IBM Plex Mono,monospace">${r.avg.toFixed(2)} <tspan fill="#6C7790">· ${r.wks} wk${r.wks > 1 ? "s" : ""}</tspan></text>`; }).join("")}
    <text x="86" y="${rows.length * rh + 13}" font-size="7.5" fill="#6C7790" font-family="Poppins,sans-serif">POINTS MISSED PER MAN · SHORTER = CLOSER</text></svg>`;
}
/* who's left in this league, by kickoff */
function leftHere(L){
  const rows = [...L.players.filter(p => !isDone(p) && !isOut(p)).map(p => ({p, me: true})), ...L.oppPlayers.filter(p => !isDone(p) && !isOut(p)).map(p => ({p, me: false}))];
  if (!rows.length) return `<div class="empty">Nobody left to play.</div>`;
  const by = {}; for (const r of rows){ const w = isLive(r.p) ? "Playing now" : (r.p.when || "Time unknown"); (by[w] = by[w] || []).push(r); }
  return Object.keys(by).sort((a, b) => (a === "Playing now" ? -1 : 0) - (b === "Playing now" ? -1 : 0) || whenRank(a) - whenRank(b)).map(w => `<div class="sub">${esc(w)}</div><div class="lh">${by[w].map(r => `<span class="${r.me ? "me" : "op"}">${esc(r.p.name)} <em>${f1(manFinal(r.p, "y"))}</em></span>`).join("")}</div>`).join("") + `<p class="note">Bright = yours, dim = the opponent's. Number = Yahoo's projected final.</p>`;
}

/* ---------- a league card ---------- */
function card(k){
  const L = lgS(k); if (!L) return "";
  const m = lgM(k), c = m.champ || {}, pm = (M && M.pm && M.pm[k]) || {};
  const me = score(L.players), op = score(L.oppPlayers), F = finals(L), done = settled(L), prev = prevEntry(), pv = prev && prev.lg[k];
  const meL = leftOf(L.players), opL = leftOf(L.oppPlayers);
  /* what it takes */
  let takes = "";
  if (!done){ const need = F.op - me, rest = meL.reduce((a, p) => a + Math.max(0, manFinal(p, "y") - pts(p)), 0);
    const top = meL.slice().sort((a, b) => manFinal(b, "y") - manFinal(a, "y"))[0];
    takes = `<div class="takes">To pass the opponent's projected <b>${f1(F.op)}</b> you need <b>${f1(Math.max(0, need))}</b> more from ${meL.length} men left (Yahoo projects ${f1(rest)}).`;
    if (top && need > 0){ const others = rest - Math.max(0, manFinal(top, "y") - pts(top)), be = need - others + pts(top);
      takes += ` Breakeven: if the rest hit their numbers, <b>${esc(top.name)}</b> has to score <b>${f1(Math.max(0, be))}</b> (Yahoo has him at ${f1(manFinal(top, "y"))}).`; }
    takes += `</div>`; }
  /* empty seats: a starter who can't score */
  const seats = emptySeats(L);
  const seatHtml = seats.length ? `<div class="seat"><div class="h">EMPTY SEAT</div>${seats.map(p => `<div><b>${esc(p.slot)} ${esc(p.name)}</b> ${p.status ? `<span class="chip r">${esc(p.status)}</span>` : ""} · Yahoo ${f1(p.proj)} · locks ${esc(p.when || "?")}</div>`).join("")}</div>` : "";
  /* the four needles with their move since the last read */
  const xr = [["y", "YAHOO"], ["v", "VEGAS"], ["r", "RATCLIFFE"], ["k", "KOERNER"], ["c", "CLAY"]].map(([s, lab]) => { const v = chance(L, s), p0 = pv ? pv[s] : null;
    const mv = p0 === null || p0 === undefined || p0 === v ? "" : `<em class="${v > p0 ? "up" : "dn"}">${v > p0 ? "▲" : "▼"}${Math.abs(v - p0)}</em>`; return `<div><b>${v}%</b><span>${lab}</span> ${mv}</div>`; }).join("");
  const ys = [chance(L, "y"), chance(L, "r"), chance(L, "k"), chance(L, "c")], yv = chance(L, "v"), split = Math.max(...ys) - Math.min(...ys);
  const anyStart = [...L.players, ...L.oppPlayers].some(started);
  const splitHtml = split >= 20 && opL.length + meL.length > 0 ? `<div class="warn">The sources split by ${split} points on this game${anyStart ? "" : " - check why before kickoff"}.</div>` : "";
  /* points since the last read */
  let since = "";
  if (pv){ const dm = me - pv.me, dop = op - pv.op, moved = [];
    if (pv.pl) for (const [side, list] of [["you", L.players], ["opp", L.oppPlayers]]) for (const p of list){ const was = pv.pl[p.name]; if (was === undefined) continue; const d = pts(p) - was; if (Math.abs(d) >= .5) moved.push({n: p.name, d, side}); }
    moved.sort((a, b) => Math.abs(b.d) - Math.abs(a.d));
    since = `<div class="sub">Since last read · ${sgn(dm)} / ${sgn(dop)}</div>` + (`<div class="takes">Since the ${esc(ptTime(prev.t))} read: you <b class="${dm >= 0 ? "up" : "dn"}">${sgn(dm)}</b> · opponent <b>${sgn(dop)}</b> · net <b class="${dm - dop >= 0 ? "up" : "dn"}">${sgn(dm - dop)}</b> (Yahoo live scores).</div>` +
      (moved.length ? `<div class="sub">Who moved</div>` + moved.map(x => `<div class="mv"><span class="k">${x.side === "you" ? "You" : '<span class="mute">Opp</span>'}</span><span class="t">${esc(x.n)}</span><span class="num ${x.d >= 0 ? "up" : "dn"}">${sgn(x.d)}</span></div>`).join("") : `<p class="note">Nobody moved half a point or more.</p>`)); }
  /* read-by-read chance */
  const es = trailEntries().filter(e => e.w === S.week && e.lg[k]);
  const rbr = es.length >= 2 ? `<div class="chartbox"><div class="ct">Today's ride · chance to win this week, read by read</div>${areaChart([["y", HEX[k], ""], ["r", "#EEF1F6", ""], ["k", "#C9CFDB", "4 3"], ["c", "#8A93A6", "2 3"], ["v", "#E0A84A", "1 2"]].map(([s, col, dash]) => ({col, dash, w: s === "y" ? 2.6 : 1.4, pts: es.map((e, i) => [i, e.lg[k][s]])})), es.map(e => PT(e.t, {weekday: "short", hour: "numeric"}).replace(" ", "")), 130, v => Math.round(v) + "%")}
      <div class="key"><span><i style="border-color:${HEX[k]}"></i>Yahoo</span><span><i style="border-color:#EEF1F6"></i>Ratcliffe</span><span><i class="dot" style="border-color:#C9CFDB"></i>Koerner</span><span><i class="dot" style="border-color:#8A93A6"></i>Clay</span><span><i class="dot" style="border-color:#E0A84A"></i>Vegas</span></div></div>` : "";
  const rng = m.viz && m.viz.scores ? `<div class="chartbox"><div class="ct">Score range · simulator</div>${rangeChart(m.viz.scores, {me, op})}<p class="note">Bar = the middle 80% of ${esc(m.sim ? (m.sim.sims || "").toLocaleString() : "")} simulated games, tick = the median final. ${esc(m.viz.run || "")}.</p></div>` : "";
  /* played bar */
  const bar = (list) => list.map(p => `<i class="${isLive(p) ? "on" : isDone(p) ? "done" : ""}"></i>`).join("");
  const scoreHtml = `<div class="score"><div class="side"><span>${esc(L.team || "Dark Knight")}</span><div class="big">${f1(me)}</div></div>
      <div class="mid">${done ? `<div class="vd" style="color:${me >= op ? "var(--up)" : "var(--dn)"}">${verdict(me - op)}</div><small>FINAL · ${sgn(me - op)}</small>` : `<div class="vd">${esc(L.state || "")}</div><small>${meL.length} / ${opL.length} left</small>`}</div>
      <div class="side r"><span>${esc(L.opp)}</span><div class="big" style="color:var(--ink2)">${f1(op)}</div></div></div>
    <div class="proj"><span>Yahoo proj ${f1(F.me)}</span><span>Yahoo proj ${f1(F.op)}</span></div>
    <div class="played">${bar(L.players)}<em>PLAYED</em>${bar(L.oppPlayers)}</div>`;

  /* road to the championship */
  const mvs = (c.moves || []).filter(x => shown(moveId(k, x), sigMove(x)));
  const calls = (c.calls || []).filter(x => shown(callId(k, x), sigCall(x)));
  const trades = (c.trades || []).filter(x => shown(tradeId(k, x), sigTrade(x)));
  const b = c.base || {};
  const road = `<p class="note">${esc(c.rec_now || m.rec || "")} · ${c.stand_now ? "standing " + c.stand_now : ""}${b.wins ? " · " + b.wins.toFixed(1) + " expected wins" : ""}${b.seed ? " · likeliest seed " + b.seed : ""}. Season odds from ${esc(c.note ? "the championship simulator" : "the simulator")}, built ${esc(c.built || "")}.</p>
    <div class="sub">Pickups tested (${mvs.length})</div>${mvs.length ? mvs.map(x => `<div class="pk"><b>Add ${esc(x.add)}</b> (${esc(x.pos || "")} ${esc(x.nfl || "")}, ${esc(x.acq || "")}) · drop ${esc(x.drop)}: playoff odds <b class="${x.d_playoff >= 0 ? "up" : "dn"}">${sgn(x.d_playoff * 100)} pts</b>, title ${sgn((x.d_title || 0) * 100)} pts, ${sgn(x.d_wins || 0, 2)} wins.<br><span class="mute">${esc(x.drop)} ${esc(x.drop_role || "")}${x.block && x.block.rival ? " · blocks " + esc(x.block.rival) : ""}</span></div>`).join("") : `<p class="note">Nothing tested clears the bar right now.</p>`}
    ${(c.not_worth || []).length ? `<p class="note">${c.not_worth.length} other adds tested and not worth it (under half a point of playoff odds).</p>` : ""}
    <div class="sub">Injury calls (${calls.length})</div>${calls.length ? calls.map(x => { const best = (x.options || [])[0];
      return `<div class="pk"><b>${esc(x.starter)}</b> <span class="chip ${/^(O|D)$/.test(x.status) ? "r" : "y"}">${esc(x.status)}</span> locks ${esc(x.locks)}: this week ${pc(x.week_now)} with him, ${pc(x.week_if_out)} if out${best ? `; best fill <b>${esc(best.add)}</b> for ${esc(best.drop)} (${sgn((best.d_week || 0) * 100)} this week)` : ""}. Season playoff odds if he sits: ${pc(x.if_out && x.if_out.playoff)}.</div>`; }).join("") : `<p class="note">No starter on the injury report.</p>`}
    <div class="sub">Trades screened (${trades.length} of ${c.trades_screened || 0})</div>${trades.length ? trades.map(x => `<div class="pk">Give <b>${esc((x.give || []).join(" + "))}</b> for <b>${esc(x.get)}</b>: playoff odds ${sgn(x.d_playoff * 100)} pts, title ${sgn((x.d_title || 0) * 100)} pts.</div>`).join("") : `<p class="note">${esc(c.trade_rules || "No trade clears both sides.")}</p>`}
    ${(c.worth || []).length ? `<div class="sub">What your bench is for</div>` + c.worth.map(x => `<div class="pk"><b>${esc(x.name)}</b> ${esc(x.pos)}: ${esc(x.role)}. Dropping him would ${(x.d_playoff || 0) < -.0005 ? "cost " + Math.abs(x.d_playoff * 100).toFixed(1) + " pts of" : (x.d_playoff || 0) > .0005 ? "add " + (x.d_playoff * 100).toFixed(1) + " pts to" : "barely move"} playoff odds.</div>`).join("") : ""}`;
  const roadCnt = `${mvs.length} pickups · ${calls.length} injury · ${trades.length} trades`;

  /* season analytics */
  const hist = (m.sim_hist || []).map(h => [h[0], h[2]]);
  const acc = (M && M.acc && M.acc.src) || {};
  const accRows = Object.entries(acc).map(([s, wk]) => { const ws = Object.entries(wk); const last = ws[ws.length - 1]; const avg = ws.reduce((a, [, v]) => a + v[0], 0) / (ws.length || 1);
    return [s, last ? last[0] : "", last ? last[1][0] : null, avg, ws.length]; }).sort((a, b) => a[3] - b[3]);
  const byes = {}; for (const r of ((M && M.rosters && M.rosters.t && M.rosters.t[DKP[k]]) || [])){ const wk = (M.byes || {})[r[3]]; if (wk) for (const w of wk) if (w >= (S.week || 0)) (byes[w] = byes[w] || []).push(r[0]); }
  const sw0 = (c.swing || [])[0], sw1 = (c.swing || [])[1];
  const picture = `${bracketChart(c, k) ? `<div class="chartbox"><div class="ct">The bracket · your road to the title</div>${bracketChart(c, k)}<p class="note">Each ring fills to your chance of getting that far; the gold tube thins as the odds drop. Under each round: the opponent you're likeliest to meet there, and how often. ${esc(c.note || "")}.</p></div>` : ""}
    ${seedChart(c, k) ? `<div class="chartbox"><div class="ct">Where you finish</div>${seedChart(c, k)}</div>` : ""}
    ${winsChart(c, k) ? `<div class="chartbox"><div class="ct">How many wins</div>${winsChart(c, k)}</div>` : ""}
    ${(c.race || []).length ? `<div class="sub">The race</div><div class="scroll"><table class="tbl"><tr><th>Team</th><th>Record</th><th>Playoffs</th><th>Title</th></tr>${c.race.map(r => `<tr class="${r.me ? "me" : ""}"><td>${esc(r.team)}</td><td>${esc(r.rec)}</td><td>${pcs(r.playoff)}</td><td>${pcs(r.title)}</td></tr>`).join("")}</table></div>` : ""}`;
  const season = `${hist.length >= 2 ? `<div class="chartbox"><div class="ct">Playoff odds over time</div>${areaChart([{col: HEX[k], w: 2.6, pts: hist.map((h, i) => [i, h[1] * 100])}], hist.map(h => PT(h[0], {weekday: "short", hour: "numeric"}).replace(" ", "")), 120, v => Math.round(v) + "%")}<p class="note">Playoff odds for the season after every simulator run.</p></div>` : `<p class="note">Playoff odds history: ${hist.length} point${hist.length === 1 ? "" : "s"} so far (${hist.length ? pcs(hist[0][1]) : "–"}); the line draws from the second run on.</p>`}
    <div class="chartbox"><div class="ct">The road ahead · chance to win each game</div>${roadTiles(c, m)}${b.wins ? `<p class="note">${b.wins.toFixed(1)} expected wins${b.seed ? " · likeliest seed " + b.seed : ""}.</p>` : ""}</div>
    ${sw1 ? `<div class="sub">Week ${sw1.wk} next up</div><div class="pk">vs ${esc(sw1.opp)}: ${pc(sw1.win)} chance to win that game · playoff odds <span class="up">${pc(sw1.po_w)}</span> with a win, <span class="dn">${pc(sw1.po_l)}</span> with a loss.</div>` : ""}
    ${Object.keys(byes).length ? `<div class="sub">Byes ahead</div>${Object.entries(byes).sort((a, b) => a[0] - b[0]).map(([w, ns]) => `<div class="mv"><span class="k">Wk ${w}</span><span class="t">${esc(ns.join(", "))}</span></div>`).join("")}` : ""}`;

  /* expert cards */
  const xp = (m.xp && m.xp.players) || {};
  const xpc = Object.entries(xp).filter(([n, v]) => v && (v.r !== undefined || v.k !== undefined)).map(([n, v]) => { const ns = [v.r, v.k, v.c].filter(x => x !== null && x !== undefined); const sp = ns.length ? Math.max(...ns) - Math.min(...ns) : 0;
    return {n, v, sp}; }).filter((x, i, arr) => arr.findIndex(y => y.v.pos === x.v.pos && y.v.r === x.v.r && y.v.k === x.v.k && y.v.c === x.v.c) === i).sort((a, b) => b.sp - a.sp);
  const eb = expertBars(L, m, k);
  const experts = (eb ? `<div class="chartbox"><div class="ct">Your starters · every expert · ${DK[k]} scoring</div>${eb}</div>` : "") + (accBars() ? `<div class="chartbox"><div class="ct">Who's been closest</div>${accBars()}</div>` : "") + (xpc.length ? `<div class="sub">Every player the experts cover</div><div class="xpc">${xpc.map(({n, v, sp}) => `<div class="c${sp >= 3 ? " split" : ""}"><b>${esc(n)}</b><div class="why">${esc(v.pos || "")} · ${esc(v.why || "")}${sp >= 3 ? " · split " + sp.toFixed(1) : ""}</div>
      <div class="ns"><span>R ${f1(v.r)}</span><span>K ${f1(v.k)}</span><span>C ${f1(v.c)}</span><span title="${v.vrk ? "Vegas rank " + v.vrk + (v.vgap ? " (" + (v.vgap > 0 ? "+" : "") + v.vgap + " vs experts)" : "") : "no Vegas prop"}">V ${f1(v.v)}</span></div></div>`).join("")}</div><p class="note">This week in ${DK[k]} scoring: R = Ratcliffe (FTN, leads), K = Koerner (FantasyLabs), C = Clay (ESPN), V = Vegas (player props, a check - not an expert). Gold edge = the experts split by 3+ points. ${esc((m.experts || {}).read ? "Ranks read " + m.experts.read : "")}</p>
      ${((m.experts || {}).rising || []).length ? `<div class="sub">Moving up</div>${m.experts.rising.map(t => `<div class="pk">${esc(t)}</div>`).join("")}` : ""}
      ${((m.experts || {}).sliding || []).length ? `<div class="sub">Sliding</div>${m.experts.sliding.map(t => `<div class="pk">${esc(t)}</div>`).join("")}` : ""}` : (eb ? "" : `<div class="empty">No expert numbers for this league yet.</div>`));

  /* weather for the teams in this game */
  const teams = new Set([...L.players, ...L.oppPlayers].filter(p => !isDone(p)).map(p => (p.tm || "").toUpperCase()));
  const WX = (M && M.wx && M.wx.teams) || {}, games = {};
  for (const t of teams){ const w = WX[t]; if (w && !games[w.game]) games[w.game] = w; }
  const wxs = Object.values(games).sort((a, b) => (b.flag - a.flag) || String(a.ko).localeCompare(String(b.ko)));
  const sky = (w) => w.roof === "dome" ? `<svg viewBox="0 0 26 20"><path d="M3 17a10 10 0 0 1 20 0z" fill="#5C677D"/></svg>` : w.snow > 0 ? `<svg viewBox="0 0 26 20"><circle cx="13" cy="9" r="6" fill="#DDE6F5"/><text x="13" y="19" font-size="7" text-anchor="middle" fill="#DDE6F5">✶✶</text></svg>`
    : /rain/.test(w.sky) || w.pop >= 60 ? `<svg viewBox="0 0 26 20"><ellipse cx="13" cy="8" rx="9" ry="5" fill="#8A93A6"/><path d="M8 14l-1 4M13 14l-1 4M18 14l-1 4" stroke="#5B9BF5" stroke-width="1.6"/></svg>`
    : /cloud/.test(w.sky) ? `<svg viewBox="0 0 26 20"><ellipse cx="13" cy="11" rx="10" ry="6" fill="#9AA2B5"/></svg>` : `<svg viewBox="0 0 26 20"><circle cx="13" cy="10" r="6" fill="#F7C531"/></svg>`;
  const wx = wxs.length ? `<div class="wxg">${wxs.map(w => `<div class="wc${w.flag ? " bad" : ""}">${sky(w)}<div class="t"><b>${esc(w.game)}</b><br>${w.roof === "dome" ? "Dome" : `${Math.round(w.temp)}°F · wind ${Math.round(w.wind)} mph · rain ${w.pop}%`}${w.flag ? `<br><span class="why">${esc((w.why || []).join(", ") || "can move the game")}</span>` : ""}</div></div>`).join("")}</div><p class="note">Kickoff forecast, Open-Meteo, pulled ${esc(M.wx ? ptTime(M.wx.pulled) : "")}. Red = weather that can move the game.</p>` : `<div class="empty">No weather for games still to play.</div>`;

  /* clear this league */
  const al = aFor(k, aLive), notes = movesItems(k);
  const clr = `<div class="clr">${[["alerts", "Alerts " + al.length], ["notes", "Notes " + notes.length], ["pickups", "Pickups " + mvs.length], ["calls", "Injury calls " + calls.length], ["trades", "Trades " + trades.length], ["all", "Everything"]].map(([w, lab]) =>
    `<button type="button" class="${ARM === "clr:" + k + ":" + w ? "arm" : ""}" data-clr="${k}:${w}">${ARM === "clr:" + k + ":" + w ? "Tap again" : lab}</button>`).join("")}</div>
    <p class="note">Alerts are deleted for good. Notes, pickups, injury calls and trades are cleared until something real changes (a different drop, a 3-point swing in playoff odds, a new injury status).</p>`;

  const rec = [m.rec ? "Record " + m.rec : "", (m.std || []).map(x => x.join(" ")).join(" · "), m.oppRec ? "opponent " + m.oppRec : ""].filter(Boolean).join(" · ");
  return `<article class="card" id="${SLUG[k]}" style="--lc:${LCOL[k]}">
    <div class="chd"><span class="dkb">${DK[k]}</span><span class="lgname">${esc(LGN[k])}</span><span class="vs">vs</span><span class="opp">${esc(L.opp)}</span></div>
    <div class="recl">${[m.rec ? `<span><b>${esc(m.rec)}</b></span>` : "", ...(m.std || []).map(x => `<span>${esc(x[0].toLowerCase())} <b>${esc(x.slice(1).join(" "))}</b></span>`), m.oppRec ? `<span>opp <b>${esc(m.oppRec)}</b></span>` : ""].join("")}</div>
    ${scoreHtml}${takes}${seatHtml}
    <div class="xrow">${xr}</div><p class="note">Chance to win this week, best lineup both sides. Ratcliffe leads every decision number; Vegas is a check.</p>${splitHtml}${vegHtml(L, m, k, yv)}
    ${progress(L, k)}
    ${fold("wk-" + SLUG[k], "This week", rbr ? "today's ride" : meL.length + opL.length + " left", `${rbr}${rng}${sw0 ? `<div class="chartbox"><div class="ct">On the line · playoff odds for the season</div>${swingChart(c, k)}<p class="note">Title odds ${pcs(sw0.ti_w)} with a win, ${pcs(sw0.ti_l)} with a loss.</p></div>` : ""}${since}<div class="sub">Who's left</div>${leftHere(L)}`)}
    ${fold("road-" + SLUG[k], "Recommendations", roadCnt, road + `<div class="sub">Your moves (${notes.length})</div>` + movesHtml(k), calls.length > 0)}
    ${fold("al-" + SLUG[k], "Alerts", al.length ? `${al.filter(x => x.color === "red").length} act now · ${al.filter(x => x.color === "gold").length} monitor · ${al.filter(x => x.color === "grey").length} noted` : "none", `<div id="alb-${SLUG[k]}">${alertsBlock(k)}</div>`, al.some(x => x.color === "red"))}
    ${fold("pic-" + SLUG[k], "Playoff picture", b.playoff !== undefined ? pcs(b.playoff) + " playoffs · " + pcs(b.title) + " title" : "", picture)}
    ${fold("ana-" + SLUG[k], "Season odds", hist.length + " runs", season)}
    ${fold("xp-" + SLUG[k], "Experts", xpc.filter(x => x.sp >= 3).length + " splits", experts)}
    ${fold("wx-" + SLUG[k], "Game weather", wxs.filter(w => w.flag).length ? wxs.filter(w => w.flag).length + " red" : wxs.length + " games", wx, wxs.some(w => w.flag))}
    ${fold("clr-" + SLUG[k], "Clear " + DK[k], "", clr)}
  </article>`;
}

/* ---------- top alert strip, separated alerts ---------- */
const alertRow = (x) => { const k = BYPRINT[x.lg];
  return `<button type="button" class="${mk(x.id).read ? "" : "unread"}" data-goal="${esc(x.id)}"><span class="dot ${x.color}"></span><span><span class="lgtag" style="color:${LCOL[k] || "var(--ink)"}">${esc(DK[k] || x.lg)}</span> ${esc(x.title)}${x.deadline_utc && dueMin(x.deadline_utc) > 0 ? `<span class="dl${dueMin(x.deadline_utc) < 180 ? " hot" : ""}">${DUE(x.deadline_utc)} LEFT</span>` : ""}</span></button>`; };
/* ---------- needs you: before-lock free agents, act-now alerts, empty seats ---------- */
function needs(){
  const box = $("#need"); if (!box || !S) return;
  const out = [];
  for (const x of alertsAll().filter(aLive)){ const k = BYPRINT[x.lg];
    if (x.kind === "radar_prekick" && x.deadline_utc && dueMin(x.deadline_utc) > 0)
      out.push({k, col: dueMin(x.deadline_utc) < 180 ? "red" : "gold", r: 1, t: dueMin(x.deadline_utc), aid: x.id, cd: DUE(x.deadline_utc), cl: "until lock",
        html: `<b>${esc(x.who || "")}</b> is a free agent you could start. Free to add until ${esc((x.by || "").replace(/^before /i, "") || ptTime(x.deadline_utc))}.`});
    else if (x.color === "red")
      out.push({k, col: "red", r: 0, t: x.deadline_utc ? dueMin(x.deadline_utc) : 0, aid: x.id, cd: x.deadline_utc && dueMin(x.deadline_utc) > 0 ? DUE(x.deadline_utc) : "", cl: "act now", html: esc(x.title)});
  }
  for (const k of KEYS){ const L = lgS(k); if (!L) continue;
    for (const p of emptySeats(L)) out.push({k, col: "red", r: 0, t: whenRank(p.when), cd: "", cl: p.when ? "locks " + p.when : "",
      html: `Empty seat: <b>${esc(p.slot)} ${esc(p.name)}</b>${p.status ? " (" + esc(p.status) + ")" : ""} won't score. Yahoo has him at ${f1(p.proj)}.`}); }
  out.sort((a, b) => (a.col === "red" ? 0 : 1) - (b.col === "red" ? 0 : 1) || a.r - b.r || a.t - b.t);
  { const n = $("#ltN"); if (n) n.className = "lt " + (out.some(o => o.col === "red") ? "red" : out.length ? "yellow" : "green"); }
  box.innerHTML = out.length ? `<div class="need">${out.map(o => `<button type="button" class="nd ${o.col}" ${o.aid ? `data-goal="${esc(o.aid)}"` : `data-jump="${SLUG[o.k]}"`}><span class="lgtag" style="color:${LCOL[o.k] || "var(--ink)"}">${DK[o.k] || ""}</span><span class="tx">${o.html}</span>${o.cd || o.cl ? `<span class="cd">${esc(o.cd)}<small>${esc(o.cl)}</small></span>` : ""}</button>`).join("")}</div>`
    : `<div class="allclear">Nothing needs you: no free agent to grab before lock, no empty seat, no act-now alert.</div>`;
}
/* open one alert in its league card */
async function goAlert(id){
  const x = alertsAll().find(a => a.id === id); if (!x) return; const k = BYPRINT[x.lg]; if (!k) return;
  const fid = "al-" + SLUG[k]; FOLDS[fid] = true; store.set("folds", FOLDS);
  const d = document.querySelector(`details[data-fold="${fid}"]`); if (d) d.open = true;
  if (x.color === "grey") SHOWNOTED.add(k);
  OPEN.add(id);
  if (!mk(id).read) await writeMarks({[id]: Object.assign({}, mk(id), {read: new Date().toISOString()})}); else renderAlertsOnly();
  const el = [...document.querySelectorAll("#cards .al")].find(e => e.dataset.aid === id); el && el.scrollIntoView({behavior: SMOOTH(), block: "center"});
}
/* find a player */
function findRun(){
  const box = $("#fres"), raw = $("#findq").value.trim(), q = norm(raw); if (q.length < 2){ box.innerHTML = ""; return; }
  const ros = []; for (const k of KEYS){ const L = lgS(k); if (!L) continue;
    for (const p of L.players) if (norm(p.name).includes(q)) ros.push({k, p, mine: true});
    for (const p of L.oppPlayers) if (norm(p.name).includes(q)) ros.push({k, p, mine: false}); }
  const hits = alertsAll().filter(x => (aLive(x) || aSep(x)) && norm([x.who, x.title, x.tie].join(" ")).includes(q)).sort(aSort);
  const mv = ((MV && MV.items) || []).filter(x => norm(x.text).includes(q));
  const html = (ros.length ? `<div class="sub">This week's lineups (${ros.length})</div>` + ros.map(r => `<div class="mv"><span class="k"><span class="lgtag" style="color:${LCOL[r.k]}">${DK[r.k]}</span></span><span class="t"><b>${esc(r.p.name)}</b> <span class="mute">${esc(r.p.slot || "")} ${esc(r.p.tm || "")} · ${r.mine ? "starts for you" : "starts against you"} · ${started(r.p) ? f1(pts(r.p)) + " pts" : "Yahoo " + f1(r.p.proj)}${r.p.status ? " · " + esc(r.p.status) : ""} · ${esc(r.p.when || "")}</span></span></div>`).join("") : "")
    + (hits.length ? `<div class="sub">Alerts (${hits.length})</div><div class="prev">${hits.map(alertRow).join("")}</div>` : "")
    + (mv.length ? `<div class="sub">Your moves (${mv.length})</div>` + mv.map(x => `<div class="mv"><span class="k mute">${esc(x.lg)}</span><span class="t">${esc(x.text)}</span></div>`).join("") : "");
  box.innerHTML = html || `<div class="empty">Nobody on this page matches “${esc(raw)}”.</div>`;
}
/* the floating NEXT button names the league it goes to */
function nextTarget(){ const cs = KEYS.map(k => document.getElementById(SLUG[k])).filter(Boolean); return cs.find(c => c.getBoundingClientRect().top > 100) || cs[0] || null; }
function nextLabel(){ const b = $("#goNext"), nx = nextTarget(); if (!b) return; if (!nx){ b.textContent = "NEXT"; return; }
  const lab = DK[KEYOF[nx.id]] || "NEXT", up = nx.getBoundingClientRect().top <= 100; b.textContent = lab + (up ? " ↑" : " ↓"); b.setAttribute("aria-label", "Jump to " + lab); }
let NL = 0; addEventListener("scroll", () => { if (NL) return; NL = requestAnimationFrame(() => { NL = 0; nextLabel(); }); }, {passive: true});
function jumpTo(id){ const el = document.getElementById(id); if (!el) return; el.scrollIntoView({behavior: SMOOTH(), block: "start"});
  try { history.replaceState(null, "", "#" + id); } catch(_){} }
function scoresText(){ return `Dark Knight Live · NFL Week ${S.week} · ${ptTime(S.stamp)} PT\n` + KEYS.map(k => { const L = lgS(k); if (!L) return ""; const F = finals(L);
  return `${DK[k]} vs ${L.opp}: ${f1(score(L.players))}–${f1(score(L.oppPlayers))} (Yahoo proj ${f1(F.me)}–${f1(F.op)}) · ${chance(L, "y")}% to win`; }).filter(Boolean).join("\n"); }
function astrip(){
  const live = alertsAll().filter(aLive), cnt = (c) => live.filter(x => x.color === c).length;
  const newest = A ? A.generated || A.built : "", unread = live.filter(x => !mk(x.id).read), loud = live.filter(x => x.color !== "grey").sort((a, b) => (b.deadline_utc && dueMin(b.deadline_utc) > 0 ? 1 : 0) - (a.deadline_utc && dueMin(a.deadline_utc) > 0 ? 1 : 0) || aSort(a, b));
  { const ac = $("#alCnt"); if (ac) { ac.textContent = live.length ? `${cnt("red")} act now · ${cnt("gold")} monitor · ${cnt("grey")} noted` : "none"; ac.className = "cnt" + (cnt("red") ? " hot" : ""); } }
  $("#astrip").innerHTML = `<div class="astrip"><span class="ttl" style="color:${live.length ? (cnt("red") ? "var(--red)" : cnt("gold") ? "var(--amber)" : "var(--ink)") : "var(--up)"}">${live.length}</span>
    <span class="tal">${cnt("red")} act now · ${cnt("gold")} monitor · ${cnt("grey")} noted${unread.length ? ` · <span class="unr">${unread.length} unread</span>` : ""}${newest ? " · checked " + esc(ago(newest)) : ""}</span>
    ${unread.length ? `<button type="button" class="abtn sep" data-markread="1">Mark all read</button>` : ""}
    <button type="button" class="abtn${ARM === "del:ALL" ? " arm" : ""}" data-abulk="del:ALL">${ARM === "del:ALL" ? "Tap again: delete " + live.length : "Delete all"}</button>
    <button type="button" class="abtn sep${ARM === "sep:ALL" ? " arm" : ""}" data-abulk="sep:ALL">${ARM === "sep:ALL" ? "Tap again: separate " + live.length : "Separate all"}</button></div>
    <div class="note">${KEYS.map(k => { const n = aFor(k, aLive); return `<a href="#${SLUG[k]}" data-jump="${SLUG[k]}" style="color:${LCOL[k]};text-decoration:none;font-weight:700">${DK[k]} ${n.length}</a>`; }).join(" · ")} · Each alert sits in its league's card. Separate keeps it for 7 days at the bottom of the page.</div>
    ${loud.length ? `<div class="prev">${loud.slice(0, 4).map(alertRow).join("")}</div>${loud.length > 4 ? `<p class="note">${loud.length - 4} more act-now and monitor alerts in the league cards.</p>` : ""}` : ""}`;
}
function separated(){
  const xs = alertsAll().filter(aSep).sort(aSort);
  $("#sepCnt").textContent = xs.length ? xs.length + " kept 7 days" : "none";
  $("#sep").innerHTML = xs.length ? `<div class="ahd"><span class="tal">Delete for good:</span><button type="button" class="abtn${ARM === "delsep:ALL" ? " arm" : ""}" data-abulk="delsep:ALL">${ARM === "delsep:ALL" ? "Tap again: delete " + xs.length : "Delete all " + xs.length}</button>
    ${KEYS.map(k => { const n = xs.filter(x => BYPRINT[x.lg] === k).length; return n ? `<button type="button" class="abtn${ARM === "delsep:" + k ? " arm" : ""}" data-abulk="delsep:${k}">${ARM === "delsep:" + k ? "Tap again" : DK[k] + " · " + n}</button>` : ""; }).join("")}</div>
    <div class="alist">${xs.map(x => alertCard(x, true)).join("")}</div>` : `<div class="empty">Nothing separated.</div>`;
}
function renderAlertsOnly(){ astrip(); separated(); needs(); for (const k of KEYS){ const el = document.getElementById("alb-" + SLUG[k]); if (el) el.innerHTML = alertsBlock(k); } meters(); }

function footer(){
  const st = (M && M.status) || {};
  $("#foot").innerHTML = `Yahoo read ${esc(S ? ptTime(S.stamp) + " (" + ago(S.stamp) + ")" : "–")} · Dispatch build ${esc(st.build ? ptTime(st.build.last) : "–")} · Ratcliffe ${esc(st.ratcliffe ? ptTime(st.ratcliffe.last) : "–")} · Koerner ${esc(st.koerner ? ptTime(st.koerner.last) : "–")} · alerts ${esc(A ? ago(A.generated || A.built) : "–")} · system check ${esc(H ? H.checked_pt : "–")}.<br>
    Every chance on this page is the chance to win this week unless it says playoff odds or title odds. The page's code is saved in the dk-feeds repo (live_page/) so it can always be restored.`;
}

/* ---------- render ---------- */
function renderAll(){
  renderStatus(); renderHealth();
  if (!S || !S.leagues){ return; }
  const y = scrollY; meters(); astrip();
  $("#cards").innerHTML = KEYS.map(card).join("");
  separated(); footer(); needs();
  if ($("#findq").value.trim()) findRun();
  scrollTo(0, y); nextLabel();
}
document.addEventListener("toggle", (e) => { const d = e.target; if (!d.matches || !d.matches("details[data-fold]")) return; FOLDS[d.dataset.fold] = d.open; store.set("folds", FOLDS); }, true);

/* ---------- events ---------- */
function rmsg(t, bad){ const el = $("#rmsg"); el.textContent = t; el.hidden = false; el.style.background = bad ? "#FBE4E5" : "#F2E6C4"; clearTimeout(rmsg.t); rmsg.t = setTimeout(() => el.hidden = true, 9000); }
document.addEventListener("click", async (e) => {
  const t = e.target.closest ? e.target : e.target.parentElement;
  const ga = t.closest("[data-goal]"); if (ga){ e.preventDefault(); await goAlert(ga.dataset.goal); return; }
  const j = t.closest("[data-jump]"); if (j){ e.preventDefault(); const id = j.dataset.jump; if (id === "top") scrollTo({top: 0, behavior: SMOOTH()}); else jumpTo(id); return; }
  if (t.closest("[data-markread]")){ const ts = new Date().toISOString(), up = {}; for (const x of alertsAll().filter(aLive)) if (!mk(x.id).read) up[x.id] = Object.assign({}, mk(x.id), {read: ts});
    await writeMarks(up); rmsg("Marked " + Object.keys(up).length + " alerts read."); return; }
  if (t.id === "copy"){ if (!S){ rmsg("No scores yet - the first read hasn't landed.", 1); return; } const txt = scoresText();
    try { await navigator.clipboard.writeText(txt); rmsg("Copied the four scores."); } catch(_){ rmsg("This view blocked copying. Select the text below:\n\n" + txt, 1); } return; }
  if (t.closest("#stat")){ const b = $("#hc"); b.hidden = !b.hidden; $("#stat").setAttribute("aria-expanded", String(!b.hidden)); renderHealth(); return; }
  if (t.id === "hcAll"){ HC_ALL = !HC_ALL; renderHealth(); return; }
  if (t.id === "goTop"){ scrollTo({top: 0, behavior: SMOOTH()}); return; }
  if (t.id === "goNext"){ const nx = nextTarget(); nx && jumpTo(nx.id); return; }
  if (t.id === "openAll" || t.id === "closeAll"){ const o = t.id === "openAll"; document.querySelectorAll("details[data-fold]").forEach(d => { d.open = o; FOLDS[d.dataset.fold] = o; }); store.set("folds", FOLDS); return; }
  if (t.id === "wake"){ try { if (wakeLock){ await wakeLock.release(); wakeLock = null; t.classList.remove("on"); t.textContent = "Keep screen on"; }
      else { wakeLock = await navigator.wakeLock.request("screen"); t.classList.add("on"); t.textContent = "Screen stays on"; wakeLock.addEventListener("release", () => { wakeLock = null; t.classList.remove("on"); t.textContent = "Keep screen on"; }); } }
    catch(_){ rmsg("This view can't keep the screen on.", 1); } return; }
  if (t.id === "refresh"){ t.disabled = true; t.textContent = "Asking…";
    try { const mcp = await window.claude?.use?.("mcp"); if (!mcp) throw {code: "no_mcp"};
      await mcp.callTool(RSRV, "fire_trigger", {trigger_id: LIVE_SYNC_TASK}); rmsg("Asked for the Live sync - the newest build lands here in about 2 minutes.");
    } catch(err){ rmsg(err && err.code === "no_mcp" ? "Refresh needs the Claude Code Remote connector in this view; the hourly sync keeps running." : "Refresh didn't start (" + ((err && (err.code || err.message)) || "error") + "). The hourly sync keeps running.", 1); }
    finally { setTimeout(() => { t.disabled = false; t.textContent = "Refresh"; }, 4000); } return; }
  const nb = t.closest("[data-noted]"); if (nb){ const k = nb.dataset.noted; SHOWNOTED.has(k) ? SHOWNOTED.delete(k) : SHOWNOTED.add(k); renderAlertsOnly(); return; }
  const mx = t.closest("[data-mvx]"); if (mx){ await writeMarks({["mvd:" + mx.dataset.mvx]: {at: new Date().toISOString()}}); renderAll(); return; }
  const bulk = t.closest("[data-abulk]"); if (bulk){ const id = bulk.dataset.abulk; if (!armed(id)) return;
    const [op, k] = id.split(":"), ts = new Date().toISOString(), up = {};
    const pool = op === "delsep" ? alertsAll().filter(aSep) : alertsAll().filter(aLive);
    for (const x of pool) if (k === "ALL" || BYPRINT[x.lg] === k) up[x.id] = Object.assign({}, mk(x.id), op === "sep" ? {cleared: ts, read: mk(x.id).read || ts} : {deleted: ts});
    await writeMarks(up); renderAll(); return; }
  const cl = t.closest("[data-clr]"); if (cl){ const id = "clr:" + cl.dataset.clr; if (!armed(id)) return;
    const [k, w] = cl.dataset.clr.split(":"), ts = new Date().toISOString(), up = {}, c = lgM(k).champ || {};
    if (w === "alerts" || w === "all") for (const x of aFor(k, aLive)) up[x.id] = Object.assign({}, mk(x.id), {deleted: ts});
    if (w === "notes" || w === "all") for (const x of movesItems(k)) up["mvd:" + x.id] = {at: ts};
    if (w === "pickups" || w === "all") for (const x of c.moves || []) up["x:" + moveId(k, x)] = {at: ts, sig: sigMove(x)};
    if (w === "calls" || w === "all") for (const x of c.calls || []) up["x:" + callId(k, x)] = {at: ts, sig: sigCall(x)};
    if (w === "trades" || w === "all") for (const x of c.trades || []) up["x:" + tradeId(k, x)] = {at: ts, sig: sigTrade(x)};
    await writeMarks(up); renderAll(); return; }
  const card = t.closest(".al"); if (card){ const id = card.dataset.aid, act = t.closest("[data-ado]");
    if (act){ e.stopPropagation(); const a = act.dataset.ado, ts = new Date().toISOString(); OPEN.delete(id);
      if (a === "close"){ renderAlertsOnly(); return; }
      await writeMarks({[id]: Object.assign({}, mk(id), a === "del" ? {deleted: ts} : {cleared: ts, read: mk(id).read || ts})}); return; }
    if (t.closest(".b") && OPEN.has(id)) return;
    OPEN.has(id) ? OPEN.delete(id) : OPEN.add(id);
    if (!mk(id).read) await writeMarks({[id]: Object.assign({}, mk(id), {read: new Date().toISOString()})}); else renderAlertsOnly(); return; }
});
document.addEventListener("keydown", (e) => { if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches(".al,.mtr")){ e.preventDefault(); e.target.click(); } });
document.addEventListener("keydown", (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target.matches && e.target.matches("input,textarea,select,[contenteditable]")){ if (e.key === "Escape") e.target.blur(); return; }
  if (/^[1-4]$/.test(e.key)){ e.preventDefault(); jumpTo("dk" + e.key); }
  else if (e.key === "t" || e.key === "T"){ scrollTo({top: 0, behavior: SMOOTH()}); }
  else if (e.key === "n" || e.key === "N"){ const nx = nextTarget(); nx && jumpTo(nx.id); }
  else if (e.key === "/"){ e.preventDefault(); $("#findq").focus(); }
  else if (e.key === "Escape"){ if (OPEN.size){ OPEN.clear(); renderAlertsOnly(); } const b = $("#hc"); if (!b.hidden){ b.hidden = true; $("#stat").setAttribute("aria-expanded", "false"); } }
});
$("#findq").addEventListener("input", findRun);
addEventListener("hashchange", () => { const h = location.hash.slice(1); if (/^dk[1-4]$/.test(h)) document.getElementById(h)?.scrollIntoView({behavior: SMOOTH(), block: "start"}); });
let wakeLock = null, HASHED = false;
/* sticky scoreboard once the meters scroll away */
try { new IntersectionObserver(([en]) => { $("#sticky").hidden = en.isIntersecting || !S; }, {threshold: 0}).observe($("#metersFrame")); } catch(_){}
setInterval(() => { renderStatus(); if (S){ meters(); needs(); } }, 60000);

/* ---------- data ---------- */
(async () => {
  const db = await window.claude?.use?.("db");
  if (!db){ $("#statTxt").innerHTML = `<span class="late">Can't reach the live feed in this view.</span> Open Dark Knight Live from your Claude sidebar or artifact list.`; $("#meters").innerHTML = `<div class="empty" style="grid-column:1/-1">No data in this view.</div>`; return; }
  DB = db;
  const val = (s) => s && (s.data ? s.data() : s);
  const watch = (path, fn) => { try { db.doc(path).onSnapshot(s => { if (FEED_ERR.delete(path)) renderStatus(); fn(val(s)); },
      () => { FEED_ERR.add(path); renderStatus(); setTimeout(() => watch(path, fn), 30000); }); }
    catch(_){ db.doc(path).get().then(s => fn(val(s))).catch(() => {}); } };
  const tm = setTimeout(() => { if (!S) $("#statTxt").innerHTML = `<span class="late">The live feed hasn't answered in 10 seconds.</span> It keeps trying.`; }, 10000);
  try { TR = val(await db.doc("live/trail").get()) || {entries: []}; } catch(_){ TR = {entries: []}; }
  if (!Array.isArray(TR.entries)) TR = {entries: []};
  watch("live/alert_marks", v => { MK = Object.assign({}, v || {}); if (S) renderAll(); });
  watch("live/moves", v => { MV = v || null; if (S) renderAll(); });
  watch("live/health", v => { H = v || null; renderStatus(); renderHealth(); });
  watch("live/alerts", v => { A = v || null; if (S) renderAll(); });
  watch("live/models", v => { if (v){ M = v; if (S){ renderAll(); trailAdd(); } } });
  watch("live/state", v => { if (v && v.leagues){ clearTimeout(tm); S = v; renderAll(); if (M) trailAdd();
    if (!HASHED){ HASHED = true; const h = location.hash.slice(1); if (/^dk[1-4]$/.test(h)) setTimeout(() => document.getElementById(h)?.scrollIntoView({block: "start"}), 60); } } });
})();
