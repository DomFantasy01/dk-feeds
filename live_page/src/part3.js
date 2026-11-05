/* Dark Knight Live - rebuilt Nov 4-5 2026 after the old page was lost. Source of truth: dk-feeds/live_page/dark_knight_live.html */
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
      <div class="main"><div class="w"><span class="age">${age}</span>${esc(PT(x.first_seen, {month: "short", day: "numeric", hour: "numeric", minute: "2-digit"}))}</div><div class="t">${esc(x.title)}</div><div class="w">${esc(x.own || "")}${x.by ? " · " + esc(x.by) : ""}</div></div></div>
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
  $("#wk").textContent = "NFL WEEK " + (S.week || "");
}
let HC_ALL = false;
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
function meters(){
  if (!S || !S.leagues){ return; }
  const prev = prevEntry();
  $("#meters").innerHTML = KEYS.map(k => { const L = lgS(k); if (!L) return "";
    const m = lgM(k), y = chance(L, "y"), live = aFor(k, aLive), w = worst(live);
    const arrow = (src, v) => { const pv = prev && prev.lg[k] ? prev.lg[k][src] : null; if (pv === null || pv === undefined || v === pv) return ""; return v > pv ? `<em class="up">▲</em>` : `<em class="dn">▼</em>`; };
    const po = m.champ && m.champ.base ? m.champ.base.playoff : (m.sim ? m.sim.playoff : null);
    return `<div class="mtr" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}" role="button" tabindex="0" aria-label="${DK[k]} details">
      <div class="lgn">${esc(LGN[k])}</div><div class="dk">${DK[k]}</div>${dial(y, HEX[k])}
      <div class="pct">${y}%${arrow("y", y)}</div><div class="src">YAHOO · BEST LINEUP</div>
      <div class="xps"><div><span>RATCLIFFE</span><b>${chance(L, "r")}%</b></div><div><span>KOERNER</span><b>${chance(L, "k")}%</b></div><div><span>CLAY</span><b>${chance(L, "c")}%</b></div></div>
      <div class="mrow"><div class="tube"><div class="tb"><i style="width:${po === null ? 0 : Math.max(2, po * 100)}%"></i></div><span>PLAYOFFS ${pcs(po)}</span></div>
        <span class="bell ${w}" title="${live.length} open alerts">${bellSvg}${live.length}</span></div>
      <div class="mstate">${settled(L) ? verdict(score(L.players) - score(L.oppPlayers)) : esc(L.state || "")}</div></div>`; }).join("");
  const kick = nextKick();
  $("#sch").innerHTML = KEYS.map(k => { const L = lgS(k); if (!L) return ""; const y = chance(L, "y"), pv = prev && prev.lg[k] ? prev.lg[k].y : null;
    const mv = pv === null || pv === undefined ? "" : y === pv ? "" : `<span class="${y > pv ? "up" : "dn"}">${y > pv ? "▲" : "▼"}${Math.abs(y - pv)}</span>`;
    return `<button type="button" class="sc" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}"><div class="t">${DK[k]}</div><div class="s">${f1(score(L.players))}–${f1(score(L.oppPlayers))}</div>
      <div class="p"><b>${y}%</b> ${mv}</div><div class="p">${leftOf(L.players).length}/${leftOf(L.oppPlayers).length} left</div></button>`; }).join("");
  $("#sbar").innerHTML = `<span>Yahoo read ${esc(ago(S.stamp))}</span><span>${kick ? "Next kickoff " + esc(kick) : "No games left this week"}</span><button type="button" data-jump="top">Top</button>`;
}
function nextKick(){ const ks = ((M && M.kicks) || []).map(x => new Date(Array.isArray(x) ? x[0] : x).getTime()).filter(t => t > Date.now()).sort((a, b) => a - b);
  if (!ks.length) return ""; const m = Math.round((ks[0] - Date.now()) / 6e4); const d = Math.floor(m / 1440), h = Math.floor(m % 1440 / 60), mi = m % 60;
  return (d ? d + "d " : "") + (h || d ? h + "h " : "") + mi + "m"; }
