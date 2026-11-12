
var XACC = {r: {rk: 4, lead: true}, k: {rk: 2}, c: {}, v: {}, b: {test: true}}, XACC_ASOF = "Nov 8, 9:10 PM PT";
/* Nov 8 (Dom): Clay and Vegas aren't in FantasyPros' contest, so their spot shows our own grade - average points missed per player in the latest graded week (lower is better) */
function xGrade(s2){ try { const nm = {r: "ratcliffe", k: "koerner", c: "clay", v: "vegas", b: "rotoballer"}[s2], src = (typeof M !== "undefined" && M && M.acc && M.acc.src) || {}, wk = src[nm] || {};
  const ws = Object.keys(wk).map(Number).sort((a, b) => a - b); if (!ws.length) return null; const w = ws[ws.length - 1]; return {w, miss: wk[String(w)][0], n: wk[String(w)][1]}; } catch (e) { return null; } }
/* Dark Knight Live - rebuilt Nov 4-5 2026 after the old page was lost. Nov 5: needs-you panel, alert preview + finder, deadline chips, deep links, keys. Source of truth: dk-feeds/live_page/dark_knight_live.html */
"use strict";
const KEYS = ["MOST", "WINNERS", "HERS&HIS", "NEXTDOOR"];
const DK = {MOST: "DK1", WINNERS: "DK2", "HERS&HIS": "DK3", NEXTDOOR: "DK4"};
const DKP = {MOST: "DK I", WINNERS: "DK II", "HERS&HIS": "DK III", NEXTDOOR: "DK IV"};          /* printed form, as the alerts carry it */
const LGN = {MOST: "Most Important", WINNERS: "Winners & Sinners", "HERS&HIS": "Hers His Ver 2.0", NEXTDOOR: "Murrieta NextDoor"};
const LCOL = {MOST: "var(--l1)", WINNERS: "var(--l2)", "HERS&HIS": "var(--l3)", NEXTDOOR: "var(--l4)"};
const HEX = {MOST: "#5B9BF5", WINNERS: "#F0763A", "HERS&HIS": "#A98BFF", NEXTDOOR: "#4FD6CA"};
const SLUG = {MOST: "dk1", WINNERS: "dk2", "HERS&HIS": "dk3", NEXTDOOR: "dk4"};
const BYPRINT = {"DK I": "MOST", "DK II": "WINNERS", "DK III": "HERS&HIS", "DK IV": "NEXTDOOR"};
const LIVE_SYNC_TASK = "trig_014As1cm2kT6H6bXFSbQvJL6";   /* Refresh = pull the latest Dispatch build into this page */
const RSRV = "Claude Code Remote";

let S = null, M = null, A = null, MK = {}, H = null, TR = null, MV = null, DB = null, PK = null;
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const f1 = (v) => (v === null || v === undefined || isNaN(v)) ? "–" : Number(v).toFixed(1);
/* Nov 8 (Dom): win probability always two digits - 01%, not 1% */
const wp2 = (v) => (v === null || v === undefined || isNaN(v)) ? "–" : String(Math.round(+v)).padStart(2, "0");
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
const isLive = (p) => !isDone(p) && /(1st|2nd|3rd|4th|Half|OT|End|Q\d|In progress|Playing)/i.test(p.when || "");   /* Nov 8: the Dispatch read says "In progress" */
/* Nov 8 (Dom, Waddle): in-game status from the fast RotoWire news (models.ingame, written by sync_models.py) - "out" = ruled out
   mid-game (red, no more points counted), "trbl" = questionable to return / being checked (amber). Today's items only. */
const igOf = (p) => { const I = M && M.ingame; if (!I || !I.players) return null;
  const d = PT(new Date().toISOString(), {month: "long", day: "numeric", year: "numeric"}); if (I.day && I.day !== d) return null;
  return I.players[norm(p.name)] || null; };
const isOut = (p) => /^(O|IR|IR-R|NA|SUSP|PUP|COV)$/i.test((p.status || "").trim()) || ((igOf(p) || {}).s === "out" && !isDone(p));
const pts = (p) => (p.actual === null || p.actual === undefined) ? 0 : +p.actual;
const started = (p) => (isDone(p) && !/^(Bye|No game)/i.test((p.when || "").trim())) || isLive(p);   /* Nov 11 (Dom): a man on bye has not "started" - it was flipping DK4 to LIVE 0.0 TIED before kickoff */
/* each source's projected final for one man: Yahoo's live projection, or the expert's number (pm: [Ratcliffe, Clay, Koerner, Vegas]) */
const SRCI = {r: 0, c: 1, k: 2, v: 3, b: 4};   /* Nov 8: b = RotoBaller (testing) */   /* Nov 7 (Dom): v = Vegas props */
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
  const anyStarted = [...L.players, ...L.oppPlayers].some(p => isLive(p) || /^(Fin|Final)/i.test((p.when || "").trim()));   /* Nov 11: a man on BYE is not a started game - it flipped DK4 to the as-set read (opponent's empty kicker) and showed 84% instead of 70% */
  if (!anyStarted && src !== "y"){
    const set = (M && M.best && M.best[L.key] && (M.best[L.key].bestn || M.best[L.key].set)) || {};   /* Nov 10 (Dom): best lineups, both sides */
    const v = src === "r" ? set.ratcliffe : src === "k" ? set.koerner : src === "v" ? set.vegas : src === "b" ? set.rotoballer : src === "g" ? set.gotham : (set.clay ?? set.gotham);   /* the build's best-lineup number, both sides */
    if (v !== null && v !== undefined) return +v;
  }
  if (src === "y") return +L.pct;
  return liveModel(L, src);
}
/* the same spread model run on one source's projected finals; for "y" it gives the chance Yahoo's own projections imply */
function liveModel(L, src){
  const pm = (M && M.pm && M.pm[L.key]) || {};
  const me = L.players.reduce((a, p) => a + manFinal(p, src, pm), 0), op = L.oppPlayers.reduce((a, p) => a + manFinal(p, src, pm), 0);
  const remain = [...L.players, ...L.oppPlayers].reduce((a, p) => a + (isDone(p) || isOut(p) ? 0 : Math.max(0, manFinal(p, src, pm) - pts(p))), 0);
  const full = [...L.players, ...L.oppPlayers].reduce((a, p) => a + Math.max(1, manFinal(p, src, pm)), 0) || 1;
  const sd = Math.max(1.5, 30 * Math.sqrt(Math.min(1, remain / full)));   /* the spread shrinks as the week is played */
  if (remain < .05) return me > op ? 100 : me < op ? 0 : 50;
  return Math.round(phi((me - op) / sd) * 100);
}
const finals = (L) => ({me: L.players.reduce((a, p) => a + manFinal(p, "y"), 0), op: L.oppPlayers.reduce((a, p) => a + manFinal(p, "y"), 0)});
const score = (list) => list.reduce((a, p) => a + pts(p), 0);
/* Nov 8 (Dom): only a seat he can still fix - a man whose game has kicked off can't be swapped, so he is not an empty-seat alert */
const emptySeats = (L) => L.players.filter(p => !isDone(p) && !isLive(p) && !(teamKo(p.tm) && Date.now() >= teamKo(p.tm)) && (isOut(p) || /^D$/i.test(p.status || "") || ((+p.proj || 0) === 0 && !(expertProj(p) > 0) && !isLive(p))));
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
   one glass orb per source, stacked top to bottom under the Yahoo dial, Vegas first. The bezel ring starts at the bottom and climbs up the left side like a clock hand (25% = left, 50% = top, 75% = right; Dom, Nov 7)
   and takes its color from the red-amber-green scale; a small dot on the bezel marks where the week started; the number sits
   behind a glass sheen; the week's change rides beside it. */
const heat = (v) => { v = Math.max(0, Math.min(100, +v || 0)); const L = (a, b, t) => Math.round(a + (b - a) * t);
  const [c0, c1, t] = v < 50 ? [[255, 77, 87], [247, 179, 43], v / 50] : [[247, 179, 43], [79, 208, 138], (v - 50) / 50];
  return `rgb(${L(c0[0], c1[0], t)},${L(c0[1], c1[1], t)},${L(c0[2], c1[2], t)})`; };
/* Nov 10 8:35 AM (Dom): a clear, shiny glass bubble - no ring, no needle - with the chance to win inside (green 55%+, amber 45-55, red under 45) */
function glassBubble(v, id){
  v = Math.max(0, Math.min(100, +v || 0)); const g = "gb" + id, col = v >= 55 ? "#3DDC84" : v >= 45 ? "#F7B32B" : "#FF4D57";
  return `<svg viewBox="0 0 48 48" aria-hidden="true"><defs>
    <radialGradient id="${g}a" cx="50%" cy="42%" r="62%"><stop offset="0" stop-color="#2A3A5E" stop-opacity=".55"/><stop offset=".7" stop-color="#16213A" stop-opacity=".75"/><stop offset="1" stop-color="#0A1020" stop-opacity=".95"/></radialGradient>
    <radialGradient id="${g}r" cx="50%" cy="50%" r="50%"><stop offset=".78" stop-color="${col}" stop-opacity="0"/><stop offset="1" stop-color="${col}" stop-opacity=".45"/></radialGradient>
    <linearGradient id="${g}h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <radialGradient id="${g}b" cx="50%" cy="100%" r="60%"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
    <ellipse cx="24" cy="45.5" rx="13" ry="1.8" fill="#000" opacity=".35"/>
    <circle cx="24" cy="23" r="21" fill="url(#${g}a)"/>
    <circle cx="24" cy="23" r="21" fill="url(#${g}r)"/>
    <circle cx="24" cy="23" r="21" fill="none" stroke="rgba(255,255,255,.35)" stroke-width=".8"/>
    <ellipse cx="24" cy="38" rx="12" ry="5" fill="url(#${g}b)"/>
    <ellipse cx="19" cy="11.5" rx="11" ry="6.5" fill="url(#${g}h)" transform="rotate(-18 19 11.5)"/>
    <circle cx="33" cy="13" r="1.6" fill="#fff" opacity=".7"/>
    <text x="24" y="29.5" text-anchor="middle" font-family="Bebas Neue,Arial Narrow,sans-serif" font-size="19" fill="${col}" letter-spacing=".3" style="paint-order:stroke" stroke="#0A1020" stroke-width=".6">${wp2(v)}</text></svg>`;
}
function glassOrb(v, v0, tint, id, gold){
  v = Math.max(0, Math.min(100, +v || 0)); const c = 18, r = 15.2, C = 2 * Math.PI * r, col = heat(v), g = "o" + id;
  let dot = ""; if (v0 !== null && v0 !== undefined && !isNaN(v0)){ const a = (Math.max(0, Math.min(100, v0)) / 100) * 2 * Math.PI + Math.PI / 2;
    dot = `<circle cx="${(c + r * Math.cos(a)).toFixed(2)}" cy="${(c + r * Math.sin(a)).toFixed(2)}" r="1.9" fill="#0B1222" stroke="#EEF1F6" stroke-width=".9"/>`; }
  return `<svg viewBox="0 0 36 36" aria-hidden="true"><defs>
    <radialGradient id="${g}b" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="#121B30"/><stop offset="1" stop-color="#121B30"/></radialGradient>
    <linearGradient id="${g}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="${g}f" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.3"/></filter></defs>
    ${gold ? `<circle cx="${c}" cy="${c}" r="17.3" fill="none" stroke="#EFD23E" stroke-opacity=".45" stroke-width=".8"/>` : ""}
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#1C2A48" stroke-width="2.8"/>
    <line x1="${c}" y1="${c - r - 2.4}" x2="${c}" y2="${c - r + 2.4}" stroke="#8A93A6" stroke-width=".8" opacity=".8"/><line x1="${c}" y1="${c + r - 2.4}" x2="${c}" y2="${c + r + 2.4}" stroke="#8A93A6" stroke-width=".8" opacity=".5"/>
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${col}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="${(C * v / 100).toFixed(2)} ${C.toFixed(2)}" transform="rotate(90 ${c} ${c})" opacity=".55" filter="url(#${g}f)"/>
    <circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${col}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="${(C * v / 100).toFixed(2)} ${C.toFixed(2)}" transform="rotate(90 ${c} ${c})"/>${dot}
    <circle cx="${c}" cy="${c}" r="12.4" fill="url(#${g}b)" stroke="rgba(255,255,255,.16)" stroke-width=".7"/>
    <text x="${c}" y="${c + 4.6}" text-anchor="middle" font-family="Bebas Neue,Arial Narrow,sans-serif" font-size="13.5" fill="#fff" letter-spacing=".3">${wp2(v)}</text></svg>`;
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
  /* Nov 8 8:30 PM: the real Live syncs - hourly at :25 (4:25 AM-11:25 PM), plus game-window syncs every 20 min with it:
     Sunday :45 (9:45 AM-8:45 PM) and :05 (10:05 AM-9:05 PM); Monday and Thursday :45 (4:45-8:45 PM) and :05 (5:05-9:05 PM) */
  sync(d){ const R = (a, b, m) => Array.from({length: b - a + 1}, (_, i) => [a + i, m]);
    return [...R(4, 23, 25), ...(d === 0 ? [...R(9, 20, 45), ...R(10, 21, 5)] : d === 1 || d === 4 ? [...R(16, 20, 45), ...R(17, 21, 5)] : [])]; }
};
function pacNow(){ const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", {timeZone: "America/Los_Angeles", weekday: "short", hour: "numeric", minute: "numeric", hour12: false}).formatToParts(new Date()).map(x => [x.type, x.value]));
  return {d: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(p.weekday), m: (+p.hour % 24) * 60 + (+p.minute)}; }
function nextRun(){ const n = pacNow(); let best = null;
  for (let add = 0; add < 2 && best === null; add++){ const d = (n.d + add) % 7;
    for (const [lab, fn] of [["Yahoo read", SCHED.yahoo], ["Live sync", SCHED.sync]]) for (const [h, mi] of fn(d)){ const t = h * 60 + mi + add * 1440;
      if (t > n.m && (best === null || t < best.t)) best = {t, lab}; } }
  if (!best) return ""; const t = best.t % 1440, h = Math.floor(t / 60), mi = t % 60;
  return `${best.t >= 1440 ? "tomorrow " : ""}${(h % 12) || 12}:${String(mi).padStart(2, "0")} ${h < 12 ? "AM" : "PM"} (${best.lab})`; }
/* the next time the Live page gets new data (next Live sync), as "8:45 PM" or "Mon 4:25 AM" */
function nextUpdate(){ const n = pacNow(); let best = null;
  for (let add = 0; add < 3 && best === null; add++){ const d = (n.d + add) % 7; for (const [h, mi] of SCHED.sync(d)){ const t = h * 60 + mi + add * 1440; if (t > n.m && (best === null || t < best)) best = t; } }
  if (best === null) return ""; const t = best % 1440, h = Math.floor(t / 60), mi = t % 60, dd = Math.floor(best / 1440);
  return `${dd ? ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][(n.d + dd) % 7] + " " : ""}${(h % 12) || 12}:${String(mi).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`; }
function nextMins(){ const n = pacNow(); let best = null;   /* minutes to the next scheduled Yahoo read */
  for (let add = 0; add < 2 && best === null; add++){ const d = (n.d + add) % 7; for (const [h, mi] of SCHED.yahoo(d)){ const t = h * 60 + mi + add * 1440; if (t > n.m && (best === null || t < best)) best = t; } }
  return best === null ? null : best - n.m; }
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
    : `<b>${esc(PT(S.stamp, {weekday: "short"}))}, ${esc(PT(S.stamp, {month: "short", day: "numeric"}))} · ${esc(PT(S.stamp, {hour: "numeric", minute: "2-digit"}))}</b>`;
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
/* Nov 8 v5 (Dom, voice walk-through 11:20-11:40): every row lines up straight across the four meters (CSS subgrid), in order -
   DK tag + full league name (two lines) · bell with red / amber / grey counts · the dial, number below the needle, "Win probability" ·
   score box: actual points, colored by win probability (blinks while your men play), white arrow + margin, a dot per starter
   (red out, blinking amber trouble, blinking green playing, green done, grey not yet - the same colors as the card's boxes) ·
   the four experts as glass orbs with names spelled out and their move since the last read · playoff odds for the season. */
const LASTY = {};
const LGSHORT = {MOST: "Most Important", WINNERS: "Winners & Sinners", "HERS&HIS": "Hers & His", NEXTDOOR: "NextDoor"};
const LGFULL = {MOST: "The Most Important Thing in Life", WINNERS: "Winners & Sinners", "HERS&HIS": "Hers and His Version 2.0", NEXTDOOR: "Murrieta NextDoor"};
/* Nov 10 (Dom): RANKED = average chance to win this week of the top three sources by accuracy (the checked ones) */
function rankedOf(X, OCK){ const IDS = {ratcliffe: "r", koerner: "k", clay: "c", vegas: "v", rotoballer: "b", yahoo: "y", gotham: "g"};
  const top = (OCK || []).map(id => IDS[id]).filter(s3 => X[s3] !== null && X[s3] !== undefined && !isNaN(X[s3]));
  return top.length ? {v: top.reduce((a, s3) => a + X[s3], 0) / top.length, top} : null; }
function bigDial(v, col, mark, id, v0, v2){
  /* Nov 11 2:45 PM (Dom: "add more shine, more beauty to that gauge"): glass dial face lit in the league color, glowing gradient
     arc with a gloss line, tapered needles with shadows, metal hub. Same meaning as before: white needle = Yahoo, blue needle =
     RANKED (top three by accuracy), white tick = the experts' middle, dashed ghost needle + thin arc = where Yahoo started the week */
  v = Math.max(0, Math.min(100, +v || 0));
  const cx = 60, cy = 60, r = 44, A = (q) => Math.PI * (1 - q / 100), P = (q, rr) => [cx + rr * Math.cos(A(q)), cy - rr * Math.sin(A(q))], f = (n) => n.toFixed(1);
  const arc = (p0, p1, rr) => { const [x0, y0] = P(p0, rr), [x1, y1] = P(p1, rr); return `M${f(x0)} ${f(y0)} A${rr} ${rr} 0 0 1 ${f(x1)} ${f(y1)}`; };
  const g = "bd" + id;
  let ticks = ""; for (let t = 0; t <= 20; t++){ const maj = t % 10 === 0, mid = t % 2 === 0, [a0, b0] = P(t * 5, r + 8.5), [a1, b1] = P(t * 5, r + (maj ? 14 : mid ? 12 : 10.5));
    ticks += `<line x1="${f(a0)}" y1="${f(b0)}" x2="${f(a1)}" y2="${f(b1)}" stroke="${t === 10 ? "#F4F6FA" : maj ? "#AEB8CE" : mid ? "#56658A" : "#34415F"}" stroke-width="${maj ? 1.5 : mid ? .9 : .6}" stroke-linecap="round"/>`; }
  /* tapered needle: a slim kite from a short tail behind the hub to a sharp tip */
  const needle = (q, len, fill, w) => { const a = A(q), ux = Math.cos(a), uy = -Math.sin(a), px = -uy, py = ux, tip = [cx + ux * len, cy + uy * len], tail = [cx - ux * 7, cy - uy * 7];
    const l = [cx + px * w, cy + py * w], rr = [cx - px * w, cy - py * w];
    return `<path d="M${f(tail[0])} ${f(tail[1])} L${f(l[0])} ${f(l[1])} L${f(tip[0])} ${f(tip[1])} L${f(rr[0])} ${f(rr[1])} Z" fill="${fill}"/>`; };
  let mk = ""; if (mark !== null && mark !== undefined && !isNaN(mark)){ const [a0, b0] = P(mark, r - 7), [a1, b1] = P(mark, r + 7);
    mk = `<line x1="${f(a0)}" y1="${f(b0)}" x2="${f(a1)}" y2="${f(b1)}" stroke="#060A14" stroke-width="4" stroke-linecap="round" opacity=".8"/><line x1="${f(a0)}" y1="${f(b0)}" x2="${f(a1)}" y2="${f(b1)}" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>`; }
  const ghost = v0 !== null && v0 !== undefined && !isNaN(v0) && Math.round(v0) !== Math.round(v) ? (() => { const w0 = Math.max(0, Math.min(100, +v0)), [gx, gy] = P(w0, r - 9);
    return `<path d="${arc(Math.min(w0, v), Math.max(w0, v), r + 8.5)}" stroke="${v > w0 ? "#4FD08A" : "#FF6B72"}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".95"/>
      <line x1="${cx}" y1="${cy}" x2="${f(gx)}" y2="${f(gy)}" stroke="#D9DEE8" stroke-width="1.3" stroke-dasharray="2.4 2.4" opacity=".7"/><circle cx="${f(gx)}" cy="${f(gy)}" r="2" fill="#0B1222" stroke="#D9DEE8" stroke-width="1"/>`; })() : "";
  const rk = v2 !== null && v2 !== undefined && !isNaN(v2) ? `<g filter="url(#${g}d)">${needle(Math.max(0, Math.min(100, +v2)), r - 6, `url(#${g}nb)`, 2.3)}</g>` : "";
  return `<svg class="bdl" viewBox="0 0 120 66" aria-hidden="true"><defs>
    <linearGradient id="${g}" x1="0" x2="1"><stop offset="0" stop-color="#FF4D57"/><stop offset=".5" stop-color="#F7B32B"/><stop offset="1" stop-color="#3DDC84"/></linearGradient>
    <radialGradient id="${g}face" cx="50%" cy="100%" r="100%"><stop offset="0" stop-color="${col}" stop-opacity=".30"/><stop offset=".45" stop-color="#14203C" stop-opacity=".95"/><stop offset="1" stop-color="#0A1020"/></radialGradient>
    <linearGradient id="${g}gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity=".03"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="${g}s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5D6780"/><stop offset=".22" stop-color="#EEF1F7"/><stop offset=".5" stop-color="#8590A8"/><stop offset=".78" stop-color="#F6F8FB"/><stop offset="1" stop-color="#5D6780"/></linearGradient>
    <linearGradient id="${g}nw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#B9C2D4"/></linearGradient>
    <linearGradient id="${g}nb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9BE0FF"/><stop offset="1" stop-color="#2E9BEA"/></linearGradient>
    <radialGradient id="${g}hub" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#9AA5BC"/><stop offset="1" stop-color="#3A4560"/></radialGradient>
    <filter id="${g}f" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="2.4"/></filter>
    <filter id="${g}d" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy=".8" stdDeviation=".9" flood-color="#000" flood-opacity=".7"/></filter></defs>
    <path d="M${cx - r - 17} ${cy} A${r + 17} ${r + 17} 0 0 1 ${cx + r + 17} ${cy} Z" fill="url(#${g}face)"/>
    <path d="M${cx - r - 17} ${cy} A${r + 17} ${r + 17} 0 0 1 ${cx + r + 17} ${cy} Z" fill="url(#${g}gl)"/>
    <path d="${arc(0, 100, r + 17)}" stroke="url(#${g}s)" stroke-width="1.8" fill="none"/>
    <path d="${arc(0, 100, r + 6.5)}" stroke="#2A3656" stroke-width=".8" fill="none"/>
${ticks}
    <path d="${arc(0, 100, r)}" stroke="#0C1426" stroke-width="10.5" fill="none" stroke-linecap="round"/>
    <path d="${arc(0, 100, r)}" stroke="url(#${g})" stroke-opacity=".16" stroke-width="10.5" fill="none" stroke-linecap="round"/>
    <path d="${arc(0, Math.max(1, v), r)}" stroke="url(#${g})" stroke-width="10.5" fill="none" stroke-linecap="round" filter="url(#${g}f)" opacity=".75"/>
    <path d="${arc(0, Math.max(1, v), r)}" stroke="url(#${g})" stroke-width="9" fill="none" stroke-linecap="round"/>
    <path d="${arc(0, Math.max(1, v), r + 2.6)}" stroke="#fff" stroke-opacity=".38" stroke-width=".9" fill="none" stroke-linecap="round"/>
${mk}
    ${ghost}
    ${rk}
    <g filter="url(#${g}d)">${needle(v, r - 4, `url(#${g}nw)`, 2.6)}</g>
    <circle cx="${cx}" cy="${cy}" r="6.6" fill="#0B1222" stroke="url(#${g}s)" stroke-width="1.4"/><circle cx="${cx}" cy="${cy}" r="4.4" fill="url(#${g}hub)"/><circle cx="${cx}" cy="${cy}" r="1.7" fill="${col}"/></svg>`;
}
const isStarter = (p) => !/^(BN|IR|IR\+|NA)$/i.test((p.slot || "").trim());
const isTrouble = (p) => /^(Q|D|GTD|DTD)$/i.test((p.status || "").trim()) || (igOf(p) || {}).s === "trbl";
/* one state for a starter, shared by the meter dots and the card's boxes */
const dotState = (p) => (!isDone(p) && (isOut(p) || (!isLive(p) && (+p.proj || 0) === 0 && !/bye/i.test(p.when || "")))) ? "out" : isTrouble(p) && !isDone(p) ? "trbl" : isLive(p) ? "live" : isDone(p) ? "done" : "pre";
const segs = (list) => list.filter(isStarter).sort((a, b) => SEGORD[dotState(a)] - SEGORD[dotState(b)]).map(p => `<i class="${dotState(p)}" title="${esc((p.slot || "") + " " + p.name + (p.status ? " (" + p.status + ")" : "") + " · " + (p.when || "") + (igOf(p) ? " · " + igOf(p).note + " (RotoWire)" : ""))}"></i>`).join("");
const dots = (list) => list.filter(isStarter).map(p => `<i class="${dotState(p)}" title="${esc((p.slot || "") + " " + p.name + (p.status ? " (" + p.status + ")" : "") + " · " + (p.when || "") + (igOf(p) ? " · " + igOf(p).note + " (RotoWire)" : ""))}"></i>`).join("");
/* Nov 8 1:40 PM (Dom): the scoreboard globe, take 2.
   Your orb's fluid takes the color of Yahoo's chance to win this week (Nov 8 1:45: globe back to black, his orb always gray): green 55% and up, amber 45-55%, red under 45% (FINAL = the real result).
   Inside, two orbs: yours in the league color, his in gray. Solid fluid = points scored, with the wave on top and a soft glowing edge;
   a lighter shade of the same color above it rises to Yahoo's projected final (league scoring). No dotted line.
   Ring = every starter with his position spelled out, yours on the left, his on the right:
   dark green done · light green blinking = playing · amber blinking = something's wrong (Q/D/GTD) ·
   red = out (ruled out) · red blinking = no projection and nobody knows why · gray = still to play. */
/* Nov 10 (Dom, voice): THE PLAYER LIGHTS - one look tells the week. Starters only, his and the opponent's, reset each Tuesday with the new week's lineup.
   green = fine · amber = questionable/doubtful · red = out/IR/suspended/inactive · pink = bye · empty spot or no projection = yellow/red two-tone flash all week
   (and the ACTION light comes on) · solid dark green = his game is over. A light blinks ONLY while that man's game is on (the empty-spot flash is the one exception).
   Statuses come from each Yahoo read. */
const RINGC = {ok: "#3DDC84", live: "#3DDC84", trbl: "#F7B32B", trblon: "#F7B32B", out: "#FF4D57", bye: "#FF7EC8", done: "#1C7A45", empty: "#F7C52B"};
const SEGORD = {live: 0, trblon: 1, empty: 2, out: 3, trbl: 4, bye: 5, ok: 6, done: 7};
const isEmptySpot = (p) => !(p.name || "").trim() || /^\(?\s*empty\s*\)?$/i.test((p.name || "").trim());
const isByeMan = (p) => /bye/i.test(p.when || "");
/* Nov 11 (Dom: ACTION red after the claims): Yahoo's per-player read has no number yet for men added after it ran (Estime, Kiner,
   the new defenses), so they looked like empty seats. Any expert number for him in any league means he's a real starter. */
function expertProj(p){ const PM = (M && M.pm) || {}, n = norm(p.name).toLowerCase().replace(/ (jr|sr|ii|iii|iv)$/, "");
  let best = 0; for (const lg of Object.values(PM)){ const e = lg[n] || lg[norm(p.name).toLowerCase()]; if (e) for (const v of e) if (+v > best) best = +v; } return best; }
const ringState = (p) => {
  if (isEmptySpot(p)) return "empty";
  if (isByeMan(p)) return "bye";
  if (isOut(p)) return "out";
  if (isDone(p)) return "done";
  if (isLive(p)) return isTrouble(p) ? "trblon" : "live";
  if (isTrouble(p)) return "trbl";
  if ((+p.proj || 0) === 0 && !(expertProj(p) > 0)) return "empty";   /* no projection and nobody knows why = a hole, same flash (Nov 11: an expert number counts - a man added this morning has none from Yahoo yet) */
  return "ok"; };
const POSAB = (sl) => { const t = (sl || "").toUpperCase().trim(); return /Q\/W\/R\/T|SUPER|^SF/.test(t) ? "SF" : /W\/R\/T|W\/R|FLEX|R\/W/.test(t) ? "FX" : /DEF|D\/ST|DST/.test(t) ? "DEF" : t.replace(/[^A-Z]/g, "").slice(0, 3) || "?"; };
const STWORD = {ok: "fine, still to play", live: "playing now", trbl: "questionable / doubtful", trblon: "playing - questionable tag", out: "out", bye: "on bye", done: "game over", empty: "EMPTY SPOT / no projection - fill it"};
/* Nov 8 2:50 PM (Dom: "maybe we're better making it a box rather than a circle... be creative"): the scoreboard TANKS.
   One card per league: two tall glass tanks side by side - yours fills in your win color (green 55%+, amber 45-55, red under 45 on
   Yahoo's chance to win this week), his in gray. Solid fluid = points scored (gentle wave, rising bubbles, soft glowing edge on top);
   the lighter shade above it = the rest of Yahoo's projected final. Score + projection sit at the top of each tank.
   A position rail runs down the outside of each tank - one segment per starter in lineup order, labeled, tap for his line:
   dark green done, light green pulsing = playing, amber pulsing = problem, red = out, red pulsing = unknown, gray = still to play.
   The card's frame glows in your win color. */
/* Nov 8 4:45 PM (Dom: "something better... rather than a half-assed test tube"): the scoreboard GAUGE.
   One clean dashboard dial per league, 270 degrees, open at the bottom. Outer ring = you (your win color: green 55%+,
   amber 45-55, red under 45 on Yahoo's chance to win this week), inner ring = him (gray). Solid arc = points scored,
   faint arc beyond it = the rest of Yahoo's projected final, white tick = the projection. Center: your actual score
   (green ahead, red behind), his score under it. In the open bottom: the margin pill, ▲ ahead / ▼ behind, colored.
   Under the dial, two position strips (YOU / HIM, lineup order): dark green done, light green pulsing = playing,
   amber = problem, red = out/unknown, gray = still to play. Tap a block for that player, the dial for the league sheet. */
/* Nov 8 5:55 PM (Dom: "hastily improve the graphics, better chart"): gauge v2 - built for the 4-across phone width (~85px a dial).
   Clean 240-degree dial, no texture or blur: thick outer arc = you (win color), thin inner arc = him (gray); faint arc to Yahoo's
   projected final with a white notch at the projection. Big score in the middle, his under it, projected finals under the dial,
   margin pill, then two taller position strips (YOU / OPP) with readable letters. */
/* Nov 8 6:10 PM (Dom: "dress them up, add color, borders, add to it, make it work"): gauge v3 - an instrument dial.
   Framed face (league-color bezel, graduation ticks every 25 pts with 50/100/150 marked), outer arc = you in your win color
   (green 55%+, amber 45-55, red under 45 on Yahoo's chance to win this week; FINAL = real result), inner arc = him in steel blue,
   faint arcs to each side's Yahoo projected final with a notch. Center: LIVE/FINAL/PRE-GAME, your score (green ahead / red behind),
   his score. Under the dial: margin pill, projected finals, players left each side, and the two position strips. */
function scoreGlobe(L, k, o){
  const id = "sg" + SLUG[k], W = 124, H = 162, CX = 62, CY = 62, LC = HEX[k];
  const top = Math.max(o.pMe, o.pOp, o.me, o.op, 1), step = top > 160 ? 50 : 25, sc = Math.ceil(top * 1.05 / step) * step;
  const fin = o.state === "FINAL", y = o.y, pre = o.state === "NOT STARTED", mg = o.me - o.op;
  const zone = fin ? (o.me >= o.op ? "win" : "lose") : y === null || y === undefined || isNaN(y) ? "mid" : y >= 55 ? "win" : y >= 45 ? "mid" : "lose";
  const ZC = {win: "#3DDC84", mid: "#F7B32B", lose: "#FF4D57"}[zone];
  /* Nov 8 8:10 PM (Dom): PRE-GAME before the first kickoff · LIVE while any game in this matchup is being played ·
     "N GAMES LEFT" when nothing is on but games remain (every game with a starter from either side) · WIN green / LOSS red when final */
  const stL = [...L.players, ...L.oppPlayers].filter(isStarter), anyLive = stL.some(isLive);
  const gLeft = new Set(stL.filter(p => !isDone(p) && !isLive(p)).map(p => gameOf(p.tm) || (p.when || "").trim().toLowerCase() || p.tm)).size;
  const gAll = fin ? 0 : new Set(stL.filter(p => !isDone(p)).map(p => gameOf(p.tm) || (p.when || "").trim().toLowerCase() || p.tm)).size;
  const zw = fin ? (o.me >= o.op ? "WIN" : "LOSS") : pre ? "PRE-GAME" : anyLive || !gLeft ? "LIVE" : gLeft + (gLeft === 1 ? " GAME LEFT" : " GAMES LEFT");
  const PAL = {"#3DDC84": ["#0F7A44", "#3DDC84", "#B4F8D2"], "#F7B32B": ["#A35E00", "#F7B32B", "#FFE6A8"],
    "#FF4D57": ["#9C1424", "#FF4D57", "#FFB3B8"], "#7FA3E0": ["#3B5684", "#7FA3E0", "#CFE0FF"]};
  const MC = pre ? "#AEB6C8" : Math.abs(mg) < .05 ? "#F7B32B" : mg > 0 ? "#3DDC84" : "#FF4D57";
  const A0 = 150, SW = 240, rad = (d) => d * Math.PI / 180, pt = (r, d) => [CX + r * Math.cos(rad(d)), CY + r * Math.sin(rad(d))];
  const arc = (r, f0, f1) => { f0 = Math.max(0, Math.min(1, f0)); f1 = Math.max(f0, Math.min(1, f1)); if (f1 - f0 < .002) return "";
    const d0 = A0 + SW * f0, d1 = A0 + SW * f1, [x0, y0] = pt(r, d0), [x1, y1] = pt(r, d1);
    return `M${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${d1 - d0 > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`; };
  let ticks = ""; for (let v = 0; v <= sc + .01; v += step / 5){ const f = v / sc, d = A0 + SW * f, maj = Math.abs(v % step) < .01 || Math.abs(v % step - step) < .01;
    const [x0, y0] = pt(55.5, d), [x1, y1] = pt(maj ? 59.5 : 57.6, d); ticks += `<line x1="${x0.toFixed(2)}" y1="${y0.toFixed(2)}" x2="${x1.toFixed(2)}" y2="${y1.toFixed(2)}" stroke="${maj ? "#C9D1E2" : "#46557A"}" stroke-width="${maj ? 1.1 : .6}"/>`;
    if (maj && v > 0 && (v % (step * 2) < .01 || sc / step <= 4)){ const [lx, ly] = pt(49.5, d); ticks += `<text x="${lx.toFixed(2)}" y="${(ly + 1.6).toFixed(2)}" text-anchor="middle" class="gtk">${Math.round(v)}</text>`; } }
  /* Nov 9 noon (Dom): your ring starts in the league color and blends into your win color (green 55%+, gold 45-55, red under 45);
     his starts gray and blends into the mirror - green when he's winning, red when he's losing. True gray track, no blue */
  const ring = (r, sw, val, proj, col, side, c0) => { const [dk, md, lt] = PAL[col], fv = val / sc, fp = Math.max(proj, val) / sc, big = side === "m", on = big ? o.meOn : o.opOn;
    const pa = A0 + SW * Math.min(1, proj / sc), [tx0, ty0] = pt(r - sw / 2 - .4, pa), [tx1, ty1] = pt(r + sw / 2 + .4, pa), [ex, ey] = pt(r, A0 + SW * Math.min(1, fv));
    const [gx0, gy0] = pt(r, A0), gfar = Math.hypot(ex - gx0, ey - gy0) > 6, gx1 = gfar ? ex : gx0 + 6, gy1 = gfar ? ey : gy0;
    return `<linearGradient id="${id}${side}g" gradientUnits="userSpaceOnUse" x1="${gx0.toFixed(2)}" y1="${gy0.toFixed(2)}" x2="${gx1.toFixed(2)}" y2="${gy1.toFixed(2)}"><stop offset="0" stop-color="${c0}"/><stop offset=".35" stop-color="${c0}"/><stop offset="1" stop-color="${md}"/></linearGradient>
      <path d="${arc(r, 0, 1)}" fill="none" stroke="#151617" stroke-width="${sw + 1.6}" stroke-linecap="round"/>
      <path d="${arc(r, 0, 1)}" fill="none" stroke="#25272B" stroke-width="${sw}" stroke-linecap="round"/>
      <path d="${arc(r, fv, fp)}" fill="none" stroke="${md}" stroke-opacity=".28" stroke-width="${sw}" stroke-linecap="round" stroke-dasharray="${big ? "2.2 1.4" : "1.6 1.2"}"/>
      ${val > 0 ? `<path d="${arc(r, 0, fv)}" fill="none" stroke="${md}" stroke-opacity=".35" stroke-width="${sw + 3}" stroke-linecap="round" filter="url(#${id}bl)"/>
      <g filter="url(#${id}ab)"><path d="${arc(r, 0, fv)}" fill="none" stroke="url(#${id}${side}g)" stroke-width="${sw}" stroke-linecap="round"/></g>
      <path d="${arc(r - sw * .3, 0, fv)}" fill="none" stroke="#000" stroke-opacity=".28" stroke-width="${(sw * .22).toFixed(2)}" stroke-linecap="round"/>
      ${big ? `<path d="${arc(r + sw * .28, 0, fv)}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="${(sw * .16).toFixed(2)}" stroke-linecap="round"/>` : ""}
      ${on ? `<circle class="gcap on" cx="${ex.toFixed(2)}" cy="${ey.toFixed(2)}" r="${(sw / 2 - .6).toFixed(2)}" fill="#fff" fill-opacity=".92"/>` : ""}` : ""}
      <line x1="${tx0.toFixed(2)}" y1="${ty0.toFixed(2)}" x2="${tx1.toFixed(2)}" y2="${ty1.toFixed(2)}" stroke="#fff" stroke-width="${big ? 1.6 : 1.1}" stroke-linecap="round"/>`; };
  const strip = (list, mine, yy) => { const st = list.filter(isStarter), n = st.length; if (!n) return ""; const x0 = 22.5, x1 = W - 3, g = 1, bw = (x1 - x0 - g * (n - 1)) / n, bh = 11;
    return `<text x="3" y="${(yy + 7.8).toFixed(1)}" class="gsl${mine ? " me" : ""}" style="${mine ? `fill:${LC}` : ""}">${mine ? "TEAM" : "OPNT"}</text>` + st.map((p, i) => { const s = ringState(p), bx = x0 + i * (bw + g), dp = `${SLUG[k]}|${mine ? "m" : "o"}|${i}`;
      const tip = esc((mine ? "Yours: " : "His: ") + (p.slot || "") + " " + p.name + " · " + STWORD[s] + (p.when ? " · " + p.when : ""));
      return `<g class="tap seg ${s}" data-pl="${dp}" role="button" aria-label="${tip}"><rect class="rb" x="${bx.toFixed(2)}" y="${yy}" width="${bw.toFixed(2)}" height="${bh}" rx="2" fill="${RINGC[s]}" filter="url(#${id}ab)"/><rect x="${(bx + .6).toFixed(2)}" y="${yy + .5}" width="${(bw - 1.2).toFixed(2)}" height="${(bh * .42).toFixed(2)}" rx="1.4" fill="#fff" fill-opacity=".22" pointer-events="none"/>
        ${bw >= 6 ? `<text class="gpz ${s}" x="${(bx + bw / 2).toFixed(2)}" y="${(yy + 7.2).toFixed(1)}" text-anchor="middle">${POSAB(p.slot)}</text>` : ""}</g>`; }).join(""); };
  const pmg = o.pMe - o.pOp, sv = f1(o.me), mtxt = pre ? "PROJ " + (Math.abs(pmg) < .05 ? "EVEN" : (pmg > 0 ? "▲" : "▼") + f1(Math.abs(pmg))) : Math.abs(mg) < .05 ? "TIED" : (mg > 0 ? "▲" : "▼") + f1(Math.abs(mg));
  const pw = Math.max(42, mtxt.length * 6.4 + 14), lf = (n) => n === 0 ? "DONE" : n;
  return `<svg class="sglobe sbox sgauge" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(`${DK[k]} score ${f1(o.me)} to ${f1(o.op)}, ${pre ? "not started" : mg >= 0 ? "ahead by " + f1(mg) : "behind by " + f1(-mg)}; Yahoo projected final ${f1(o.pMe)} to ${f1(o.pOp)}; ${o.meL} of yours and ${o.opL} of his left; ${zw}`)}"><defs>
    <radialGradient id="${id}fc" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#1B2848"/><stop offset=".7" stop-color="#0E1629"/><stop offset="1" stop-color="#080D1A"/></radialGradient>
    <radialGradient id="${id}zg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="${MC}" stop-opacity=".22"/><stop offset="1" stop-color="${MC}" stop-opacity="0"/></radialGradient>
    <linearGradient id="${id}bz" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${LC}"/><stop offset=".5" stop-color="${LC}" stop-opacity=".35"/><stop offset="1" stop-color="${LC}"/></linearGradient>
    <filter id="${id}bl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.4"/></filter>
    <filter id="${id}ds" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur in="SourceAlpha" stdDeviation="2.6"/><feOffset dy="3.2"/><feComponentTransfer><feFuncA type="linear" slope=".75"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="${id}ab" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur in="SourceAlpha" stdDeviation=".7"/><feOffset dy="1.3"/><feComponentTransfer><feFuncA type="linear" slope=".85"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="${id}mt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F5FB"/><stop offset=".18" stop-color="${LC}"/><stop offset=".5" stop-color="#2A3656"/><stop offset=".82" stop-color="${LC}"/><stop offset="1" stop-color="#0A0F1C"/></linearGradient>
    <linearGradient id="${id}mi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080F"/><stop offset="1" stop-color="#3A4870"/></linearGradient>
    <radialGradient id="${id}in" cx=".5" cy=".5" r=".5"><stop offset=".82" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
    <linearGradient id="${id}gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset=".55" stop-color="#fff" stop-opacity=".03"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <radialGradient id="${id}ga" cx="50%" cy="42%" r="62%"><stop offset="0" stop-color="#2A3A5E"/><stop offset=".7" stop-color="#16213A"/><stop offset="1" stop-color="#0A1020"/></radialGradient>
    <radialGradient id="${id}gr" cx="50%" cy="50%" r="50%"><stop offset=".74" stop-color="${ZC}" stop-opacity="0"/><stop offset="1" stop-color="${ZC}" stop-opacity=".5"/></radialGradient>
    <linearGradient id="${id}gh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <radialGradient id="${id}gb" cx="50%" cy="100%" r="60%"><stop offset="0" stop-color="#fff" stop-opacity=".26"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <radialGradient id="${id}hb" cx=".38" cy=".3" r=".75"><stop offset="0" stop-color="#2E3D63"/><stop offset=".6" stop-color="#121A30"/><stop offset="1" stop-color="#070B16"/></radialGradient></defs>
    <g filter="url(#${id}ds)"><circle cx="${CX}" cy="${CY}" r="60.6" fill="url(#${id}fc)" stroke="url(#${id}mt)" stroke-width="2.8"/></g>
    <circle cx="${CX}" cy="${CY}" r="58.6" fill="none" stroke="url(#${id}mi)" stroke-width="1"/>
    <circle cx="${CX}" cy="${CY}" r="58.2" fill="url(#${id}in)"/>
    <circle cx="${CX}" cy="${CY}" r="53.6" fill="none" stroke="#24304C" stroke-width=".6"/>
    ${ticks}
    <circle cx="${CX}" cy="${CY}" r="26" fill="url(#${id}zg)"/>
    ${ring(44, 9.5, o.me, o.pMe, ZC, "m", LC)}${ring(32.5, 5, o.op, o.pOp, {win: "#FF4D57", mid: "#F7B32B", lose: "#3DDC84"}[zone], "o", "#8E9196")}
    <ellipse cx="${CX}" cy="${CY + 28.6}" rx="16" ry="2.2" fill="#000" opacity=".4"/>
    <g filter="url(#${id}ds)"><circle cx="${CX}" cy="${CY + 1}" r="26.5" fill="url(#${id}ga)"/></g>
    <circle cx="${CX}" cy="${CY + 1}" r="26.5" fill="url(#${id}gr)"/>
    <circle cx="${CX}" cy="${CY + 1}" r="26.5" fill="none" stroke="#fff" stroke-opacity=".38" stroke-width=".9"/>
    <ellipse cx="${CX}" cy="${CY + 20}" rx="15" ry="6" fill="url(#${id}gb)" pointer-events="none"/>
    <text x="${CX}" y="${CY - 8}" text-anchor="middle" class="gk g2${anyLive && !fin ? " on" : ""}">${anyLive && !fin ? "LIVE" : "SCORE"}</text>
    <text x="${CX}" y="${CY + 9}" text-anchor="middle" class="gsc g2${o.meOn && !fin ? " on" : ""}">${sv}</text>
    <ellipse cx="${CX - 7}" cy="${CY - 15}" rx="12.5" ry="6.6" fill="url(#${id}gh)" transform="rotate(-18 ${CX - 7} ${CY - 15})" pointer-events="none"/>
    <circle cx="${CX + 15.5}" cy="${CY - 8}" r="1.7" fill="#fff" opacity=".7" pointer-events="none"/>
    <path d="M${CX - 52} ${CY - 6} A 52 52 0 0 1 ${CX + 52} ${CY - 6} Q ${CX} ${CY - 22} ${CX - 52} ${CY - 6} Z" fill="url(#${id}gl)" pointer-events="none"/>
    <path id="${id}c1" d="M${pt(37, 150).map(v => v.toFixed(2)).join(" ")} A 37 37 0 0 0 ${pt(37, 30).map(v => v.toFixed(2)).join(" ")}" fill="none"/>
    <path id="${id}c2" d="M${pt(48.5, 150).map(v => v.toFixed(2)).join(" ")} A 48.5 48.5 0 0 0 ${pt(48.5, 30).map(v => v.toFixed(2)).join(" ")}" fill="none"/>
    <text class="gcv fitarc" data-max="${(2 * Math.PI * 37 / 3 * .84).toFixed(1)}"><textPath href="#${id}c1" startOffset="50%" text-anchor="middle"><tspan class="gco">OPNT${pre ? " PROJ" : ""}</tspan> <tspan class="gcn">${f1(pre ? o.pOp : o.op)}</tspan> <tspan style="fill:${MC}">${mtxt.replace(/^PROJ /, "")}</tspan></textPath></text>
    <text class="gcl fitarc" data-max="${(2 * Math.PI * 48.5 / 3 * .8).toFixed(1)}"><textPath href="#${id}c2" startOffset="50%" text-anchor="middle">${gAll ? gAll + (gAll === 1 ? " GAME LEFT" : " GAMES LEFT") : "FINAL"}</textPath></text>
    ${strip(L.players, true, 131)}${strip(L.oppPlayers, false, 145)}</svg>`;   /* Nov 11 4 PM (Dom: too small to read): PROJ / LEFT moved out of the drawing into a readable line under it */
}
/* Nov 8 (Dom): each league name on ONE line - shrink it until it fits its tile, never cut it off */
/* Nov 10 8:00 AM (Dom): keep the four Experts boxes side by side; name + check + points on ONE line, centered - if a box is too
   narrow, drop to one decimal (+6.9), then shrink the names together until every line fits */
function fitExp(){ const xs = [...document.querySelectorAll("#msExp .xo .xtx")]; if (!xs.length) return;
  /* Nov 10 8:04 AM (Dom): one table look - name left, check, points right; ONE font size for every name and number on the page section */
  const bs = xs.map(x => x.querySelector("b")).filter(Boolean), os = xs.map(x => x.querySelector(".opc")).filter(Boolean), all = bs.concat(os);
  all.forEach(e => e.style.removeProperty("font-size")); os.forEach(o => { o.textContent = o.dataset.f2 || o.textContent; });
  const over = () => all.some(e => e.scrollWidth > e.clientWidth + .5);
  if (!over()) return;
  os.forEach(o => { if (o.dataset.f1) o.textContent = o.dataset.f1; });
  let f = parseFloat(getComputedStyle(bs[0]).fontSize) || 7;
  while (over() && f > 4.6){ f -= .2; all.forEach(e => e.style.setProperty("font-size", f + "px", "important")); } }
/* Nov 10 10:10 AM (Dom): the curved wording in the bottom of each scoreboard globe must fit its arc - shrink it until it does */
function fitArcs(){ document.querySelectorAll("#msScore .fitarc").forEach(t => { t.style.removeProperty("font-size"); [...t.querySelectorAll("tspan")].forEach(x => x.style.removeProperty("font-size"));
  const mx = +t.dataset.max || 70; let len = 0; try { len = t.getComputedTextLength(); } catch(_){ return; } if (!len || len <= mx) return;
  const r = mx / len; t.style.setProperty("font-size", (parseFloat(getComputedStyle(t).fontSize) * r).toFixed(2) + "px", "important");
  [...t.querySelectorAll("tspan")].forEach(x => { const f = parseFloat(getComputedStyle(x).fontSize); if (f) x.style.setProperty("font-size", (f * r).toFixed(2) + "px", "important"); }); }); }
function fitNames(){ setTimeout(fitArcs, 0); if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitArcs); setTimeout(fitExp, 0); if (!fitNames.rzx){ fitNames.rzx = 1; addEventListener("resize", () => requestAnimationFrame(fitExp)); } const go = () => { const ns = [...document.querySelectorAll("#msScore .sbh .nm, #msWin .wph .nm, #msExp .wph .nm")]; if (!ns.length) return; ns.forEach(n => n.style.removeProperty("font-size"));
    let f = parseFloat(getComputedStyle(ns[0]).fontSize) || 17; const over = () => ns.some(n => n.scrollWidth > n.clientWidth + .5);
    while (over() && f > 6){ f -= .5; ns.forEach(n => n.style.setProperty("font-size", f + "px", "important")); } };
  const go2 = () => { const ls = []; if (!ls.length) return; ls.forEach(n => n.style.removeProperty("font-size"));
    let f = parseFloat(getComputedStyle(ls[0]).fontSize) || 8; const over = () => ls.some(n => n.scrollWidth > n.clientWidth + .5);
    while (over() && f > 4.5){ f -= .25; ls.forEach(n => n.style.setProperty("font-size", f + "px", "important")); } };
  const both = () => { go(); go2(); };
  both(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(both); if (!fitNames.rz){ fitNames.rz = 1; addEventListener("resize", () => requestAnimationFrame(() => { go(); go2(); })); } }
function meters(){
  if (!S || !S.leagues){ return; }
  const prev = prevEntry(), ORK = ourRanks(), OMISS = ourMiss(), OCK = ourCheck(), OBIAS = ourBias(), OPCT = ourPct();
  /* Nov 9 9:56 AM (Dom): every league's Experts box lists the sources in accuracy order - #1 on top down to #7 - with a green check on the
     top three and nothing under the names; tap the box for the detail (How far off they were) */
  const OLAB = {g: "GOTHAM", v: "VEGAS", r: "RATCLIFFE", k: "KOERNER", y: "YAHOO", c: "CLAY", b: "ROTOBALLER"};
  const ORBS = Object.keys(OLAB).sort((a, b) => (ORK[SRCID[a]] || 99) - (ORK[SRCID[b]] || 99)).map(s2 => [s2, OLAB[s2]]);
  const TILES = KEYS.map(k => { const L = lgS(k); if (!L) return null;
    const m = lgM(k), y = chance(L, "y"), live = aFor(k, aLive);
    const nA = {red: live.filter(x => x.color === "red").length, gold: live.filter(x => x.color === "gold").length}; nA.grey = live.length - nA.red - nA.gold;
    const X = {v: chance(L, "v"), r: chance(L, "r"), k: chance(L, "k"), c: chance(L, "c"), b: chance(L, "b"), g: chance(L, "g"), y: chance(L, "y")};
    const xs = Object.entries(X).filter(([s3]) => !["b", "g", "y"].includes(s3)).map(([, v]) => v).filter(v => v !== null && !isNaN(v)).sort((a, b) => a - b), xmid = xs.length ? (xs[(xs.length - 1) >> 1] + xs[xs.length >> 1]) / 2 : null;
    const mid5 = [y, ...xs].sort((a, b) => a - b)[2];
    const F = finals(L), imp = liveModel(L, "y"), off = Math.abs(y - imp) >= 20;
    const po = m.champ && m.champ.base ? m.champ.base.playoff : (m.sim ? m.sim.playoff : null);
    const goNow = [...L.players, ...L.oppPlayers].some(started), me = score(L.players), op = score(L.oppPlayers), mg = goNow ? me - op : F.me - F.op;
    const onField = L.players.some(isLive), done = settled(L), meL = leftOf(L.players).length, opL = leftOf(L.oppPlayers).length;
    const outs = L.players.filter(isStarter).filter(p => dotState(p) === "out").length;
    const fl = LASTY[k] !== undefined && LASTY[k] !== y; LASTY[k] = y;
    const say = `${DK[k]}, ${LGFULL[k]}: ${y}% win probability this week on Yahoo; experts Vegas ${X.v}%, Ratcliffe ${X.r}%, Koerner ${X.k}%, Clay ${X.c}%. Score ${f1(me)} to ${f1(op)}${goNow ? "" : " (not started)"}, ${meL} and ${opL} players left. Playoff odds for the season ${pcs(po)}. Alerts: ${nA.red} act now, ${nA.gold} monitor, ${nA.grey} noted${outs ? ". " + outs + " starter" + (outs > 1 ? "s" : "") + " out" : ""}. Opens the league card.`;
    const orb = ([s2, nm]) => { const v = X[s2], gap = v - mid5, lvl = Math.abs(gap) >= 5 ? 2 : Math.abs(gap) >= 3 ? 1 : 0, p0 = prev && prev.lg[k] ? prev.lg[k][s2] : null, d = p0 === null || p0 === undefined ? null : Math.round(v - p0);
      return `<div class="xo${lvl ? ` neo ${gap > 0 ? "hi" : "lo"}${lvl === 2 ? " pulse" : ""}` : ""}" title="${nm}: ${ORK[SRCID[s2]] ? "our accuracy rank #" + ORK[SRCID[s2]] + " of " + Object.keys(ORK).length + " (last graded week) · " : ""}${(XACC[s2] || {}).rk ? "FantasyPros 2026 in-season accuracy #" + XACC[s2].rk + " (as of " + XACC_ASOF + ")" : "not in FantasyPros' accuracy contest - our grade: " + (xGrade(s2) ? "missed by " + xGrade(s2).miss.toFixed(1) + " points per player in Week " + xGrade(s2).w + " (" + xGrade(s2).n + " players)" : "not graded yet")} · ${v}% win probability this week${d === null ? "" : ` · ${d === 0 ? "no change" : (d > 0 ? "up " : "down ") + Math.abs(d)} since the ${esc(ptTime(prev.t))} read`}${lvl ? ` · ${Math.abs(Math.round(gap))} points ${gap > 0 ? "above" : "below"} the middle of the five sources` : ""}">
        ${glassOrb(v, null, HEX[k], SLUG[k] + s2, s2 === "v")}<span class="xtx"><b${s2 === "b" ? ' class="lng"' : ""}>${nm}</b>${OCK.includes(SRCID[s2]) ? `<i class="okb" aria-label="top three, used for pickups">&#10003;</i>` : `<i class="okb nil" aria-hidden="true"></i>`}${OMISS[SRCID[s2]] !== undefined ? `<i class="opc ${(OBIAS[SRCID[s2]] ?? OPCT[SRCID[s2]] ?? 0) >= 0 ? "hi" : "lo"}" title="missed by ${OMISS[SRCID[s2]].toFixed(2)} points per player last graded week, ${(OBIAS[SRCID[s2]] ?? OPCT[SRCID[s2]] ?? 0) >= 0 ? "too high" : "too low"}" data-f2="${pmSign(OMISS[SRCID[s2]], OBIAS[SRCID[s2]] ?? OPCT[SRCID[s2]])}" data-f1="${pmSign(OMISS[SRCID[s2]], OBIAS[SRCID[s2]] ?? OPCT[SRCID[s2]]).slice(0, 1) + OMISS[SRCID[s2]].toFixed(1)}">${pmSign(OMISS[SRCID[s2]], OBIAS[SRCID[s2]] ?? OPCT[SRCID[s2]])}</i>` : ""}</span><em class="${d > 0 ? "up" : d < 0 ? "dn" : "z"}">${d === null || d === 0 ? "–" : (d > 0 ? "▲" : "▼") + Math.abs(d)}</em></div>`; };
        const BELL = `<button type="button" class="bel sbel ${live.length ? (nA.red ? "red" : nA.gold ? "gold" : "grey") : "none"}" data-alerts="${SLUG[k]}" aria-label="${DK[k]} alerts: ${live.length ? `${nA.red} act now, ${nA.gold} monitor, ${nA.grey} noted` : "none open"}. Opens the alerts." title="${live.length ? `${nA.red} act now · ${nA.gold} monitor · ${nA.grey} noted - tap to open` : "No open alerts"}">${bellSvg}${live.length ? `<i>${live.length}</i>` : ""}</button>`;
        const yPrev = prev && prev.lg[k] && prev.lg[k].y !== undefined && prev.lg[k].y !== null ? Math.round(prev.lg[k].y) : null;
        const ZF = (v) => v === null || v === undefined || isNaN(v) ? "mid" : v >= 55 ? "win" : v >= 45 ? "mid" : "lose";
        /* Nov 11 2:35 PM (Dom: "worked out from the experts, not Yahoo"): the Scoreboard WEEK number and the fluid color are the RANKED
           chance - the average of the top three sources by accuracy - with Yahoo's own number kept in the tooltip */
        const RK = rankedOf(X, OCK), wk = RK ? Math.round(RK.v) : y, wkP = (() => { /* change since the last read, counted only over the top sources both reads have, so a source missing from the old read can't fake a jump */
          const P0 = prev && prev.lg[k]; if (!RK || !P0) return null; const cm = RK.top.filter(s3 => P0[s3] !== null && P0[s3] !== undefined && !isNaN(P0[s3])); if (!cm.length) return null;
          const a0 = cm.reduce((a, s3) => a + P0[s3], 0) / cm.length, a1 = cm.reduce((a, s3) => a + X[s3], 0) / cm.length; return wk - Math.round(a1 - a0); })();
        /* Nov 11 2:50 PM (Dom): the little week line is gone - each number carries its own arrow: how far it has moved since the first
           read of the week (green up, red down). RANKED counts only the top sources that also had a number at the start of the week */
        const dY = (() => { const w0 = weekStart(k, "y"); return w0 === null || w0 === undefined || isNaN(w0) ? null : Math.round(y - w0); })();
        const dR = (() => { if (!RK) return null; const cm = RK.top.map(s3 => [s3, weekStart(k, s3)]).filter(([, v0]) => v0 !== null && v0 !== undefined && !isNaN(v0)); if (!cm.length) return null;
          return Math.round(cm.reduce((a, [s3]) => a + X[s3], 0) / cm.length - cm.reduce((a, [, v0]) => a + v0, 0) / cm.length); })();
        const wkArrow = (d, who) => d === null ? "" : `<i class="wch ${d > 0 ? "up" : d < 0 ? "dn" : "z"}" title="${who}: ${d === 0 ? "no change" : (d > 0 ? "up " : "down ") + Math.abs(d) + " points"} since the first read of the week">${d === 0 ? "– 0" : (d > 0 ? "▲" : "▼") + Math.abs(d)}</i>`;
        const ZN = settled(L) ? (score(L.players) >= score(L.oppPlayers) ? "win" : "lose") : ZF(wk), PZ = ZF(po === null || po === undefined ? null : po * 100);
        const T = (sec, body) => `<div class="mx ms-${sec}${fl ? " flash" : ""}" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}" role="button" tabindex="0" aria-label="${esc(say)}">${body}</div>`;
        const tag = `<div class="mtag"><b>${DK[k]}</b><span>${esc(LGSHORT[k])}</span></div>`;
        return {k, a: T("a", `<div class="mxh wph"><div class="r1"><b>${DK[k]}</b>${BELL}</div><span class="nm" title="${esc(LGFULL[k])}">${esc(k === "MOST" ? "Most Important" : k === "HERS&HIS" ? "Hers and His" : LGFULL[k])}</span></div>
      <div class="mxd mxd2">${bigDial(y, HEX[k], xmid, SLUG[k], weekStart(k, "y"), (rankedOf(X, OCK) || {}).v)}<div class="wln wln2"><div class="mxp wo" title="Yahoo's chance to win this week${xmid === null ? "" : ` · white tick = the experts' middle, ${Math.round(xmid)}%`}${off ? ` · CHECK: Yahoo's own projections (${f1(F.me)} vs ${f1(F.op)}) work out to about ${imp}%` : ""}"><b class="wpn z-${ZF(y)}">${wp2(y)}%</b><span class="ny">YAHOO</span>${wkArrow(dY, "Yahoo")}</div>
        
        ${(() => { /* Nov 10 8:31 AM (Dom): second orb = the average chance to win this week of the top three sources by accuracy (the checked ones) */
          const IDS = {ratcliffe: "r", koerner: "k", clay: "c", vegas: "v", rotoballer: "b", yahoo: "y", gotham: "g"}, top = OCK.map(id => IDS[id]).filter(s3 => X[s3] !== null && X[s3] !== undefined && !isNaN(X[s3]));
          if (!top.length) return "";
          const t3 = top.reduce((a, s3) => a + X[s3], 0) / top.length, NM3 = {r: "Ratcliffe", k: "Koerner", c: "Clay", v: "Vegas", b: "RotoBaller", y: "Yahoo", g: "Gotham"};
          return `<div class="wo" title="RANKED = average chance to win this week of your top ${top.length} sources by accuracy (last graded week): ${top.map(s3 => NM3[s3] + " " + Math.round(X[s3]) + "%").join(", ")}"><b class="wpn z-${ZF(t3)}">${wp2(Math.round(t3))}%</b><span class="nr">RANKED</span>${wkArrow(dR, "RANKED")}</div>`; })()}
        </div></div>`),
          b: T("b", `<div class="sbh"><b>${DK[k]}</b><span class="nm" title="${esc(LGFULL[k])}">${esc(k === "MOST" ? "Most Important" : k === "HERS&HIS" ? "Hers and His" : LGFULL[k])}</span></div><div class="mxs sgw z-${ZN}${onField ? " on" : ""}" data-sheet="${SLUG[k]}" role="button" title="Tap for both lineups and the week's trend. ${goNow ? "Live points (Yahoo). Your fluid color = chance to win this week: green 55%+, amber 45-55%, red under 45%; his is always gray. Solid fluid = points scored; lighter shade above = rest of the projected final. Ring = every starter by position (yours left, his right); a pulsing segment = playing (green), problem (amber) or unknown (red)." : "Not started · projected " + f1(F.me) + " vs " + f1(F.op)}">
        ${scoreGlobe(L, k, {y: wk, meOn: L.players.some(p => isStarter(p) && isLive(p)), opOn: L.oppPlayers.some(p => isStarter(p) && isLive(p)), me: goNow ? me : 0, op: goNow ? op : 0, pMe: F.me, pOp: F.op, meL, opL, state: done ? "FINAL" : goNow ? (onField ? "LIVE" : "IN PROGRESS") : "NOT STARTED"})}</div>
        ${(() => { /* Nov 11 4:10 PM (Dom: "too much wasted space"): one compact ledger under the globe - MARGIN, PLAYOFFS, PROJ, LEFT
          and FAAB (or waiver order) - readable labels, no boxes inside boxes. Two columns on a computer, one tight list on a phone */
          const mz = Math.abs(mg) < 3 ? "mid" : mg > 0 ? "win" : "lose", mt = Math.round(mg);
          const tip = done ? `Final margin: ${f1(me)} to ${f1(op)}` : goNow ? `Live margin: ${f1(me)} to ${f1(op)} · you have ${meL} left to play, he has ${opL}` : `Projected margin (Yahoo's projections): ${f1(F.me)} to ${f1(F.op)}`;
          const wb = m.wire, at = wb && wb.read ? " · Yahoo read " + esc(wb.read) : "";
          const row = (lab, val, cls, title) => `<div class="lr" title="${esc(title)}"><span>${lab}</span><b class="${cls || ""}">${val}</b></div>`;
          const rows = [
            row(goNow && !done ? "LIVE MARGIN" : done ? "FINAL" : "MARGIN", (mt > 0 ? "+" : mt < 0 ? "−" : "") + Math.abs(mt), "z-" + mz, tip),
            row("PLAYOFFS", pcs(po), "z-" + PZ, "Playoff odds for the season (championship simulator)"),
            row("PROJ", `<em>${Math.round(F.me)}</em><i>·</i>${Math.round(F.op)}`, "pr", `Projected final, Yahoo: you ${f1(F.me)}, him ${f1(F.op)}`),
            row("LEFT", `<em>${meL}</em><i>·</i>${opL}`, "pr", `Players still to play: you ${meL}, him ${opL}`)];
          if (wb && wb.faab !== null && wb.faab !== undefined) rows.push(row("FAAB", "$" + wb.faab, "fb", `FAAB budget left${wb.wp ? " · waiver order #" + wb.wp + " of " + wb.n : ""}${at}`));
          else if (wb && wb.wp) rows.push(row("WAIVER", `#${wb.wp}<i>/${wb.n}</i>`, "fb", `No FAAB in this league - claims go by waiver order: #${wb.wp} of ${wb.n}${at}`));
          return `<div class="sled">${rows.join("")}</div>`; })()}`),
          c: T("c", `<div class="mxh wph" data-accgo="1"><div class="r1"><b>${DK[k]}</b></div><span class="nm" title="${esc(LGFULL[k])}">${esc(k === "MOST" ? "Most Important" : k === "HERS&HIS" ? "Hers and His" : LGFULL[k])}</span></div><div class="mxe"><div class="xg">${ORBS.map(orb).join("")}</div></div>`)}; }).filter(Boolean);
  /* Nov 8 9:40 PM (Dom): expert order Ratcliffe (two stars, the one we check against), Koerner, Clay, Vegas; FantasyPros 2026 in-season accuracy rank beside each name */
  const SEC = (id, lab, sub, key) => `<section class="frame msec" id="${id}"><span class="lab">${lab}</span>${sub ? `<span class="lsub">${sub}</span>` : ""}<div class="mgrid g-${key}">${TILES.map(t => t[key]).join("")}</div></section>`;
  /* Nov 9 10:37 AM (Dom): every section label carries its time on the right, Diamonds style: "9:52 AM · Next 10:25" */
  const hm = (t) => String(t || "").replace(/:00 /, ":00 ");
  const TNOW = (stamp) => { const a = stamp ? esc(PT(stamp, {hour: "numeric", minute: "2-digit"})) : "–", n = nextUpdate(); return `${a}${n ? " · Next " + esc(n.replace(/ (AM|PM)$/, "")) : ""}`; };
  $("#meters").innerHTML = SEC("msScore", "Scoreboard", TNOW(S.stamp), "b") + SEC("msWin", "Win Probability", TNOW(S.stamp), "a");   /* Nov 9 11:00 AM (Dom): Scoreboard on top */
  fitNames();
  const ACCT = (() => { const g = ((M && M.acc) || {}).graded; const m = g && /(\d+:\d+ [AP]M)/.exec(g); const n = nextUpdate(); return (m ? m[1] : "–") + (n ? " · Next " + n.replace(/ (AM|PM)$/, "") : ""); })();
  $("#meters2").innerHTML = SEC("msExp", "Experts &amp; Sources", esc(ACCT), "c"); { const xs = $("#msExp"); if (xs) xs.insertAdjacentHTML("beforeend", accTable().replace('<details class="fold accf"', `<details class="fold accf"${ACCSHOW ? "" : " hidden"}`)); fitNames(); }   /* Nov 8 (Dom): Win probability above Experts; section called just "Experts" */
  const kick = nextKick();
  $("#sch").innerHTML = KEYS.map(k => { const L = lgS(k); if (!L) return ""; const y = chance(L, "y"), pv = prev && prev.lg[k] ? prev.lg[k].y : null;
    const mv = pv === null || pv === undefined ? "" : y === pv ? "" : `<span class="${y > pv ? "up" : "dn"}">${y > pv ? "▲" : "▼"}${Math.abs(y - pv)}</span>`;
    return `<button type="button" class="sc" style="--lc:${LCOL[k]}" data-jump="${SLUG[k]}"><div class="t">${DK[k]}</div><div class="s ${scoreCls(L).split(" ")[0]}">${f1(score(L.players))}–${f1(score(L.oppPlayers))}</div>
      <div class="p"><b>${y}%</b> ${mv}</div><div class="p">${leftOf(L.players).length}/${leftOf(L.oppPlayers).length} left</div></button>`; }).join("");
  $("#sbar").innerHTML = `<span>Yahoo read ${esc(ago(S.stamp))}</span><span>${kick ? "Next kickoff " + esc(kick) : "No games left this week"}</span><button type="button" data-jump="top">Top</button>`;
}
/* Nov 9 (Dom): "Experts rank #, how far off pts or % from last week. Last time graded." Our own grade, in his leagues' scoring,
   each number frozen before kickoff: rank among the panel by last graded week, points missed per player and % off, change vs the week before. */
/* Nov 9 8:20 AM (Dom): "add our rank behind name" - our accuracy rank (same order as the How far off table) behind every source's name */
/* Nov 9 8:55 AM (Dom): one ranking everywhere - the pickup panel ranks all seven on the same players; its top three are the check */
const PNID = {Ratcliffe: "ratcliffe", Koerner: "koerner", Clay: "clay", Vegas: "vegas", RotoBaller: "rotoballer", Yahoo: "yahoo", Gotham: "gotham"};
function panelQ(){ const Q = ((PK || (M && M.pickups) || {}).panel) || null; return Q && Q.order && Q.miss && Object.keys(Q.miss).length ? Q : null; }
function ourRanks(){ const Q = panelQ();
  if (Q) return Object.fromEntries(Q.order.filter(n => Q.miss[n] !== undefined).map((n, i) => [PNID[n] || n.toLowerCase(), i + 1]));
  const src = ((M && M.acc) || {}).src || {}, last = (wk) => { const ws = Object.keys(wk || {}).map(Number).sort((a, b) => a - b); return ws.length ? wk[String(ws[ws.length - 1])][0] : null; };
  const ids = Object.keys(src).filter(id => last(src[id]) !== null).sort((a, b) => last(src[a]) - last(src[b])); return Object.fromEntries(ids.map((id, i) => [id, i + 1])); }
function ourMiss(){ const Q = panelQ(); if (Q) return Object.fromEntries(Object.entries(Q.miss).map(([n, v]) => [PNID[n] || n.toLowerCase(), v]));
  const src = ((M && M.acc) || {}).src || {}; return Object.fromEntries(Object.entries(src).map(([id, wk]) => { const ws = Object.keys(wk).map(Number).sort((a, b) => a - b); return [id, ws.length ? wk[String(ws[ws.length - 1])][0] : undefined]; }).filter(x => x[1] !== undefined)); }
/* Nov 9 9:10 AM (Dom): "instead of off, use a + or - in front" - + = that source usually projected high, - = low; the number is how far off */
function ourBias(){ const Q = panelQ(); return Q && Q.bias ? Object.fromEntries(Object.entries(Q.bias).map(([n, v]) => [PNID[n] || n.toLowerCase(), v])) : {}; }
const pmSign = (miss, bias) => (bias === undefined || bias === null ? "±" : bias >= 0 ? "+" : "−") + miss.toFixed(2);
/* Nov 10 7:57 AM (Dom): the percent is gone - each expert shows points missed per player, + too high / - too low, on the name's line, names centered.
   Nov 10 (Dom, earlier): after each expert's name and check, how far off he was last graded week as a percent with its direction:
   ▲11% = projected players 11% too high, ▼5% = 5% too low (fair across the four leagues' scoring) */
function ourPct(){ const Q = panelQ(); return Q && Q.pct ? Object.fromEntries(Object.entries(Q.pct).filter(([, v]) => v !== null && v !== undefined).map(([n, v]) => [PNID[n] || n.toLowerCase(), v])) : {}; }
const pctTag = (v) => v === undefined || v === null ? "" : Math.round(v) === 0 ? "±0%" : (v > 0 ? "▲" : "▼") + Math.abs(Math.round(v)) + "%";
const pctWhy = (v) => v === undefined || v === null ? "" : Math.round(v) === 0 ? "right on, last graded week" : `projected players ${Math.abs(Math.round(v))}% too ${v > 0 ? "high" : "low"} last graded week`;
function ourCheck(){ const Q = panelQ(); return Q ? (Q.check || []).map(n => PNID[n] || n.toLowerCase()) : []; }
const SRCID = {r: "ratcliffe", k: "koerner", c: "clay", v: "vegas", b: "rotoballer", y: "yahoo", g: "gotham"};
function accTable(){
  /* Nov 9 8:55 AM (Dom): "How far off they were" folds up into Experts & Sources (closed until tapped); 1-7 best on top,
     "1, Gotham" then points off to two decimals; green check on the top three = the three this week's pickups are averaged on;
     the pickup check's rules live here now, not under Diamonds in the Rough */
  const Q = panelQ(), A = (M && M.acc) || {}, P = PK || (M && M.pickups) || {};
  const LBL = {Ratcliffe: "Ratcliffe", Koerner: "Koerner", Clay: "Clay", Vegas: "Vegas", RotoBaller: "RotoBaller", Yahoo: "Yahoo", Gotham: "Gotham (engine)"};
  const FPR = {Ratcliffe: (XACC.r || {}).rk, Koerner: (XACC.k || {}).rk};
  let rows = [], wk = "", np = "", basis = "";
  if (Q){ wk = Q.week; np = Q.players; basis = Q.basis || "";
    const ranked = Q.order.filter(n => Q.miss[n] !== undefined), rest = Object.keys(LBL).filter(n => !ranked.includes(n));
    rows = ranked.map((n, i) => ({n, r: i + 1, m: Q.miss[n], b: (Q.bias || {})[n], pc: (Q.pct || {})[n], ck: (Q.check || []).includes(n), wait: (Q.waiting || {})[n]})).concat(rest.map(n => ({n, r: null})));
  } else { const src = A.src || {}; if (!Object.keys(src).length) return "";
    const lastOf = (w) => { const ws = Object.keys(w || {}).map(Number).sort((a, b) => a - b); return ws.length ? [ws[ws.length - 1], w[String(ws[ws.length - 1])]] : [null, null]; };
    const IDN = {ratcliffe: "Ratcliffe", koerner: "Koerner", clay: "Clay", vegas: "Vegas", rotoballer: "RotoBaller", yahoo: "Yahoo", gotham: "Gotham"};
    const g = Object.entries(IDN).map(([id, n]) => { const [w, v] = lastOf(src[id]); if (w !== null) wk = w; return {n, m: v ? v[0] : null}; });
    const gr = g.filter(x => x.m !== null).sort((a, b) => a.m - b.m); rows = gr.map((x, i) => ({n: x.n, r: i + 1, m: x.m, ck: false})).concat(g.filter(x => x.m === null).map(x => ({n: x.n, r: null}))); basis = "each source on its own players"; }
  const li = rows.map(x => x.r === null
      ? `<li><span class="n">–,</span><span class="nm">${LBL[x.n] || x.n}</span><span class="of ng">not graded yet</span></li>`
      : `<li class="${x.ck ? "ck" : ""}"><span class="n">${x.r},</span><span class="nm">${LBL[x.n] || x.n}${x.ck ? ` <span class="pk3" title="Top three by accuracy - this week's pickups are averaged on these">&#10003;</span>` : ""}</span><span class="of" title="${x.b === undefined || x.b === null ? "" : x.b >= 0 ? "usually projected high" : "usually projected low"}"><b>${pmSign(x.m, x.b ?? x.pc)}</b></span>${x.ck && x.wait ? `<em>Week ${esc(String(x.wait))} numbers only so far - the next source steps in until the week-ahead numbers post</em>` : FPR[x.n] ? `<em>FantasyPros #${FPR[x.n]}</em>` : ""}</li>`).join("");
  const top = rows.filter(x => x.ck).map(x => x.n);
  return `<details class="fold accf" data-fold="accf"${FOLDS.accf ? " open" : ""}><summary>How far off they were <span class="cnt">${top.length ? "&#10003; " + esc(top.join(", ")) : "Week " + esc(String(wk || "-"))}</span></summary><div class="fb"><div class="acct">
    <div class="ach"><span>Week ${esc(String(wk || "-"))}${np ? ` · ${np} players` : ""}${basis ? " · " + esc(basis) : ""} · graded ${esc(A.graded || "-")}</span></div>
    <ol class="acl">${li}</ol>
    <p>The number = points missed per player, in your leagues' scoring, each projection frozen before kickoff; + in front = that source usually projected too high, − = too low (± until the next build posts which way). &#10003; = the top three: every pickup's points, and his edge over the man he'd replace, are the average of these three (if one has no number for a man, the next one down steps in). The order re-ranks every week. Alerts still fire on any one source.${Q && (Q.notes || []).length ? " Note: " + esc(Q.notes.join("; ")) : ""}</p>
    <p>Diamonds in the Rough grade, out of 100: value 30, your fit 25 (missing pieces, beats your weakest starter, depth), workload 15, playoffs 15, team record 5, path to the job 10; Out or Doubtful costs 10. &#128680; MUST = 10%+ over the man he'd replace (or fills a missing piece at grade 70+), at least half the sources agree, grade 60+, healthy - blinks and pushes to your phone. &#128293; HOT = grade 60+ or clears 10% without the sources behind it. &#128230; STASH = the starter ahead is fading or a coach talked up his role. &#128064; WATCH = not yet. Checked 4:40 AM, 1:40 PM, 7:40 PM PT${P.built ? " · last " + esc(P.built) : ""}. Talk it through before any claim.</p></div></div></details>`;
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
/* Nov 7 (Dom: "wherever there's a discrepancy maybe we should automatically list the players so we know what the hell is really
   going on"; trigger 5 points): when any source's chance to win this week sits 5+ points from the middle of the five, name the
   men behind it - each man's number from that source against the middle of the other sources, both sides, the biggest first. */
function whyDiffer(L, k){
  if (settled(L)) return "";
  const pm = (M && M.pm && M.pm[L.key]) || {}, S5 = [["y", "Yahoo"], ["v", "Vegas"], ["r", "Ratcliffe"], ["k", "Koerner"], ["c", "Clay"]];
  const ch = Object.fromEntries(S5.map(([s]) => [s, chance(L, s)])), med = (a) => { const b = a.filter(x => x !== null && !isNaN(x)).sort((x, y) => x - y); return b.length ? (b.length % 2 ? b[(b.length - 1) / 2] : (b[b.length / 2 - 1] + b[b.length / 2]) / 2) : null; };
  const mid = med(Object.values(ch)), out = [];
  for (const [s, nm] of S5){
    const gap = ch[s] - mid; if (Math.abs(gap) < 5) continue;
    const rows = [];
    for (const [list, mine] of [[L.players, true], [L.oppPlayers, false]]) for (const p of list){
      if (isDone(p) || isOut(p)) continue;
      const mv = manFinal(p, s, pm), others = med(S5.filter(([o]) => o !== s).map(([o]) => manFinal(p, o, pm)));
      if (others === null) continue; const d = mv - others, push = mine ? d : -d;   /* push > 0 helps you on this source */
      if (Math.abs(d) >= 1 && Math.sign(push) === Math.sign(gap)) rows.push({p, mine, mv, others, push});
    }
    rows.sort((a, b) => Math.abs(b.push) - Math.abs(a.push));
    if (!rows.length) continue;
    out.push(`<div class="wd"><div class="wh"><b class="${gap > 0 ? "up" : "dn"}">${nm} ${gap > 0 ? "higher" : "lower"}</b> <span>${ch[s]}% vs the others' ~${Math.round(mid)}%</span></div>` +
      rows.slice(0, 3).map(x => `<div class="wr"><span class="wn">${esc(x.p.name)} <em>${x.mine ? "yours" : "opp"}</em></span><span class="wv">${nm.slice(0, 3).toUpperCase()} <b>${f1(x.mv)}</b> · others ${f1(x.others)}</span></div>`).join("") + `</div>`);
  }
  return out.length ? `<div class="sub">Why they differ</div>${out.join("")}<p class="note">Shown when a source is 5+ points from the middle of the five. Each man: that source's points against the middle of the other four, ${DK[k]} scoring.</p>` : "";
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
/* ---------- Nov 8 (Dom): the played strip + box score ----------
   Strip: every starter in lineup order, labeled with his position. Dark green = done, light green blinking neon = playing now,
   gray = not played yet. Tap the strip: the box score for both teams - starters and bench - with each man's stat line, Yahoo
   points (league scoring) and his projection (Yahoo, Ratcliffe where the meter has him). Your bench is flagged when a man
   there is projected 2+ points over the starter at his position (before lock) or outscored him by 2+ (after). */
const SLOTLAB = (s) => ({"W/R/T": "FLEX", "Q/W/R/T": "SFLX", "SUPER": "SFLX", "W/R": "W/R", "DEF": "DEF"})[s] || s || "?";
const bxNorm = (n) => String(n || "").toLowerCase().replace(/ (jr|sr|ii|iii|iv)\.?$/, "").replace(/[^a-z]/g, "");
function bxState(r, L){
  const all = [...(L.players || []), ...(L.oppPlayers || [])], n = bxNorm(r.name);
  const st = all.find(p => bxNorm(p.name) === n);
  if (st) return {g: isStarter(st) ? dotState(st) : isLive(st) ? "live" : isDone(st) ? "done" : "pre", when: st.when || r.when || "", pts: started(st) ? pts(st) : (r.pts || 0), starter: st};
  const tm = String(r.tm || "").toUpperCase();
  for (const LL of (S.leagues || [])) for (const p of [...(LL.players || []), ...(LL.oppPlayers || [])])
    if (String(p.tm || "").toUpperCase() === tm && (isLive(p) || isDone(p))) return {g: isLive(p) ? "live" : "done", when: p.when, pts: r.pts || 0};
  return {g: r.gs === "final" || r.gs === "bye" ? "done" : r.gs === "live" ? "live" : "pre", when: r.when || "", pts: r.pts || 0};
}
/* Nov 8 (Dom): your score is colored by Yahoo's chance to win this week - green 55%+, soft amber 45-55%, red under 45% -
   and blinks while any of your starters is on the field */
const scoreCls = (L) => { const c = chance(L, "y"); if (c === null || c === undefined || isNaN(c)) return "";
  return "sc-" + (c >= 55 ? "g" : c >= 45 ? "a" : "r") + ((L.players || []).some(isLive) ? " sc-live" : ""); };
function boxHtml(k, L){
  const B = L.box && L.box.me && L.box.op ? L.box : null;
  const fallback = (list) => list.map(p => ({slot: p.slot, name: p.name, tm: p.tm, pos: "", status: p.status, pts: p.actual, line: "", yp: p.proj, rp: null, gs: "", when: p.when}));
  const sides = B ? {me: B.me, op: B.op} : {me: fallback(L.players || []), op: fallback(L.oppPlayers || [])};
  const isBench = (r) => /^(BN|IR)/.test(r.slot || "");
  /* Nov 10 (Dom): the same player light beside every name in the box score */
  const lightOf = (r, s) => ringState({name: r.name, status: r.status, proj: r.yp === null || r.yp === undefined ? 1 : r.yp, slot: r.slot,
    when: /bye/i.test(r.when || "") || r.gs === "bye" ? "Bye" : s.g === "live" ? "In progress" : s.g === "done" ? "Final" : (r.when || "")});
  const blocks = (rows) => rows.filter(r => !isBench(r)).map(r => { const s = bxState(r, L), lt = lightOf(r, s);
    return `<i class="bk lt-${lt}" title="${esc(r.name)} · ${esc(STW[lt] || "")} · ${esc(s.when)}">${esc(SLOTLAB(r.slot))}</i>`; }).join("");
  const fid = "bx-" + SLUG[k], open = !!FOLDS[fid];
  /* bench flags, your side only */
  const flags = {};
  if (B){ const st = sides.me.filter(r => !isBench(r) && r.slot !== "IR"), bn = sides.me.filter(r => r.slot === "BN");
    for (const b of bn){ const sb = bxState(b, L); const same = st.filter(s => (s.pos || "") === (b.pos || "") && b.pos); if (!same.length) continue;
      if (sb.g === "pre"){ const pre = same.filter(s => bxState(s, L).g === "pre" && s.yp !== null && s.yp !== undefined);
        if (b.yp !== null && b.yp !== undefined && pre.length){ const w = pre.reduce((a, c) => c.yp < a.yp ? c : a); const d = b.yp - w.yp;
          if (d >= 2) flags[b.name] = {c: "y", t: `Projected ${d.toFixed(1)} more than ${w.name} (${SLOTLAB(w.slot)}) · swap before ${sb.when}`}; } }
      else if (sb.g === "done"){ const dn = same.filter(s => bxState(s, L).g === "done");
        if (dn.length){ const w = dn.reduce((a, c) => bxState(c, L).pts < bxState(a, L).pts ? c : a); const d = sb.pts - bxState(w, L).pts;
          if (d >= 2) flags[b.name] = {c: "r", t: `Outscored ${w.name} (${SLOTLAB(w.slot)}) by ${d.toFixed(1)} · left on the bench`}; } } } }
  const row = (r, mine) => { const s = bxState(r, L), f = mine ? flags[r.name] : null, gotPts = s.g !== "pre";
    const proj = [r.yp !== null && r.yp !== undefined ? `Yahoo ${f1(r.yp)}` : "", r.rp !== null && r.rp !== undefined ? `Ratcliffe ${f1(r.rp)}` : ""].filter(Boolean).join(" · ") || "no projection";
    const vs = gotPts && r.yp !== null && r.yp !== undefined && s.g === "done" ? ` <em class="${s.pts - r.yp >= 0 ? "up" : "dn"}">${sgn(s.pts - r.yp)}</em>` : "";
    return `<div class="bxr${f ? " fl " + f.c : ""}"><div class="bx1"><i class="bk sm ${s.g}">${esc(SLOTLAB(r.slot))}</i>
      <span class="nm"><i class="ldot ${lightOf(r, s)}" title="${esc(STW[lightOf(r, s)] || "")}"></i><b>${esc(r.name)}</b> <span class="mute">${esc(r.tm || "")}${r.pos && r.pos !== r.slot ? " " + esc(r.pos) : ""}</span>${r.status ? ` <span class="chip r">${esc(r.status)}</span>` : ""}</span>
      <span class="pt">${gotPts ? f1(s.pts) : "–"}${vs}</span></div>
      <div class="bx2"><span>${esc(s.g === "live" ? (/^(In progress|Playing)$/i.test(s.when || "") ? "Playing" : "Playing · " + s.when) : s.g === "done" ? (s.when && !/^Final$/i.test(s.when) ? s.when : "Final") : s.when)}</span><span>${proj}</span></div>
      ${r.line ? `<div class="bx3">${esc(r.line)}</div>` : gotPts && B && s.pts ? `<div class="bx3 mute">No stat line in the last Yahoo API read.</div>` : ""}
      ${f ? `<div class="bxf">${esc(f.t)}</div>` : ""}</div>`; };
  const team = (rows, name, mine) => { const st = rows.filter(r => !isBench(r)), bn = rows.filter(isBench);
    const tot = st.reduce((a, r) => a + (bxState(r, L).g !== "pre" ? bxState(r, L).pts : 0), 0), ytot = st.reduce((a, r) => a + (+r.yp || 0), 0);
    return `<div class="bxt"><div class="bxh"><b>${esc(name)}</b><span>${f1(tot)} pts · Yahoo proj ${f1(ytot)}</span></div>
      <div class="sub">Starters</div>${st.map(r => row(r, mine)).join("")}
      ${bn.length ? `<div class="sub">Bench${mine && Object.keys(flags).length ? ` · <span class="hot">${Object.keys(flags).length} flagged</span>` : ""}</div>${bn.map(r => row(r, mine)).join("")}` : B ? "" : `<p class="note">Bench and stat lines come with the next Dispatch build.</p>`}</div>`; };
  const nfl = Object.keys(flags).length;
  return `<details class="bxd" data-fold="${fid}"${open ? " open" : ""}><summary aria-label="Box score for both teams">
      <div class="pr"><span class="who">YOU</span><div class="blks">${blocks(sides.me)}</div></div>
      <div class="pr"><span class="who op">OPP</span><div class="blks">${blocks(sides.op)}</div></div>
      <div class="pkey"><span><i class="bk sm lt-ok"></i>Fine</span><span><i class="bk sm lt-trbl"></i>Q / D</span><span><i class="bk sm lt-out"></i>Out</span><span><i class="bk sm lt-bye"></i>Bye</span><span><i class="bk sm lt-done"></i>Done</span><span><i class="bk sm lt-empty"></i>Empty</span>${nfl ? `<span class="hot">${nfl} bench flag${nfl > 1 ? "s" : ""}</span>` : ""}<b>Box score ${open ? "▴" : "▾"}</b></div></summary>
    <div class="bxb">${team(sides.me, L.team || "Dark Knight", true)}${team(sides.op, L.opp || "Opponent", false)}
      <p class="note">Points: Yahoo, league scoring${B ? `, Yahoo API read ${esc(B.read || "")}` : ""}. Projections: Yahoo's weekly projection (league scoring) and Ratcliffe's where the meter has him. Live status follows the latest Yahoo read.</p></div></details>`;
}
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
    const mv = p0 === null || p0 === undefined || p0 === v ? "" : `<em class="${v > p0 ? "up" : "dn"}">${v > p0 ? "▲" : "▼"}${Math.abs(v - p0)}</em>`; return `<div><b>${wp2(v)}%</b><span>${lab}</span> ${mv}</div>`; }).join("");
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
  const scoreHtml = `<div class="score"><div class="side"><span>${esc(L.team || "Dark Knight")}</span><div class="big ${scoreCls(L)}" title="${chance(L, "y")}% chance to win this week (Yahoo)">${f1(me)}</div></div>
      <div class="mid">${done ? `<div class="vd" style="color:${me >= op ? "var(--up)" : "var(--dn)"}">${verdict(me - op)}</div><small>FINAL · ${sgn(me - op)}</small>` : `<div class="vd">${esc(L.state || "")}</div><small>${meL.length} / ${opL.length} left</small>`}</div>
      <div class="side r"><span>${esc(L.opp)}</span><div class="big" style="color:var(--ink2)">${f1(op)}</div></div></div>
    <div class="proj"><span>Yahoo proj ${f1(F.me)}</span><span>Yahoo proj ${f1(F.op)}</span></div>
    ${boxHtml(k, L)}`;

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
    ${scoreHtml}${seatHtml}
    ${fold("num-" + SLUG[k], "The numbers", `Ratcliffe ${chance(L, "r")}% · Vegas ${chance(L, "v")}%${splitHtml ? " · sources split" : ""}`,
      `${takes}<div class="xrow">${xr}</div><p class="note">Chance to win this week, best lineup both sides. Ratcliffe leads every decision number; Vegas is a check.</p>${splitHtml}${whyDiffer(L, k)}${vegHtml(L, m, k, yv)}`, !!splitHtml)}
    ${fold("gm-" + SLUG[k], "Games", `${meL.length} / ${opL.length} left`, progress(L, k))}
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
    for (const p of L.players.filter(isStarter).filter(p => ringState(p) === "empty" || ringState(p) === "bye"))
      out.push({k, col: "red", r: 0, t: 0, cd: "", cl: "fill before kickoff", html: ringState(p) === "bye"
        ? `<b>${esc(POSAB(p.slot))} ${esc(p.name)}</b> is on bye in your starting lineup - that spot scores 0.`
        : `Empty spot: <b>${esc(POSAB(p.slot))}</b>${p.name && !isEmptySpot(p) ? " " + esc(p.name) + " has no projection" : " has nobody in it"} - fill it before kickoff.`});
    for (const p of emptySeats(L).filter(p => isStarter(p) && ringState(p) !== "empty")) out.push({k, col: "red", r: 0, t: whenRank(p.when), cd: "", cl: p.when ? "locks " + p.when : "",
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
  separated(); footer(); needs(); renderPickups();
  if ($("#findq").value.trim()) findRun();
  scrollTo(0, y); nextLabel();
}
document.addEventListener("toggle", (e) => { const d = e.target; if (!d.matches || !d.matches("details[data-fold]")) return; FOLDS[d.dataset.fold] = d.open; store.set("folds", FOLDS);
  if (d.open && d.dataset.pkseen && d.classList.contains("chg")){ const ps = d.dataset.pkseen.split("|"); pkSeen(ps[0], ps[1], ps.slice(2).join("|")); d.classList.remove("chg"); renderPickups(); } }, true);

/* ---------- Nov 9 (Dom): TOP 5 PICKUPS moving forward - why, potential points rest of season, grade out of 100, built for EACH team ----------
   Built by live_sync/pickups.py into live/pickups. One tab per league (remembered). Grade = value 45 + workload 20 +
   playoff schedule 15 + team record 10 + path to the job 10; every part and every source carries its time. */
let PKL = store.get("pkl") || "1";
/* Nov 9 8:55 AM (Dom): four boxes across, an icon instead of the word, everything else folded under them; tap a box = that league opens */
let PKOPEN = store.get("pkopen") || "";
const PKI = {MUST: "&#128680;", HOT: "&#128293;", STASH: "&#128230;", WATCH: "&#128064;"};
const PKW = {MUST: "must pick up", HOT: "hot", STASH: "stash", WATCH: "watch"};
/* Nov 9 10:11 AM (Dom): "D. Achane" - first initial and last name; a defense stays "Vikings DEF" */
const pkShort = (p) => { const n = String(p.name || ""); if (p.pos === "DEF" || p.pos === "DST" || /DEF$/.test(n)) return n.endsWith("DEF") ? n : (p.team || "") + " DEF";
  const w = n.replace(/ (Jr\.?|Sr\.?|II|III|IV|V)$/, "").split(" "); return w.length > 1 ? w[0][0] + ". " + w.slice(1).join(" ") : n; };
/* Nov 9 noon (Dom): what each grade part means, under its bar */
const PEX = {value: "points he adds over the man he'd replace, in this league's scoring", fit: "how well he fills what this team is short on",
  workload: "his touches and snaps, and which way they're trending", playoffs: "his Weeks 15-17 matchups",
  team: "how good his NFL offense is", path: "the chance more work opens up for him - an injury or a depth-chart change ahead of him"};
/* Nov 9 noon (Dom): his points a game next to the man he'd replace, so the row says right away whether he helps.
   Top-3 sources by last week's accuracy when the build marked them (his Nov 9 rule), otherwise Ratcliffe */
function pkVs(p){ try { const X = (p.experts && p.experts.lines) || [], parse = (x) => { const m = String(x.txt || "").match(/^\s*([\d.]+)\s+vs\s+(.+?)\s+([\d.]+)/); return m ? {a: +m[1], who: m[2], b: +m[3]} : null; };
    let use = X.filter(x => x.check).map(parse).filter(Boolean), lab = "top 3";
    if (!use.length){ const r = X.find(x => /ratcliffe/i.test(x.ex || "")); const pr = r && parse(r); if (pr){ use = [pr]; lab = "Ratcliffe"; } }
    if (!use.length) return null;
    const a = use.reduce((t, u) => t + u.a, 0) / use.length, b = use.reduce((t, u) => t + u.b, 0) / use.length, who = use[0].who;
    const sw = who.split(" "), sn = sw.length > 1 && !/DEF$/.test(who) ? sw[0][0] + ". " + sw.slice(1).join(" ").replace(/ (Jr\.|Sr\.|II|III|IV)$/, "") : who;
    return {up: a > b, txt: `${a.toFixed(1)} a game vs ${b.toFixed(1)} ${esc(sn)} <i>${lab}</i>`}; } catch (e) { return null; } }
const pkOrb = (g) => { const r = 9, c = 2 * Math.PI * r, f = Math.max(0, Math.min(100, g || 0)) / 100, col = g >= 70 ? "#3FBF7F" : g >= 55 ? "#E5A93B" : "#8592AB";
  return `<svg class="pko" viewBox="0 0 24 24" aria-label="grade ${g} of 100"><circle cx="12" cy="12" r="${r}" fill="#0B1222" stroke="#1C2741" stroke-width="3"/><circle cx="12" cy="12" r="${r}" fill="none" stroke="${col}" stroke-width="3" stroke-linecap="round" stroke-dasharray="${(c * f).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 12 12)"/><text x="12" y="15.5" text-anchor="middle" font-size="9.5" font-weight="700" fill="#fff" font-family="IBM Plex Mono,monospace">${g}</text></svg>`; };
/* Nov 9 8:07 AM (Dom): "blink column when changes with recommended pickups" - each device remembers the list it last saw; a man who is new
   to a league's list, or whose tier or place moved, blinks his rank column (and that league's chip and tab) until his row is opened */
const PKSEEN = store.get("pkseen", {});
const pkSig = (p, i) => (p.tier || "WATCH") + "|" + (i + 1) + "|" + (p.grade == null ? "" : p.grade);
/* Nov 9 noon (Dom): no MOVE/TIER codes - say it plainly: new, "WATCH → HOT", or "grade 63 → 70". A list spot changing on its own
   (because someone else moved) means nothing to him, so it isn't flagged - the stored mark just catches up quietly */
/* Nov 11 (Dom: "reset Diamonds in the Rough"): a reset stamp in live/alert_marks (_pk_reset) clears this phone's change marks - every
   pick on the list now counts as seen, and only changes after the reset light up again */
function pkResetCheck(){ const r = MK && MK._pk_reset && MK._pk_reset.at; if (!r) return false;
  if (store.get("pkreset", "") >= r) return false; for (const k of Object.keys(PKSEEN)) delete PKSEEN[k]; store.set("pkseen", PKSEEN); store.set("pkreset", r); return true; }
function pkChanged(n, top){ const seen = PKSEEN[n]; if (!seen){ PKSEEN[n] = Object.fromEntries((top || []).map((p, i) => [p.key, pkSig(p, i)])); store.set("pkseen", PKSEEN); return {}; }
  const out = {}; let dirty = false;
  (top || []).forEach((p, i) => { const o = seen[p.key], sig = pkSig(p, i); if (o === sig) return;
    const T = p.tier || "WATCH"; if (!o){ out[p.key] = "new on the list"; return; }
    const [ot, , og] = o.split("|");
    if (ot !== T) out[p.key] = ot + " → " + T;
    else if (og !== undefined && og !== "" && p.grade != null && +og !== +p.grade) out[p.key] = "grade " + og + " → " + p.grade;
    else { seen[p.key] = sig; dirty = true; } });
  if (dirty) store.set("pkseen", PKSEEN); return out; }
function pkSeen(n, key, sig){ PKSEEN[n] = PKSEEN[n] || {}; PKSEEN[n][key] = sig; store.set("pkseen", PKSEEN); }
/* Nov 10 (Dom): THE WHEEL - five spokes on every pick, TEST ONLY: runs beside the system, never sets a tag or makes a move */
const WSP = [["team", "Team"], ["consensus", "Experts"], ["upside", "Upside"], ["drop", "Drop cost"], ["stakes", "Stakes & opp"]];
function wheelRadar(sp, mini){
  const cx = 60, cy = 58, R = 40, pt = (i, v) => { const a = -Math.PI / 2 + i * 2 * Math.PI / 5, r = R * Math.max(0, Math.min(20, v)) / 20; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
  const ring = (v) => WSP.map((_, i) => pt(i, v).map(x => x.toFixed(1)).join(",")).join(" ");
  const poly = WSP.map(([k], i) => pt(i, sp[k] || 0).map(x => x.toFixed(1)).join(",")).join(" ");
  return `<svg class="${mini ? "whmini" : "whr"}" viewBox="${mini ? "16 14 88 88" : "-16 0 152 116"}" aria-hidden="true"><polygon points="${ring(20)}" fill="none" stroke="#2A3A5C"/><polygon points="${ring(10)}" fill="none" stroke="#22304D"/><polygon points="${ring(5)}" fill="rgba(255,82,82,.10)" stroke="rgba(255,82,82,.45)" stroke-dasharray="2 2"/>
    ${WSP.map((_, i) => { const [x, y] = pt(i, 20); return `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#22304D"/>`; }).join("")}
    <polygon points="${poly}" fill="rgba(79,195,255,.28)" stroke="#4FC3FF" stroke-width="1.6"/>
    ${WSP.map(([k], i) => { const [x, y] = pt(i, sp[k] || 0); return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.6" fill="${(sp[k] || 0) < 5 ? "#FF5252" : "#4FC3FF"}"/>`; }).join("")}
    ${mini ? "" : WSP.map(([, lab], i) => { const [x, y] = pt(i, 26.5); return `<text x="${x.toFixed(1)}" y="${(y + 3).toFixed(1)}" text-anchor="middle" font-size="7.5" fill="#9FB0CF" font-family="IBM Plex Sans,sans-serif">${lab.split(" ")[0]}</text>`; }).join("")}</svg>`;
}
/* Nov 10 5:13 PM (Dom): every player is a WHEEL (5:19 PM: drawn as a cut diamond) - five spokes, each labeled with its name and number, and an orb in the
   middle holding the total out of 100, colored by the call (green GO, amber LEAN, purple STASH, grey PASS, red NO MOVE) */
const WVC = {GO: "#3DDC84", LEAN: "#FFB84D", STASH: "#A98BFF", PASS: "#8A94A8", "NO MOVE": "#FF5252"};
const WLB = {team: "Team", consensus: "Experts", upside: "Upside", drop: "Drop", stakes: "Stakes"};
const wSc = (v) => v < 5 ? "#FF5252" : v < 8 ? "#FFB84D" : v < 14 ? "#4FC3FF" : "#3DDC84";
function bigWheel(w, uid){
  /* Nov 10 5:19 PM (Dom: "some sort of a diamond"): a cut gem seen from above - five facets, one per spoke, each filled out
     from the table by its score (a dark facet = a weak spot), the total in the center table colored by the call. No glare. */
  const sp = w.spokes || {}, vc = WVC[w.verdict] || "#8A94A8", cx = 100, cy = 96, RG = 70, RT = 30;
  const O = (deg, r) => { const a = deg * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
  const L = (p, q, t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t], P = (...pts) => pts.map(q => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" ");
  const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16), f = (c) => Math.max(0, Math.min(255, Math.round(c * k))); return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`; };
  const girdle = [0, 1, 2, 3, 4].map(k => O(-126 + 72 * k, RG + 5)), table = [0, 1, 2, 3, 4].map(k => O(-126 + 72 * k, RT));
  let facets = "", marks = "";
  WSP.forEach(([k], i) => {
    const th = -90 + 72 * i, v = Math.max(0, Math.min(20, sp[k] || 0)), t = Math.max(.06, v / 20), c = wSc(v);
    const A = O(th - 36, RT), B = O(th + 36, RT), C = O(th + 36, RG), D = O(th - 36, RG), Mi = L(A, B, .5), Mo = L(D, C, .5);
    const D2 = L(A, D, t), C2 = L(B, C, t), M2 = L(Mi, Mo, t);
    facets += `<polygon points="${P(A, Mi, Mo, D)}" fill="#1A2440"/><polygon points="${P(Mi, B, C, Mo)}" fill="#131B33"/>
      <polygon points="${P(A, Mi, M2, D2)}" fill="${shade(c, 1)}"/><polygon points="${P(Mi, B, C2, M2)}" fill="${shade(c, .72)}"/>
      <polyline points="${P(D2, M2, C2)}" fill="none" stroke="${shade(c, 1.15)}" stroke-width=".8" opacity=".9"/>
      <line x1="${Mi[0].toFixed(1)}" y1="${Mi[1].toFixed(1)}" x2="${Mo[0].toFixed(1)}" y2="${Mo[1].toFixed(1)}" stroke="#0A1022" stroke-width=".7" opacity=".7"/>
      <polygon points="${P(A, B, C, D)}" fill="none" stroke="#0A1022" stroke-width="1.2"/>`;
    const [bx, by] = O(th, RG * Math.cos(Math.PI / 5) + 15), side = i === 1 || i === 4;
    const [lx, ly] = side ? [bx + (i === 1 ? 14 : -14), by + 4] : O(th, RG * Math.cos(Math.PI / 5) + (i === 0 ? 33 : 34));
    marks += `<circle cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="10.5" fill="#0B1226" stroke="${c}" stroke-width="2"/><text x="${bx.toFixed(1)}" y="${(by + 4).toFixed(1)}" text-anchor="middle" font-size="11" font-weight="700" fill="${c}" font-family="IBM Plex Mono,monospace">${Math.floor(v)}</text>
      <text x="${lx.toFixed(1)}" y="${(ly + (i === 0 ? 3 : side ? 0 : 3)).toFixed(1)}" text-anchor="${i === 1 ? "start" : i === 4 ? "end" : "middle"}" font-size="10.5" font-weight="600" fill="#CFE6FF" font-family="IBM Plex Sans,sans-serif">${WLB[k]}</text>`;
  });
  const tv = table.map((q, k) => `<line x1="${cx}" y1="${cy}" x2="${q[0].toFixed(1)}" y2="${q[1].toFixed(1)}" stroke="${shade(vc, .55)}" stroke-width=".7" opacity=".6"/>`).join("");
  return `<svg class="bwh" viewBox="-22 -6 244 206" role="img" aria-label="${esc(w.name)}: ${w.total} of 100, ${esc(w.verdict)}">
    <defs><radialGradient id="wt${uid}" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="${shade(vc, 1.12)}"/><stop offset=".7" stop-color="${shade(vc, .85)}"/><stop offset="1" stop-color="${shade(vc, .55)}"/></radialGradient>
      <filter id="ws${uid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="4"/></filter></defs>
    <ellipse cx="${cx}" cy="${cy + RG + 4}" rx="${RG * .8}" ry="6" fill="#000" opacity=".55" filter="url(#ws${uid})"/>
    <polygon points="${P(...girdle)}" fill="#0A1022" stroke="#4A5F8C" stroke-width="1.6"/>
    ${facets}
    <polygon points="${P(...table)}" fill="url(#wt${uid})" stroke="${shade(vc, 1.2)}" stroke-width="1.6"/>${tv}
    <polygon points="${P(...[0, 1, 2, 3, 4].map(k => O(-90 + 72 * k, RT * .5)))}" fill="${shade(vc, .9)}" opacity=".55"/>
    <text x="${cx}" y="${cy + 7}" text-anchor="middle" font-size="21" font-weight="800" fill="#fff" stroke="${shade(vc, .35)}" stroke-width="3" paint-order="stroke" font-family="IBM Plex Sans,sans-serif">${w.total}</text>
    ${marks}</svg>`;
}
function wheelBox(n, p){
  const W = M && M.wheel; if (!W || !W.leagues) return "";
  const w = ((W.leagues[n] || {}).picks || []).find(x => x.name === p.name);
  if (!w) return `<div class="whx"><div class="whh"><b>THE WHEEL</b><span class="wht">TEST</span><em>not run on this pick yet</em></div></div>`;
  const m = w.move, pc = (v) => (v >= 0 ? "+" : "") + (v * 100).toFixed(1);
  return `<div class="whx"><div class="whh"><b>THE WHEEL</b><span class="wht">TEST - not used for moves</span><span class="whv v-${w.verdict.replace(" ", "")}">${esc(w.verdict)}</span><span class="whs">${w.total}/100</span></div>
    <div class="whb">${bigWheel(w, "b" + n + p.name.replace(/\W/g, ""))}<ul>${WSP.map(([k, lab]) => `<li class="${(w.spokes[k] || 0) < 5 ? "red" : ""}"><b>${lab}</b><i>${Math.floor(w.spokes[k] || 0)}</i><span>${esc((w.why || {})[k] || "")}</span></li>`).join("")}</ul></div>
    ${m ? `<div class="whm">Played out: add him, drop <b>${esc(m.drop)}</b> - chance to win this week <b>${pc(m.d_week)}</b> · playoff odds for the season <b>${pc(m.d_playoff)}</b> · ${m.ppg >= 0 ? "+" : ""}${m.ppg} pts a game in ${m.games} games he'd start</div>` : ""}
    <div class="whf">${esc(w.vwhy)} · run ${esc(String(W.built || "").replace(/^\w{3} /, "").replace(/ 2026/, ""))}</div></div>`;
}

/* Nov 10 2:24 PM (Dom: "Add to DKLive so I can see it and how it is working"): its own section under Diamonds in the Rough -
   every pick in all four leagues, the wheel's call beside the Diamonds tag, and its graded record once the games are played */
const WYES = {GO: 1, LEAN: 1, MUST: 1, HOT: 1}, WNO = {PASS: 1, "NO MOVE": 1, WATCH: 1};
const wAgree = (t, v) => (t === "STASH" || v === "STASH") ? t === v : !!WYES[t] === !!WYES[v];
let WHL = store.get("whl") || "1", WHP = 0;
function renderWheel(){
  const el = $("#wheel"); if (!el) return;
  const W = M && M.wheel; if (!W || !W.leagues){ el.innerHTML = ""; return; }
  const all = Object.values(W.leagues).flatMap(L => L.picks || []), ag = all.filter(w => wAgree(w.tier, w.verdict)).length;
  const R = W.record || {}, rec = (a) => a && a[1] ? `${a[0]}-${a[1] - a[0]} <em>(${Math.round(100 * a[0] / a[1])}%)</em>` : `<em>–</em>`;
  const cnt = (v) => all.filter(w => w.verdict === v).length;
  const tabs = ["1", "2", "3", "4"].map(n => { const P = (W.leagues[n] || {}).picks || []; const best = P.slice().sort((a, b) => b.total - a.total)[0];
    return `<button type="button" class="whtab${n === WHL ? " on" : ""}" style="--lc:${LCOL[KEYS[+n - 1]]}" data-whl="${n}"><b>DK${n}</b>${best ? `<span class="whv v-${best.verdict.replace(" ", "")}">${esc(best.verdict)}</span><small>${esc(pkShort(best))} ${best.total}</small>` : "<small>none</small>"}</button>`; }).join("");
  const L = W.leagues[WHL] || {picks: []}, P = L.picks || [];
  if (WHP >= P.length) WHP = 0;
  const cards = P.map((w, i) => { const a = wAgree(w.tier, w.verdict);
    return `<button type="button" class="whcard${i === WHP ? " on" : ""}" data-whp="${i}" aria-pressed="${i === WHP}">${bigWheel(w, "s" + WHL + i)}
      <span class="whn"><b>${esc(pkShort(w))}</b><em>${esc([w.pos, w.team].join(" · "))}</em></span>
      <span class="whcmp"><span class="tg t-${esc(w.tier)}">${esc(w.tier)}</span><span class="${a ? "ok" : "no"}">${a ? "=" : "≠"}</span><span class="whv v-${w.verdict.replace(" ", "")}">${esc(w.verdict)}</span></span></button>`; }).join("");
  const w = P[WHP], pc = (v) => (v >= 0 ? "+" : "") + (v * 100).toFixed(1), m = w && w.move;
  const rows = w ? `<div class="whgrid">${cards}</div>
    <div class="whd"><div class="whdh"><b>${esc(w.name)}</b> <em>${esc([w.pos, w.team].join(" · "))}${w.replaces ? " · vs " + esc(w.replaces) : ""}</em></div>
      <ul>${WSP.map(([k, lab]) => `<li class="${(w.spokes[k] || 0) < 5 ? "red" : ""}"><b>${lab}</b><i>${Math.floor(w.spokes[k] || 0)}</i><span>${esc((w.why || {})[k] || "")}</span></li>`).join("")}</ul>
      ${m ? `<div class="whm">Played out: add him, drop <b>${esc(m.drop)}</b> - chance to win this week <b>${pc(m.d_week)}</b> · playoff odds for the season <b>${pc(m.d_playoff)}</b> · ${m.ppg >= 0 ? "+" : ""}${m.ppg} pts a game in ${m.games} games he'd start</div>` : `<div class="whm">Not in the season simulator's player pool - Drop cost and Stakes scored even (10).</div>`}
      <div class="whf">${esc(w.vwhy)}</div></div>` : "";
  const gr = (R.rows || []).length ? `<ul class="whgr">${R.rows.map(r => `<li><b>Wk ${r.wk} DK${r.lg}</b> ${esc(r.name)} ${r.actual[0]} vs ${esc(r.replaces)} ${r.actual[1]} · wheel ${esc(r.wheel)} ${r.wheel_right === undefined ? "–" : r.wheel_right ? "✓" : "✗"} · Diamonds ${esc(r.tier)} ${r.tier_right === undefined ? "–" : r.tier_right ? "✓" : "✗"}</li>`).join("")}</ul>` : "";
  el.innerHTML = `<section class="frame msec whsec" id="msWheel"><span class="lab">The Wheel <i class="wht">TEST</i></span><span class="pkts">${esc(String(W.built || "").replace(/^\w{3} \w{3} \d+ 20\d\d /, "").replace(/ PT$/, ""))}</span>
    <div class="whtop"><div class="whk"><span>Test only</span><b>never used for moves</b></div>
      <div class="whk"><span>Agrees with Diamonds</span><b>${ag} of ${all.length}</b></div>
      <div class="whk"><span>Calls</span><b>${cnt("GO")} GO · ${cnt("LEAN")} LEAN · ${cnt("STASH")} STASH · ${cnt("NO MOVE")} NO MOVE · ${cnt("PASS")} PASS</b></div>
      <div class="whk"><span>Track record</span><b>Wheel ${rec(R.wheel)} · Diamonds ${rec(R.diamonds)}</b><small>${(R.rows || []).length ? "did the pick outscore the starter he'd replace" : `${R.logged || all.length} calls logged for Week ${(R.weeks || []).join(", ") || "-"} - first grade when those games are played`}</small></div></div>
    <div class="whtabs">${tabs}</div>
    <div class="whlist" style="--lc:${LCOL[KEYS[+WHL - 1]]}">${rows || `<div class="empty">No picks for this league.</div>`}</div>
    ${gr}
    <p class="whnote">Five spokes, 20 each: Team (offense, last 3 games, record, workload) · Experts (top-3 average vs the starter he'd replace, sources ahead) · Upside (every game left, Weeks 15-17) · Drop cost (cheapest drop in the season simulator, rivals who'd start him) · Stakes &amp; opponents (this week's win chance weighted by how much the game matters, playoff odds, this week's opponent, rivals). Any spoke under 5 = NO MOVE.</p></section>`;
}
document.addEventListener("click", (e) => { const b = e.target.closest && e.target.closest("[data-whl]"); if (!b) return; WHL = b.dataset.whl; WHP = 0; store.set("whl", WHL); renderWheel(); });
document.addEventListener("click", (e) => { const b = e.target.closest && e.target.closest("[data-whp]"); if (!b) return; WHP = +b.dataset.whp; renderWheel(); });
function renderPickups(){
  const el = $("#pickups"); if (!el) return;
  /* live/pickups is the list the 3-a-day check last sent Dom (so the page matches the notification); the build's copy only fills in before the first one */
  /* Nov 9 9:56 AM (Dom): "updated more frequently, say when it was updated and when the next update is" - the newest list wins:
     every Dispatch build's list (models) or the 3-a-day check's (live/pickups), whichever was built last */
  const bt = (x) => { const t = x && x.built ? Date.parse(String(x.built).replace(/ PT$/, "").replace(/^\w{3} /, "")) : NaN; return isNaN(t) ? 0 : t; };
  const P = [PK, M && M.pickups].filter(Boolean).sort((a, b) => bt(b) - bt(a))[0];
  const TOP = $("#pkTop"); let PKCHIPS = "";
  if (!P || !P.leagues){ el.innerHTML = ""; if (TOP) TOP.innerHTML = ""; return; }
  const TO = {MUST: 0, HOT: 1, STASH: 2, WATCH: 3};
  const tierOf = (p) => p.tier || "WATCH";
  /* Nov 11 (Dom: "Kiner should not be listed - I picked him up"): never list a man already on Dom's roster in that league -
     the newest Yahoo roster read and this week's lineup both count, so a pickup drops off the list as soon as either sees it */
  { const mine = (n) => { const k = KEYS[+n - 1], L = lgS(k), out = new Set();
      for (const r of ((M && M.rosters && M.rosters.t && M.rosters.t[DKP[k]]) || [])) out.add(norm(r[0]).toLowerCase());
      if (L) for (const q of L.players) out.add(norm(q.name).toLowerCase()); return out; };
    for (const n of ["1", "2", "3", "4"]){ const Lp = P.leagues[n]; if (!Lp || !Lp.top) continue; const own = mine(n);
      if (Lp.top.some(q => own.has(norm(q.name).toLowerCase()))) P.leagues[n] = Object.assign({}, Lp, {top: Lp.top.filter(q => !own.has(norm(q.name).toLowerCase()))}); } }
  const CHG = Object.fromEntries(["1", "2", "3", "4"].map(n => [n, pkChanged(n, (P.leagues[n] || {}).top)]));
  /* top line: each league's best pickup by tier - MUST blinks (Dom, Nov 9: "blink ... pick up asap") */
  {
    const chips = ["1", "2", "3", "4"].map(n => { const t = ((P.leagues[n] || {}).top || []).slice().sort((a, b) => TO[tierOf(a)] - TO[tierOf(b)] || b.grade - a.grade)[0];
      if (!t) return `<button type="button" class="pkc${n === PKOPEN ? " on" : ""}" style="--lc:${LCOL[KEYS[+n - 1]]}" data-pkgo="${n}"><span class="r1"><span class="lg">DK${n}</span></span><span class="who none">none</span></button>`;
      const more = ((P.leagues[n] || {}).top || []).filter(x => tierOf(x) === tierOf(t)).length - 1;
      const nmT = t.pos === "DEF" || /DEF$/.test(t.name) ? (t.name.endsWith("DEF") ? t.name : t.team + " DEF") : t.name.replace(/ (Jr\.|Sr\.|II|III|IV)$/, "");
      return `<button type="button" class="pkc t-${tierOf(t)}${Object.keys(CHG[n]).length ? " chg" : ""}${n === PKOPEN ? " on" : ""}" style="--lc:${LCOL[KEYS[+n - 1]]}" aria-expanded="${n === PKOPEN}" data-pkgo="${n}" title="${esc(PKW[tierOf(t)] + ": " + (t.tier_why || ""))}" aria-label="DK${n} ${esc(PKW[tierOf(t)])}: ${esc(nmT)}"><span class="r1"><span class="lg">DK${n}</span><span class="ic">${PKI[tierOf(t)]}</span></span><span class="r2"><span class="who">${esc(pkShort(t))}</span>${pkOrb(t.grade)}</span></button>`; }).join("");
    const nm = ["1", "2", "3", "4"].reduce((a, n) => a + ((P.leagues[n] || {}).top || []).filter(x => tierOf(x) === "MUST").length, 0);
    /* Nov 9 8:21 AM (Dom): one Diamonds in the Rough, down with the list - the league chips ARE the tabs */
    TOP.innerHTML = ""; PKCHIPS = `<div class="pktop${nm ? " hasmust" : ""}"><div class="pkcs">${chips}</div></div>`;
  }
  if (PKOPEN) PKL = PKOPEN;
  const L = P.leagues[PKL] || {top: []}, src = P.sources || {};
  const gc = (g) => g >= 70 ? "g" : g >= 55 ? "a" : "n";
  const ring = (g) => { const r = 15, c = 2 * Math.PI * r, f = Math.max(0, Math.min(100, g)) / 100;
    return `<svg class="pkr ${gc(g)}" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="${r}" fill="none" stroke="#1C2741" stroke-width="4"/><circle cx="20" cy="20" r="${r}" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-dasharray="${(c * f).toFixed(1)} ${c.toFixed(1)}" transform="rotate(-90 20 20)"/><text x="20" y="24.5" text-anchor="middle" font-size="12" font-weight="700" fill="#fff" font-family="IBM Plex Mono,monospace">${g}</text></svg>`; };
  const PART = [["value", "Value", 30], ["fit", "Your fit", 25], ["workload", "Workload", 15], ["playoffs", "Playoffs", 15], ["team", "Team", 5], ["path", "Path", 10]];
  const C = CHG[PKL] || {};
  const rows = (L.top || []).map((p, i) => { const vs = pkVs(p), T = tierOf(p);
    return `<details class="pk2 t-${T}${C[p.key] ? " chg" : ""}" data-fold="pk-${PKL}-${i}" data-pkseen="${PKL}|${esc(p.key)}|${esc(pkSig(p, i))}"${FOLDS["pk-" + PKL + "-" + i] ? " open" : ""}>
      <summary><span class="rk">${i + 1}</span><span class="nm"><b>${esc(pkShort(p))}<em>${esc([p.pos === "DEF" || p.pos === "DST" ? "" : p.pos, p.team].filter(Boolean).join(" · "))}</em></b><span class="pkl2">${vs ? `<span class="pkvs ${vs.up ? "up" : "dn"}">${vs.txt}</span>` : ""}${C[p.key] ? `<span class="pkch">${esc(C[p.key])}</span>` : ""}</span></span>${pkOrb(p.grade)}<span class="ic t-${T}" title="${PKW[T]}">${PKI[T]}</span></summary>
      <div class="pkb"><div class="pkid">${esc(p.name)} · ${esc(p.pos)} · ${esc(p.team)} · <b>${Math.round(p.pts)}</b> pts rest of season · ${esc(String(p.status || ""))}</div>
      <div class="parts">${PART.map(([k, lab, mx]) => `<div><span>${lab}</span><i><b style="width:${Math.round(100 * (p.parts[k] || 0) / mx)}%"></b></i><em>${k === "workload" && (p.pos === "K" || p.pos === "DEF") ? "n/a" : (p.parts[k] || 0) + "/" + mx}</em><small>${PEX[k]}</small></div>`).join("")}</div>
      ${wheelBox(PKL, p)}
      ${p.tier_why ? `<div class="pkwhy t-${tierOf(p)}"><b>${tierOf(p)}</b> ${esc(p.tier_why)}</div>` : ""}
      <ul>${(p.why || []).map(w => `<li>${esc(w)}</li>`).join("")}</ul>
      ${p.experts ? `<div class="pkx2"><b>Every source, most to least accurate</b> - ${esc(p.experts.verdict)} <em>(gold = in this man's top-3 check)</em><ul>${(p.experts.lines || []).map(x => `<li class="${x.ok === true ? "up" : x.ok === false ? "dn" : ""}${x.check ? " ck" : ""}"><span>${x.ok === true ? "▲" : x.ok === false ? "▼" : "·"}</span><b>${esc(x.ex)}</b>${x.rank ? `<small>${esc(x.rank)}</small>` : ""} ${esc(x.txt)}${x.read ? ` <em>read ${esc(x.read.replace(/ 2026/, ""))}</em>` : ""}</li>`).join("")}</ul></div>` : ""}<div class="pst">${esc(p.status || "")}</div></div></details>`; }).join("");
  const PKT = String(P.built || "").replace(/^\w{3} \w{3} \d+ 20\d\d /, "").replace(/ PT$/, ""), NXT = nextUpdate();
  el.innerHTML = `<section class="frame msec pkx" id="msPick"><span class="lab">Diamonds in the Rough</span><span class="pkts">${esc(PKT)}${NXT ? " · Next " + esc(NXT.replace(/ (AM|PM)$/, "")) : ""}</span>
    ${PKCHIPS}
    ${PKOPEN ? `<div class="pkopen" style="--lc:${LCOL[KEYS[+PKL - 1]]}"><div class="pkneed">${(L.needs || []).length ? `<b>${DK[KEYS[+PKL - 1]]} needs:</b> ${L.needs.map(esc).join(" · ")}` : `<b>${DK[KEYS[+PKL - 1]]}:</b> no open missing pieces`}${L.read ? ` <em>· rosters ${esc(L.read)}</em>` : ""}</div>
    ${rows || `<div class="empty">Nothing graded for this league yet.</div>`}
    </div>` : ""}</section>`;
  renderWheel();
}
/* Nov 9 10:11 AM (Dom): nothing under the Experts boxes - tap any league's box and the detail opens; tap again and it goes away */
let ACCSHOW = false;
document.addEventListener("click", (e) => { const t = e.target.closest && e.target.closest(".ms-c"); if (!t || !t.closest("#msExp")) return; e.preventDefault(); e.stopImmediatePropagation();
  const f = $(".accf"); if (!f) return; ACCSHOW = !ACCSHOW; f.hidden = !ACCSHOW; f.open = ACCSHOW; if (ACCSHOW) f.scrollIntoView({behavior: "smooth", block: "nearest"}); }, true);
document.addEventListener("click", (e) => { const g = e.target.closest && e.target.closest("[data-pkgo]"); if (g){ const n = g.dataset.pkgo; PKOPEN = PKOPEN === n ? "" : n; store.set("pkopen", PKOPEN); if (PKOPEN){ PKL = n; store.set("pkl", PKL); } renderPickups(); } });
document.addEventListener("click", (e) => { const b = e.target.closest && e.target.closest("[data-pkl]"); if (!b) return; PKL = b.dataset.pkl; store.set("pkl", PKL); renderPickups(); });

/* ---------- events ---------- */
function rmsg(t, bad){ const el = $("#rmsg"); el.textContent = t; el.hidden = false; el.style.background = bad ? "#FBE4E5" : "#F2E6C4"; clearTimeout(rmsg.t); rmsg.t = setTimeout(() => el.hidden = true, 9000); }
document.addEventListener("click", async (e) => {
  const t = e.target.closest ? e.target : e.target.parentElement;
  if (t.closest("[data-shclose]") && (t.closest("[data-alerts]") || t.closest("[data-jump]"))) closeSheet();
  const ga = t.closest("[data-goal]"); if (ga){ e.preventDefault(); await goAlert(ga.dataset.goal); return; }
  const ab = t.closest("[data-alerts]"); if (ab){ e.preventDefault(); e.stopPropagation(); const id = "al-" + ab.dataset.alerts, d = document.querySelector(`details[data-fold="${id}"]`);
    if (d){ d.open = true; try { FOLDS[id] = true; } catch(_){} d.scrollIntoView({behavior: SMOOTH(), block: "start"}); } else jumpTo(ab.dataset.alerts); return; }
  const pl = t.closest("[data-pl]"); if (pl){ e.preventDefault(); e.stopPropagation(); plPop(pl.dataset.pl); return; }
  const sh = t.closest("[data-sheet]"); if (sh && (sh.tagName === "BUTTON" || !t.closest("#gsheet"))){ e.preventDefault(); e.stopPropagation(); openSheet(sh.dataset.sheet); return; }
  if (t.closest("[data-shclose]") || t.id === "gback"){ e.preventDefault(); closeSheet(); return; }
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
  else if (e.key === "/"){ e.preventDefault(); $("#findRow").hidden = false; $("#findq").focus(); }
  else if (e.key === "Escape"){ if (OPEN.size){ OPEN.clear(); renderAlertsOnly(); } const b = $("#hc"); if (!b.hidden){ b.hidden = true; $("#stat").setAttribute("aria-expanded", "false"); } }
});
$("#findq").addEventListener("input", findRun);
/* Nov 9 11:00 AM (Dom): search lives behind the magnifier in the slim button row */
$("#findBtn").addEventListener("click", () => { const r = $("#findRow"), open = r.hidden; r.hidden = !open; $("#findBtn").setAttribute("aria-expanded", String(open)); if (open) $("#findq").focus(); else { $("#findq").value = ""; findRun(); } });
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
  watch("live/alert_marks", v => { MK = Object.assign({}, v || {}); pkResetCheck(); if (S) renderAll(); renderPickups(); });
  watch("live/moves", v => { MV = v || null; if (S) renderAll(); });
  watch("live/pickups", v => { PK = v || null; renderPickups(); });
  watch("live/health", v => { H = v || null; renderStatus(); renderHealth(); });
  watch("live/alerts", v => { A = v || null; if (S) renderAll(); });
  watch("live/models", v => { if (v){ M = v; if (S){ renderAll(); trailAdd(); } } });
  watch("live/state", v => { if (v && v.leagues){ clearTimeout(tm); S = v; renderAll(); if (M) trailAdd();
    if (!HASHED){ HASHED = true; const h = location.hash.slice(1); if (/^dk[1-4]$/.test(h)) setTimeout(() => document.getElementById(h)?.scrollIntoView({block: "start"}), 60); } } });
})();

/* ---------- Nov 8 2:30 PM (Dom: "make these four 20x better"): globe taps ----------
   Tap a ring segment or position: that player's line in a bottom sheet. Tap the globe: both lineups side by side,
   the week's Yahoo win-chance trend read by read, the gap and projections, with buttons to the alerts and the full card. */
const DORD = {Thu: 0, Fri: 1, Sat: 2, Sun: 3, Mon: 4, Tue: 5, Wed: 6};
const whenKey = (w) => { const m = /^(\w{3})\s+(\d{1,2}):(\d{2})\s*(AM|PM)/i.exec(w || ""); if (!m) return null; let h = +m[2] % 12; if (/pm/i.test(m[4])) h += 12; return (DORD[m[1]] ?? 9) * 1440 + h * 60 + +m[3]; };
function nextUp(L){ const pre = [...L.players, ...L.oppPlayers].filter(p => isStarter(p) && !started(p) && !isOut(p) && whenKey(p.when) !== null);
  if (!pre.length) return ""; pre.sort((a, b) => whenKey(a.when) - whenKey(b.when)); const w = pre[0].when, today = PT(new Date().toISOString(), {weekday: "short"});
  return w.startsWith(today + " ") ? w.slice(today.length + 1) : w; }
const STW = {ok: "Fine · still to play", live: "Playing now", trbl: "Questionable / doubtful", trblon: "Playing · questionable tag", out: "Out", bye: "On bye", done: "Game over", empty: "Empty spot / no projection - fill it"};
function sheetHost(){ let b = $("#gback"); if (!b){ b = document.createElement("div"); b.id = "gback"; b.hidden = true; document.body.appendChild(b);
    const sh = document.createElement("div"); sh.id = "gsheet"; sh.setAttribute("role", "dialog"); sh.setAttribute("aria-modal", "true"); sh.hidden = true; document.body.appendChild(sh); }
  return $("#gsheet"); }
function showSheet(html, lc){ const sh = sheetHost(); sh.innerHTML = `<div class="gsg"></div>` + html; sh.style.setProperty("--lc", lc); sh.hidden = false; $("#gback").hidden = false;
  requestAnimationFrame(() => { sh.classList.add("up"); $("#gback").classList.add("up"); }); }
function closeSheet(){ const sh = $("#gsheet"), b = $("#gback"); if (!sh) return; sh.classList.remove("up"); b.classList.remove("up"); setTimeout(() => { sh.hidden = true; b.hidden = true; }, 220); }
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSheet(); });
function plRow(p){ const s = ringState(p), f = manFinal(p, "y");
  return `<div class="gpr ${s}"><i></i><span class="ps">${esc(POSAB(p.slot))}</span><span class="pn">${esc(p.name)}<em>${esc([p.tm, p.status].filter(Boolean).join(" · "))}</em></span><span class="pp">${f1(pts(p))}<em>${started(p) && !isDone(p) ? "→ " + f1(f) : isDone(p) ? "final" : "proj " + f1(f)}</em></span></div>`; }
function plPop(key){ const [slug, side, idx] = key.split("|"), k = KEYOF[slug], L = lgS(k); if (!L) return;
  const list = (side === "m" ? L.players : L.oppPlayers).filter(isStarter), p = list[+idx]; if (!p) return; const s = ringState(p), ig = igOf(p);
  showSheet(`<div class="gsh"><b>${DK[k]}</b><span>${side === "m" ? "Your" : esc(L.opp) + "'s"} ${esc(p.slot || "")}</span><button type="button" class="gx" data-shclose aria-label="Close">✕</button></div>
    <div class="gpl"><div class="gpn">${esc(p.name)}<em>${esc(p.tm || "")}</em></div>
      <div class="gst ${s}"><i></i>${STW[s]}${p.status ? " · " + esc(p.status) : ""}</div>
      <div class="gnums"><div><span>POINTS</span><b>${f1(pts(p))}</b></div><div><span>YAHOO PROJ</span><b>${f1(+p.proj || 0)}</b></div><div><span>PROJ FINAL</span><b>${f1(manFinal(p, "y"))}</b></div></div>
      <div class="gwh">Game: <b>${esc(p.when || "-")}</b>${ig ? `<br>${esc(ig.note)} <span class="mute">(RotoWire)</span>` : ""}</div>
      <div class="gft">Yahoo read ${esc(PT(S.stamp, {month: "short", day: "numeric", hour: "numeric", minute: "2-digit"}))}</div></div>
    <div class="gbt"><button type="button" data-sheet="${slug}">Both lineups</button><button type="button" data-jump="${slug}" data-shclose>Open ${DK[k]} card</button></div>`, HEX[k]);
}
function trendSvg(k, y){ const es = trailEntries().filter(e => S && e.w === S.week && e.lg && e.lg[k] && e.lg[k].y !== undefined && e.lg[k].y !== null && e.t < S.stamp).map(e => ({t: e.t, y: +e.lg[k].y}));
  es.push({t: S.stamp, y}); const W = 300, H = 74, pad = 6, n = es.length;
  const X = (i) => n < 2 ? W / 2 : pad + i * (W - 2 * pad) / (n - 1), Y = (v) => pad + (100 - v) * (H - 2 * pad) / 100;
  const zc = (v) => v >= 55 ? "#3DDC84" : v >= 45 ? "#F7B32B" : "#FF4D57";
  const line = es.map((e, i) => `${X(i).toFixed(1)},${Y(e.y).toFixed(1)}`).join(" ");
  return `<svg class="gtr" viewBox="0 0 ${W} ${H}" role="img" aria-label="Yahoo chance to win this week, read by read: ${es.map(e => Math.round(e.y) + "%").join(", ")}">
    <rect x="0" y="${Y(55)}" width="${W}" height="${Y(45) - Y(55)}" fill="#F7B32B" opacity=".08"/>
    <line x1="0" x2="${W}" y1="${Y(50)}" y2="${Y(50)}" stroke="#8E98AE" stroke-dasharray="2 3" stroke-width=".8" opacity=".6"/>
    <text x="${W - 2}" y="${Y(50) - 2}" text-anchor="end" class="gtl">50%</text>
    ${n > 1 ? `<polyline points="${line}" fill="none" stroke="${zc(y)}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` : ""}
    ${es.map((e, i) => `<circle cx="${X(i).toFixed(1)}" cy="${Y(e.y).toFixed(1)}" r="${i === n - 1 ? 3.6 : 1.8}" fill="${zc(e.y)}"><title>${esc(PT(e.t, {weekday: "short", hour: "numeric", minute: "2-digit"}))}: ${Math.round(e.y)}%</title></circle>`).join("")}</svg>
    <div class="gtk"><span>${n > 1 ? esc(PT(es[0].t, {weekday: "short", hour: "numeric", minute: "2-digit"})) + " · " + Math.round(es[0].y) + "%" : "first read"}</span><span>now · <b style="color:${zc(y)}">${wp2(y)}%</b></span></div>`; }
function openSheet(slug){ const k = KEYOF[slug], L = lgS(k); if (!L) return; const y = chance(L, "y"), F = finals(L), me = score(L.players), op = score(L.oppPlayers), mg = me - op;
  const a = L.players.filter(isStarter), b = L.oppPlayers.filter(isStarter), n = Math.max(a.length, b.length), live = aFor(k, aLive);
  showSheet(`<div class="gsh"><b>${DK[k]}</b><span>${esc(k === "MOST" ? "Most Important" : LGFULL[k])} <em>vs ${esc(L.opp)}</em></span><button type="button" class="gx" data-shclose aria-label="Close">✕</button></div>
    <div class="gsc"><div><span>YOU</span><b>${f1(me)}</b><em>proj ${f1(F.me)}</em></div><div class="gm2"><span>GAP</span><b class="${Math.abs(mg) < .05 ? "" : mg > 0 ? "up" : "dn"}">${Math.abs(mg) < .05 ? "EVEN" : (mg > 0 ? "▲ " : "▼ ") + Math.abs(mg).toFixed(1)}</b><em>proj gap ${(F.me - F.op >= 0 ? "+" : "") + (F.me - F.op).toFixed(1)}</em></div><div><span>HIM</span><b>${f1(op)}</b><em>proj ${f1(F.op)}</em></div></div>
    <div class="gsec">YAHOO WIN THIS WEEK · READ BY READ</div>${trendSvg(k, y)}
    <div class="gsec">LINEUPS · ${leftOf(L.players).length} OF YOURS LEFT · ${leftOf(L.oppPlayers).length} OF HIS</div>
    <div class="glu"><div>${a.map(plRow).join("")}</div><div>${b.map(plRow).join("")}</div></div>
    <div class="gft">Yahoo read ${esc(PT(S.stamp, {month: "short", day: "numeric", hour: "numeric", minute: "2-digit"}))}${nextUp(L) ? " · next kick " + esc(nextUp(L)) : ""}</div>
    <div class="gbt"><button type="button" data-alerts="${slug}" data-shclose>Alerts${live.length ? " (" + live.length + ")" : ""}</button><button type="button" data-jump="${slug}" data-shclose>Open ${DK[k]} card</button></div>`, HEX[k]);
}
/* Nov 8 (Dom): the floating NEXT/TOP buttons covered Refresh on the first screen - show them only once he has scrolled past the controls */
(function(){ const tb = document.getElementById("topBtns"); if (!tb) return; const f = () => { const c = document.getElementById("ctlTop") || document.getElementById("pickups"); const lim = c ? c.getBoundingClientRect().bottom + scrollY : 700; tb.classList.toggle("off", scrollY < lim - innerHeight + 40); };
  addEventListener("scroll", f, {passive: true}); addEventListener("resize", f); try { new ResizeObserver(f).observe(document.body); } catch (e) { setInterval(f, 2000); } f(); })();
