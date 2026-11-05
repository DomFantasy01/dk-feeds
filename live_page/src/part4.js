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
/* each source's projected final for one man: Yahoo's live projection, or the expert's number (pm: [Ratcliffe, Clay, Koerner]) */
const SRCI = {r: 0, c: 1, k: 2};
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
    const v = src === "r" ? set.ratcliffe : src === "k" ? set.koerner : set.gotham;   /* the build's best-lineup number, both sides */
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
    e.lg[L.key] = {y: chance(L, "y"), r: chance(L, "r"), k: chance(L, "k"), c: chance(L, "c"), me: +score(L.players).toFixed(2), op: +score(L.oppPlayers).toFixed(2), pl};
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
function prevEntry(){ const es = trailEntries().filter(e => S && e.t < S.stamp && e.w === S.week); return es.length ? es[es.length - 1] : null; }

/* ---------- small charts ---------- */
function dial(v, col){
  const a = Math.PI * (1 - Math.max(0, Math.min(100, v)) / 100), cx = 60, cy = 52, r = 42;
  const x = cx + r * Math.cos(a), y = cy - r * Math.sin(a);
  const arc = (p0, p1, c, w) => { const a0 = Math.PI * (1 - p0), a1 = Math.PI * (1 - p1);
    return `<path d="M${cx + r * Math.cos(a0)} ${cy - r * Math.sin(a0)} A${r} ${r} 0 0 1 ${cx + r * Math.cos(a1)} ${cy - r * Math.sin(a1)}" stroke="${c}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`; };
  return `<svg viewBox="0 0 120 60" aria-hidden="true">${arc(0, 1, "#26365A", 9)}${arc(0, Math.max(.01, v / 100), col, 9)}
    <line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#EEF1F6" stroke-width="2.5" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="4" fill="#EEF1F6"/>
    <text x="14" y="59" font-size="8" fill="#8A93A6" font-family="Poppins,sans-serif">0</text><text x="98" y="59" font-size="8" fill="#8A93A6" font-family="Poppins,sans-serif">100</text></svg>`;
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
    : `Updated <b>${esc(ptTime(S.stamp))}</b> · ${esc(ago(S.stamp))} · Next ${esc(nextRun())}`;
  const kk = nextKick(); if (kk) $("#statTxt").innerHTML += ` · Kickoff in <span class="kk">${esc(kk)}</span>`;
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
  const box = $("#hc"); if (box.hidden) return;
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
    const say = `${DK[k]}, ${LGN[k]}: ${y}% to win this week on Yahoo, Ratcliffe ${chance(L, "r")}%, Koerner ${chance(L, "k")}%, Clay ${chance(L, "c")}%. ${goNow ? "Live margin" : "Projected margin"} ${sgn(mg)}. Playoff odds ${pcs(po)}. ${live.length} open alerts${es ? ", " + es + " empty seat" + (es > 1 ? "s" : "") : ""}. Opens the league card.`;
    return `<div class="mtr${fl ? " flash" : ""}" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}" role="button" tabindex="0" aria-label="${esc(say)}">
      <div class="lgn">${esc(LGN[k])}</div><div class="dk">${DK[k]}</div>${dial(y, HEX[k])}
      <div class="pct">${y}%${arrow("y", y)}</div><div class="src">YAHOO · BEST LINEUP</div>
      <div class="mgn ${mg > 0 ? "up" : mg < 0 ? "dn" : ""}"><span>${goNow ? "LIVE" : "PROJ"}</span>${sgn(mg)}</div>${es ? `<div class="seatb">${es} EMPTY SEAT${es > 1 ? "S" : ""}</div>` : ""}
      <div class="xps"><div><span>RATCLIFFE</span><b>${chance(L, "r")}%</b></div><div><span>KOERNER</span><b>${chance(L, "k")}%</b></div><div><span>CLAY</span><b>${chance(L, "c")}%</b></div></div>
      <div class="mrow"><div class="tube"><div class="tb"><i style="width:${po === null ? 0 : Math.max(2, po * 100)}%"></i></div><span>PLAYOFFS ${pcs(po)}</span></div>
        <span class="bell ${w}" title="${live.length} open alerts">${bellSvg}${live.length}</span></div>
      <div class="mstate">${settled(L) ? verdict(score(L.players) - score(L.oppPlayers)) : esc(L.state || "")}</div></div>`; }).join("");
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

/* ---------- the week's boards ---------- */
function climb(){
  const rows = KEYS.map(lgS).filter(Boolean);
  const mx = Math.max(60, ...rows.map(L => Math.max(finals(L).me, finals(L).op))) * 1.05;
  return `<div class="climb">${rows.map(L => { const k = L.key, s = score(L.players), f = finals(L), o = finals(L).op, w = lgM(k).champ && lgM(k).champ.base ? lgM(k).champ.base.wins : null;
    return `<div class="row"><span class="lgtag" style="color:${LCOL[k]}">${DK[k]}</span>
      <div class="bar" title="banked ${f1(s)}, projected ${f1(f.me)}, opponent projected ${f1(o)}"><i style="left:0;width:${s / mx * 100}%;background:${HEX[k]}"></i><i style="left:${s / mx * 100}%;width:${Math.max(0, f.me - s) / mx * 100}%;background:${HEX[k]};opacity:.35"></i><span class="opp" style="left:${o / mx * 100}%"></span></div>
      <div class="v">${f1(s)} → <b>${f1(f.me)}</b><br><span class="mute">opp ${f1(o)}${w !== null ? " · " + w.toFixed(1) + " W" : ""}</span></div></div>`; }).join("")}
    <p class="note">Solid = points banked, faded = Yahoo's projection for the rest, white tick = opponent's projected final. W = expected season wins (championship simulator).</p></div>`;
}
function onTheLine(){
  return `<table class="tbl"><tr><th>League</th><th>This week</th><th>If win</th><th>If lose</th><th>Title W / L</th></tr>${KEYS.map(k => { const L = lgS(k), sw = ((lgM(k).champ || {}).swing || [])[0]; if (!L || !sw) return "";
    return `<tr><td><span class="lgtag" style="color:${LCOL[k]}">${DK[k]}</span> <span class="mute">vs ${esc(sw.opp)}</span></td><td>${chance(L, "y")}%</td><td class="up">${pc(sw.po_w)}</td><td class="dn">${pc(sw.po_l)}</td><td>${pcs(sw.ti_w)} / ${pcs(sw.ti_l)}</td></tr>`; }).join("")}</table>
    <p class="note">"If win / If lose" = playoff odds for the season. This week = Yahoo's chance to win this week. Simulator: ${esc((lgM("MOST").champ || {}).built || "")}.</p>`;
}
function ride(){
  const es = trailEntries().filter(e => S && e.w === S.week);
  if (es.length < 2) return `<div class="empty">The chart fills in as reads land this week (${es.length} so far).</div>`;
  const xl = es.map(e => PT(e.t, {weekday: "short", hour: "numeric"}).replace(" ", ""));
  return lineChart(KEYS.map(k => ({col: HEX[k], pts: es.map((e, i) => [i, e.lg[k] ? e.lg[k].y : null])})), xl, 130) +
    `<div class="key">${KEYS.map(k => `<span><i style="border-color:${HEX[k]}"></i>${DK[k]}</span>`).join("")}</div><p class="note">Yahoo's chance to win this week, read by read.</p>`;
}
function whoLeft(){
  const byWhen = {}, add = (p, k, side) => { const key = isLive(p) ? "Playing now" : (p.when || "Time unknown"); const id = p.name;
    (byWhen[key] = byWhen[key] || {})[id] = (byWhen[key][id] || {name: p.name, tm: p.tm, mine: [], opp: []}); byWhen[key][id][side].push(k); };
  for (const k of KEYS){ const L = lgS(k); if (!L) continue; L.players.filter(p => !isDone(p) && !isOut(p)).forEach(p => add(p, k, "mine")); L.oppPlayers.filter(p => !isDone(p) && !isOut(p)).forEach(p => add(p, k, "opp")); }
  const order = (w) => w === "Playing now" ? -1 : (((M && M.kicks) || []).length ? 0 : 0);
  const ws = Object.keys(byWhen).sort((a, b) => order(a) - order(b) || whenRank(a) - whenRank(b));
  if (!ws.length) return `<div class="empty">Nobody left to play this week.</div>`;
  return ws.map(w => `<div class="sub">${esc(w)}</div>` + Object.values(byWhen[w]).sort((a, b) => b.mine.length - a.mine.length).map(x =>
    `<div class="mv"><span class="k">${x.mine.map(k => `<span class="lgtag" style="color:${LCOL[k]}">${DK[k]}</span>`).join(" ") || '<span class="mute">opp</span>'}</span><span class="t"><b>${esc(x.name)}</b> <span class="mute">${esc(x.tm || "")}</span>${x.mine.length > 1 ? ` <span class="chip y">×${x.mine.length}</span>` : ""}${x.opp.length ? ` <span class="mute">· against you in ${x.opp.map(k => DK[k]).join(", ")}</span>` : ""}</span></div>`).join("")).join("");
}
function whenRank(w){ const m = /(Thu|Fri|Sat|Sun|Mon|Tue)\s+(\d+):(\d+)\s*(am|pm)/i.exec(w || ""); if (!m) return 9999;
  const d = {Thu: 0, Fri: 1, Sat: 2, Sun: 3, Mon: 4, Tue: 5}[m[1].slice(0, 1).toUpperCase() + m[1].slice(1, 3).toLowerCase()];
  return d * 1440 + ((+m[2] % 12) + (/pm/i.test(m[4]) ? 12 : 0)) * 60 + (+m[3]); }
function rooting(){
  const net = {};
  for (const k of KEYS){ const L = lgS(k); if (!L) continue;
    for (const p of L.players) if (!isDone(p) && !isOut(p)) (net[p.name] = net[p.name] || {n: 0, f: [], a: []}).n++, net[p.name].f.push(k);
    for (const p of L.oppPlayers) if (!isDone(p) && !isOut(p)) (net[p.name] = net[p.name] || {n: 0, f: [], a: []}).n--, net[p.name].a.push(k); }
  const xs = Object.entries(net).map(([n, v]) => ({name: n, ...v})).sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
  const grp = (t, fn, cls) => { const g = xs.filter(fn); return g.length ? `<div class="sub">${t} (${g.length})</div>` + g.map(x =>
    `<div class="mv"><span class="k"><span class="chip ${cls}">${x.n > 0 ? "+" + x.n : x.n}</span></span><span class="t"><b>${esc(x.name)}</b> <span class="mute">${x.f.length ? "yours in " + x.f.map(k => DK[k]).join(", ") : ""}${x.f.length && x.a.length ? " · " : ""}${x.a.length ? "against you in " + x.a.map(k => DK[k]).join(", ") : ""}</span></span></div>`).join("") : ""; };
  if (!xs.length) return `<div class="empty">Nobody left to root for this week.</div>`;
  return grp("Root for", x => x.n > 0, "g") + grp("Root against", x => x.n < 0, "r") + grp("Wash", x => x.n === 0, "n") + `<p class="note">Each remaining man counted across all four leagues: +1 for every league he starts for you, −1 for every opponent he starts for.</p>`;
}
function nextUp(){
  return `<table class="tbl"><tr><th>League</th><th>Next week</th><th>Chance</th><th>Playoffs if W / L</th></tr>${KEYS.map(k => { const sw = ((lgM(k).champ || {}).swing || [])[1]; if (!sw) return "";
    return `<tr><td><span class="lgtag" style="color:${LCOL[k]}">${DK[k]}</span></td><td style="text-align:left">Wk ${sw.wk} vs ${esc(sw.opp)}</td><td>${pc(sw.win)}</td><td><span class="up">${pc(sw.po_w)}</span> / <span class="dn">${pc(sw.po_l)}</span></td></tr>`; }).join("")}</table>
    <p class="note">Chance = the simulator's chance to win that game. Playoff odds are for the season.</p>`;
}
function boards(){
  if (!S || !S.leagues){ $("#boards").innerHTML = ""; return; }
  const left = KEYS.reduce((a, k) => { const L = lgS(k); return a + (L ? leftOf(L.players).length + leftOf(L.oppPlayers).length : 0); }, 0);
  const nxt = ((lgM("MOST").champ || {}).swing || [])[1];
  $("#boards").innerHTML = fold("climb", "The Climb", "all four on one scale", climb()) + fold("line", "On the line this week", "", onTheLine()) +
    fold("ride", "This week's ride", trailEntries().filter(e => S && e.w === S.week).length + " reads", ride()) + fold("left", "Who's left", left + " starters", whoLeft()) +
    fold("root", "Rooting guide", "", rooting()) + fold("next", nxt ? "Week " + nxt.wk + " next up" : "Next up", "", nextUp());
}

/* ---------- your moves ---------- */
function movesItems(k){ return ((MV && MV.items) || []).filter(x => (!k || BYPRINT[x.lg] === k || x.lg === DK[k]) && !MK["mvd:" + x.id]); }
function movesHtml(k){
  const xs = movesItems(k); if (!xs.length) return `<div class="empty">${k ? "Nothing decided for " + DK[k] + " this week." : "No decided moves on the list."}</div>`;
  const KC = {done: ["DONE", "g"], decide: ["TO DECIDE", "y"], watch: ["WATCH", "n"], act: ["ACT", "r"]};
  return xs.map(x => { const [lab, cls] = KC[x.kind] || ["NOTE", "n"]; const lk = BYPRINT[x.lg] || Object.keys(DK).find(q => DK[q] === x.lg);
    return `<div class="mv"><span class="k">${k ? "" : `<span class="lgtag" style="color:${LCOL[lk] || "var(--ink)"}">${esc(DK[lk] || x.lg)}</span> `}<span class="chip ${cls}">${lab}</span></span><span class="t">${esc(x.text)}${x.due ? ` <span class="mute">· ${esc(x.due)}</span>` : ""}</span><button type="button" class="x" data-mvx="${esc(x.id)}" aria-label="Remove this line">×</button></div>`; }).join("") +
    (k ? "" : `<p class="note">Your decided plan, kept by Claude${MV && MV.updated ? " · updated " + esc(MV.updated) : ""}. × hides a line on every device.</p>`);
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
  const xr = [["y", "YAHOO"], ["r", "RATCLIFFE"], ["k", "KOERNER"], ["c", "CLAY"]].map(([s, lab]) => { const v = chance(L, s), p0 = pv ? pv[s] : null;
    const mv = p0 === null || p0 === undefined || p0 === v ? "" : `<em class="${v > p0 ? "up" : "dn"}">${v > p0 ? "▲" : "▼"}${Math.abs(v - p0)}</em>`; return `<div><b>${v}%</b><span>${lab}</span> ${mv}</div>`; }).join("");
  const ys = [chance(L, "y"), chance(L, "r"), chance(L, "k"), chance(L, "c")], split = Math.max(...ys) - Math.min(...ys);
  const anyStart = [...L.players, ...L.oppPlayers].some(started);
  const splitHtml = split >= 20 && opL.length + meL.length > 0 ? `<div class="warn">The sources split by ${split} points on this game${anyStart ? "" : " - check why before kickoff"}.</div>` : "";
  /* points since the last read */
  let since = "";
  if (pv){ const dm = me - pv.me, dop = op - pv.op, moved = [];
    if (pv.pl) for (const [side, list] of [["you", L.players], ["opp", L.oppPlayers]]) for (const p of list){ const was = pv.pl[p.name]; if (was === undefined) continue; const d = pts(p) - was; if (Math.abs(d) >= .5) moved.push({n: p.name, d, side}); }
    moved.sort((a, b) => Math.abs(b.d) - Math.abs(a.d));
    since = fold("since-" + SLUG[k], "Since last read", `${sgn(dm)} / ${sgn(dop)}`, `<div class="takes">Since the ${esc(ptTime(prev.t))} read: you <b class="${dm >= 0 ? "up" : "dn"}">${sgn(dm)}</b> · opponent <b>${sgn(dop)}</b> · net <b class="${dm - dop >= 0 ? "up" : "dn"}">${sgn(dm - dop)}</b> (Yahoo live scores).</div>` +
      (moved.length ? `<div class="sub">Who moved</div>` + moved.map(x => `<div class="mv"><span class="k">${x.side === "you" ? "You" : '<span class="mute">Opp</span>'}</span><span class="t">${esc(x.n)}</span><span class="num ${x.d >= 0 ? "up" : "dn"}">${sgn(x.d)}</span></div>`).join("") : `<p class="note">Nobody moved half a point or more.</p>`)); }
  /* read-by-read chance */
  const es = trailEntries().filter(e => e.w === S.week && e.lg[k]);
  const rbr = es.length >= 2 ? `<div class="chartbox"><div class="ct">Chance to win this week, read by read</div>${lineChart([["y", "#EEF1F6", ""], ["r", HEX[k], ""], ["k", HEX[k], "4 3"], ["c", "#8A93A6", "2 3"]].map(([s, col, dash]) => ({col, dash, w: s === "y" ? 2.5 : 1.6, pts: es.map((e, i) => [i, e.lg[k][s]])})), es.map(e => PT(e.t, {weekday: "short", hour: "numeric"}).replace(" ", "")))}
      <div class="key"><span><i style="border-color:#EEF1F6"></i>Yahoo</span><span><i style="border-color:${HEX[k]}"></i>Ratcliffe</span><span><i class="dot" style="border-color:${HEX[k]}"></i>Koerner</span><span><i class="dot" style="border-color:#8A93A6"></i>Clay</span></div></div>` : "";
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
  const road = `<div class="funnel"><div><b>${pcs(b.playoff)}</b><span>PLAYOFFS</span></div><div><b>${pcs(b.semis)}</b><span>SEMIS</span></div><div><b>${pcs(b.final)}</b><span>FINAL</span></div><div><b>${pcs(b.title)}</b><span>TITLE</span></div></div>
    <p class="note">${esc(c.rec_now || m.rec || "")} · ${c.stand_now ? "standing " + c.stand_now : ""}${b.wins ? " · " + b.wins.toFixed(1) + " expected wins" : ""}${b.seed ? " · likeliest seed " + b.seed : ""}. Season odds from ${esc(c.note ? "the championship simulator" : "the simulator")}, built ${esc(c.built || "")}.</p>
    <div class="sub">Pickups tested (${mvs.length})</div>${mvs.length ? mvs.map(x => `<div class="pk"><b>Add ${esc(x.add)}</b> (${esc(x.pos || "")} ${esc(x.nfl || "")}, ${esc(x.acq || "")}) · drop ${esc(x.drop)}: playoff odds <b class="${x.d_playoff >= 0 ? "up" : "dn"}">${sgn(x.d_playoff * 100)} pts</b>, title ${sgn((x.d_title || 0) * 100)} pts, ${sgn(x.d_wins || 0, 2)} wins.<br><span class="mute">${esc(x.drop)} ${esc(x.drop_role || "")}${x.block && x.block.rival ? " · blocks " + esc(x.block.rival) : ""}</span></div>`).join("") : `<p class="note">Nothing tested clears the bar right now.</p>`}
    ${(c.not_worth || []).length ? `<p class="note">${c.not_worth.length} other adds tested and not worth it (under half a point of playoff odds).</p>` : ""}
    <div class="sub">Injury calls (${calls.length})</div>${calls.length ? calls.map(x => { const best = (x.options || [])[0];
      return `<div class="pk"><b>${esc(x.starter)}</b> <span class="chip ${/^(O|D)$/.test(x.status) ? "r" : "y"}">${esc(x.status)}</span> locks ${esc(x.locks)}: this week ${pc(x.week_now)} with him, ${pc(x.week_if_out)} if out${best ? `; best fill <b>${esc(best.add)}</b> for ${esc(best.drop)} (${sgn((best.d_week || 0) * 100)} this week)` : ""}. Season playoff odds if he sits: ${pc(x.if_out && x.if_out.playoff)}.</div>`; }).join("") : `<p class="note">No starter on the injury report.</p>`}
    <div class="sub">Trades screened (${trades.length} of ${c.trades_screened || 0})</div>${trades.length ? trades.map(x => `<div class="pk">Give <b>${esc((x.give || []).join(" + "))}</b> for <b>${esc(x.get)}</b>: playoff odds ${sgn(x.d_playoff * 100)} pts, title ${sgn((x.d_title || 0) * 100)} pts.</div>`).join("") : `<p class="note">${esc(c.trade_rules || "No trade clears both sides.")}</p>`}
    ${(c.race || []).length ? `<div class="sub">The race</div><div class="scroll"><table class="tbl"><tr><th>Team</th><th>Record</th><th>Playoffs</th><th>Title</th></tr>${c.race.map(r => `<tr class="${r.me ? "me" : ""}"><td>${esc(r.team)}</td><td>${esc(r.rec)}</td><td>${pcs(r.playoff)}</td><td>${pcs(r.title)}</td></tr>`).join("")}</table></div>` : ""}
    ${(c.path || []).length ? `<div class="sub">The road ahead</div><div class="heat">${c.path.map(g => { const v = g.win, col = v >= .6 ? "#4FD08A" : v >= .45 ? "#F7C531" : "#FF6B72"; return `<div style="background:${col}"><span>WK ${g.wk}</span>${pc(v)}</div>`; }).join("")}</div><p class="note">${c.path.map(g => "Wk " + g.wk + " " + esc(g.opp)).join(" · ")}</p>` : ""}
    ${(c.worth || []).length ? `<div class="sub">What your bench is for</div>` + c.worth.map(x => `<div class="pk"><b>${esc(x.name)}</b> ${esc(x.pos)}: ${esc(x.role)}. Dropping him would ${(x.d_playoff || 0) < -.0005 ? "cost " + Math.abs(x.d_playoff * 100).toFixed(1) + " pts of" : (x.d_playoff || 0) > .0005 ? "add " + (x.d_playoff * 100).toFixed(1) + " pts to" : "barely move"} playoff odds.</div>`).join("") : ""}`;
  const roadCnt = `${mvs.length} pickups · ${calls.length} injury · ${trades.length} trades`;

  /* season analytics */
  const hist = (m.sim_hist || []).map(h => [h[0], h[2]]);
  const acc = (M && M.acc && M.acc.src) || {};
  const accRows = Object.entries(acc).map(([s, wk]) => { const ws = Object.entries(wk); const last = ws[ws.length - 1]; const avg = ws.reduce((a, [, v]) => a + v[0], 0) / (ws.length || 1);
    return [s, last ? last[0] : "", last ? last[1][0] : null, avg, ws.length]; }).sort((a, b) => a[3] - b[3]);
  const byes = {}; for (const r of ((M && M.rosters && M.rosters.t && M.rosters.t[DKP[k]]) || [])){ const wk = (M.byes || {})[r[3]]; if (wk) for (const w of wk) if (w >= (S.week || 0)) (byes[w] = byes[w] || []).push(r[0]); }
  const analytics = `${m.viz && m.viz.weeks ? `<div class="sub">Chance to win, week by week</div><div class="heat">${Object.entries(m.viz.weeks).map(([w, v]) => { const col = v >= .6 ? "#4FD08A" : v >= .45 ? "#F7C531" : "#FF6B72"; return `<div style="background:${col}"><span>WK ${w}</span>${pc(v)}</div>`; }).join("")}</div>` : ""}
    ${hist.length >= 2 ? `<div class="sub">Playoff odds over time</div>${lineChart([{col: HEX[k], pts: hist.map((h, i) => [i, h[1] * 100])}], hist.map(h => PT(h[0], {month: "numeric", day: "numeric"})), 100)}` : `<p class="note">Playoff odds history: ${hist.length} point${hist.length === 1 ? "" : "s"} so far (${hist.length ? pcs(hist[0][1]) : "–"}); the line draws from the second build on.</p>`}
    ${Object.keys(byes).length ? `<div class="sub">Byes ahead</div>${Object.entries(byes).sort((a, b) => a[0] - b[0]).map(([w, ns]) => `<div class="mv"><span class="k">Wk ${w}</span><span class="t">${esc(ns.join(", "))}</span></div>`).join("")}` : ""}
    ${accRows.length ? `<div class="sub">Who's been most accurate</div><table class="tbl"><tr><th>Source</th><th>Last graded</th><th>Season avg</th><th>Weeks</th></tr>${accRows.map(r => `<tr><td>${esc(r[0][0].toUpperCase() + r[0].slice(1))}</td><td>${r[2] === null ? "–" : r[2].toFixed(2)} <span class="mute">wk ${esc(r[1])}</span></td><td>${r[3].toFixed(2)}</td><td>${r[4]}</td></tr>`).join("")}</table><p class="note">${esc((M.acc || {}).note || "")}. All four leagues together.</p>` : ""}`;

  /* expert cards */
  const xp = (m.xp && m.xp.players) || {};
  const xpc = Object.entries(xp).filter(([n, v]) => v && (v.r !== undefined || v.k !== undefined)).map(([n, v]) => { const ns = [v.r, v.k, v.c].filter(x => x !== null && x !== undefined); const sp = ns.length ? Math.max(...ns) - Math.min(...ns) : 0;
    return {n, v, sp}; }).filter((x, i, arr) => arr.findIndex(y => y.v.pos === x.v.pos && y.v.r === x.v.r && y.v.k === x.v.k && y.v.c === x.v.c) === i).sort((a, b) => b.sp - a.sp);
  const experts = xpc.length ? `<div class="xpc">${xpc.map(({n, v, sp}) => `<div class="c${sp >= 3 ? " split" : ""}"><b>${esc(n)}</b><div class="why">${esc(v.pos || "")} · ${esc(v.why || "")}${sp >= 3 ? " · split " + sp.toFixed(1) : ""}</div>
      <div class="ns"><span>R ${f1(v.r)}</span><span>K ${f1(v.k)}</span><span>C ${f1(v.c)}</span></div></div>`).join("")}</div><p class="note">This week in ${DK[k]} scoring: R = Ratcliffe (FTN, leads), K = Koerner (FantasyLabs), C = Clay (ESPN). Gold edge = the experts split by 3+ points. ${esc((m.experts || {}).read ? "Ranks read " + m.experts.read : "")}</p>
      ${((m.experts || {}).rising || []).length ? `<div class="sub">Moving up</div>${m.experts.rising.map(t => `<div class="pk">${esc(t)}</div>`).join("")}` : ""}
      ${((m.experts || {}).sliding || []).length ? `<div class="sub">Sliding</div>${m.experts.sliding.map(t => `<div class="pk">${esc(t)}</div>`).join("")}` : ""}` : `<div class="empty">No expert numbers for this league yet.</div>`;

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
    <div class="chd"><span class="lgname">${esc(LGN[k])}</span><span class="dkt">${DK[k]}</span><span class="vs">vs</span><span class="opp">${esc(L.opp)}</span></div>
    <div class="recl">${esc(rec)}</div>
    ${scoreHtml}${takes}${seatHtml}
    <div class="xrow">${xr}</div><p class="note">Chance to win this week, best lineup both sides. Ratcliffe leads every decision number.</p>${splitHtml}
    ${since}${rbr}${rng}
    ${fold("mv-" + SLUG[k], "Your moves", notes.length, movesHtml(k))}
    ${fold("road-" + SLUG[k], "Road to the championship", roadCnt, road, calls.length > 0)}
    ${fold("ana-" + SLUG[k], "Season analytics", "", analytics)}
    ${fold("xp-" + SLUG[k], "Your players, every expert", xpc.filter(x => x.sp >= 3).length + " splits", experts)}
    ${fold("wx-" + SLUG[k], "Game weather", wxs.filter(w => w.flag).length ? wxs.filter(w => w.flag).length + " red" : wxs.length + " games", wx, wxs.some(w => w.flag))}
    ${fold("al-" + SLUG[k], "Alerts", al.length ? `${al.filter(x => x.color === "red").length} act now · ${al.filter(x => x.color === "gold").length} monitor · ${al.filter(x => x.color === "grey").length} noted` : "none", `<div id="alb-${SLUG[k]}">${alertsBlock(k)}</div>`, al.some(x => x.color === "red"))}
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
  box.innerHTML = out.length ? `<div class="need">${out.map(o => `<button type="button" class="nd ${o.col}" ${o.aid ? `data-goal="${esc(o.aid)}"` : `data-jump="${SLUG[o.k]}"`}><span class="lgtag" style="color:${LCOL[o.k] || "var(--ink)"}">${DK[o.k] || ""}</span><span class="tx">${o.html}</span>${o.cd || o.cl ? `<span class="cd">${esc(o.cd)}<small>${esc(o.cl)}</small></span>` : ""}</button>`).join("")}</div>`
    : `<div class="allclear">Nothing needs you right now: no free agent to grab before lock, no empty seat, no act-now alert.</div>`;
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
  $("#moves").innerHTML = movesHtml(null);
  boards();
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
