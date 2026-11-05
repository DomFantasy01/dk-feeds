
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
  const seats = L.players.filter(p => !isDone(p) && (isOut(p) || /^D$/i.test(p.status || "") || ((+p.proj || 0) === 0 && !isLive(p))));
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
function astrip(){
  const live = alertsAll().filter(aLive), cnt = (c) => live.filter(x => x.color === c).length;
  const newest = A ? A.generated || A.built : "";
  $("#astrip").innerHTML = `<div class="astrip"><span class="ttl" style="color:${live.length ? (cnt("red") ? "var(--red)" : cnt("gold") ? "var(--amber)" : "var(--ink)") : "var(--up)"}">${live.length}</span>
    <span class="tal">${cnt("red")} act now · ${cnt("gold")} monitor · ${cnt("grey")} noted${newest ? " · checked " + esc(ago(newest)) : ""}</span>
    <button type="button" class="abtn${ARM === "del:ALL" ? " arm" : ""}" data-abulk="del:ALL">${ARM === "del:ALL" ? "Tap again: delete " + live.length : "Delete all"}</button>
    <button type="button" class="abtn sep${ARM === "sep:ALL" ? " arm" : ""}" data-abulk="sep:ALL">${ARM === "sep:ALL" ? "Tap again: separate " + live.length : "Separate all"}</button></div>
    <div class="note">${KEYS.map(k => { const n = aFor(k, aLive); return `<a href="#${SLUG[k]}" data-jump="${SLUG[k]}" style="color:${LCOL[k]};text-decoration:none;font-weight:700">${DK[k]} ${n.length}</a>`; }).join(" · ")} · Each alert sits in its league's card. Separate keeps it for 7 days at the bottom of the page.</div>`;
}
function separated(){
  const xs = alertsAll().filter(aSep).sort(aSort);
  $("#sepCnt").textContent = xs.length ? xs.length + " kept 7 days" : "none";
  $("#sep").innerHTML = xs.length ? `<div class="ahd"><span class="tal">Delete for good:</span><button type="button" class="abtn${ARM === "delsep:ALL" ? " arm" : ""}" data-abulk="delsep:ALL">${ARM === "delsep:ALL" ? "Tap again: delete " + xs.length : "Delete all " + xs.length}</button>
    ${KEYS.map(k => { const n = xs.filter(x => BYPRINT[x.lg] === k).length; return n ? `<button type="button" class="abtn${ARM === "delsep:" + k ? " arm" : ""}" data-abulk="delsep:${k}">${ARM === "delsep:" + k ? "Tap again" : DK[k] + " · " + n}</button>` : ""; }).join("")}</div>
    <div class="alist">${xs.map(x => alertCard(x, true)).join("")}</div>` : `<div class="empty">Nothing separated.</div>`;
}
function renderAlertsOnly(){ astrip(); separated(); for (const k of KEYS){ const el = document.getElementById("alb-" + SLUG[k]); if (el) el.innerHTML = alertsBlock(k); } meters(); }

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
  separated(); footer();
  scrollTo(0, y);
}
document.addEventListener("toggle", (e) => { const d = e.target; if (!d.matches || !d.matches("details[data-fold]")) return; FOLDS[d.dataset.fold] = d.open; store.set("folds", FOLDS); }, true);

/* ---------- events ---------- */
function rmsg(t, bad){ const el = $("#rmsg"); el.textContent = t; el.hidden = false; el.style.background = bad ? "#FBE4E5" : "#F2E6C4"; clearTimeout(rmsg.t); rmsg.t = setTimeout(() => el.hidden = true, 9000); }
document.addEventListener("click", async (e) => {
  const t = e.target.closest ? e.target : e.target.parentElement;
  const j = t.closest("[data-jump]"); if (j){ e.preventDefault(); const id = j.dataset.jump; if (id === "top") scrollTo({top: 0, behavior: "smooth"}); else document.getElementById(id)?.scrollIntoView({behavior: "smooth", block: "start"}); return; }
  if (t.closest("#stat")){ const b = $("#hc"); b.hidden = !b.hidden; $("#stat").setAttribute("aria-expanded", String(!b.hidden)); renderHealth(); return; }
  if (t.id === "hcAll"){ HC_ALL = !HC_ALL; renderHealth(); return; }
  if (t.id === "goTop"){ scrollTo({top: 0, behavior: "smooth"}); return; }
  if (t.id === "goNext"){ const cs = KEYS.map(k => document.getElementById(SLUG[k])).filter(Boolean); const nx = cs.find(c => c.getBoundingClientRect().top > 100) || cs[0]; nx && nx.scrollIntoView({behavior: "smooth", block: "start"}); return; }
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
let wakeLock = null;
/* sticky scoreboard once the meters scroll away */
try { new IntersectionObserver(([en]) => { $("#sticky").hidden = en.isIntersecting || !S; }, {threshold: 0}).observe($("#metersFrame")); } catch(_){}
setInterval(() => { renderStatus(); if (S) meters(); }, 60000);

/* ---------- data ---------- */
(async () => {
  const db = await window.claude?.use?.("db");
  if (!db){ $("#statTxt").innerHTML = `<span class="late">Can't reach the live feed in this view.</span> Open Dark Knight Live from your Claude sidebar or artifact list.`; $("#meters").innerHTML = `<div class="empty" style="grid-column:1/-1">No data in this view.</div>`; return; }
  DB = db;
  const val = (s) => s && (s.data ? s.data() : s);
  const watch = (path, fn) => { try { db.doc(path).onSnapshot(s => { fn(val(s)); }, () => {}); } catch(_){ db.doc(path).get().then(s => fn(val(s))).catch(() => {}); } };
  const tm = setTimeout(() => { if (!S) $("#statTxt").innerHTML = `<span class="late">The live feed hasn't answered in 10 seconds.</span> It keeps trying.`; }, 10000);
  try { TR = val(await db.doc("live/trail").get()) || {entries: []}; } catch(_){ TR = {entries: []}; }
  if (!Array.isArray(TR.entries)) TR = {entries: []};
  watch("live/alert_marks", v => { MK = Object.assign({}, v || {}); if (S) renderAll(); });
  watch("live/moves", v => { MV = v || null; if (S) renderAll(); });
  watch("live/health", v => { H = v || null; renderStatus(); renderHealth(); });
  watch("live/alerts", v => { A = v || null; if (S) renderAll(); });
  watch("live/models", v => { if (v){ M = v; if (S){ renderAll(); trailAdd(); } } });
  watch("live/state", v => { if (v && v.leagues){ clearTimeout(tm); S = v; renderAll(); if (M) trailAdd(); } });
})();
