// DK YAHOO PULL - the scheduled Yahoo read (Thu Oct 8 2026). Read-only: it only opens pages; it never clicks or changes anything on Yahoo.
// Lives at live_sync/dk_yahoo_pull.js in DomFantasy01/dk-feeds. A Chrome tab on football.fantasysports.yahoo.com loads it with:
//   if(!window.DK){(0,eval)(await (await fetch('https://raw.githubusercontent.com/DomFantasy01/dk-feeds/main/live_sync/dk_yahoo_pull.js?'+Date.now())).text())}
// then:  await DK.start()   (once)   ->  await DK.step()  (repeat until it returns done)  ->  DK.handoff()  (sends the bundle to GitHub)
// Every step survives page loads: progress is kept in this tab's sessionStorage.
// WHAT IT READS (Pacific weekday):
//   Mon      the week being played: Dom's four matchup pages (scores so far)            -> Post-Mortem, provisional
//   Tue      the week just played, final (4 pages) + the new week's full set below     -> Post-Mortem final + the new week
//   Wed/other  the current week's full set: all matchups in all four leagues (win %, kickoff windows, records),
//            Dom's four matchups, standings, Dom's rosters, every team's roster (for the Radar)
// Yahoo (Oct 8 evening) moved this week's matchup pages to a new layout that only exists once the page renders and shows
// short names ("J. Goff"); full names come from the team pages by Yahoo player id. Both the old and new layouts are read.
(()=>{
const DOM={269381:2,1519795:7,1507991:2,864215:6}, LGN={269381:12,1519795:12,1507991:14,864215:10};
const LAB={269381:'DK I',1519795:'DK II',1507991:'DK III',864215:'DK IV'}, IDX={269381:1,1519795:2,1507991:3,864215:4};
const SK='dk_pull_v1', W1TUE=Date.UTC(2026,8,8);          // Tue Sep 8 2026 starts NFL Week 1 (opener Thu Sep 10)
const cl=s=>(s||'').replace(/\s+/g,' ').trim();
const load=()=>{try{return JSON.parse(sessionStorage.getItem(SK)||'null')}catch(e){return null}};
const save=s=>sessionStorage.setItem(SK,JSON.stringify(s));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function pt(){const p={};new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'short',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit',hour12:true})
  .formatToParts(new Date()).forEach(x=>p[x.type]=x.value);
  const h=+p.hour, m=p.minute, ap=p.dayPeriod.toUpperCase(), h24=(h%12)+(ap==='PM'?12:0);
  const ymd=Date.UTC(+p.year,['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].indexOf(p.month),+p.day);
  return {stamp:`${p.weekday} ${p.month} ${p.day} ${h}:${m} ${ap} PT`, pulled:`${p.weekday} ${p.month} ${p.day.padStart(2,'0')} ${p.year} ${h}:${m} ${ap} PT`, tag:`${p.weekday.toLowerCase()}${String(h24).padStart(2,'0')}${m}`,
          day:p.weekday.toLowerCase(), week:Math.floor((ymd-W1TUE)/864e5/7)+1, file:`${p.year}${String(new Date(ymd).getUTCMonth()+1).padStart(2,'0')}${p.day.padStart(2,'0')}_${String(h24).padStart(2,'0')}${m}`};}
async function doc(u){const r=await fetch(u,{credentials:'include'});if(!r.ok)throw new Error('HTTP '+r.status+' '+u);return new DOMParser().parseFromString(await r.text(),'text/html');}

// ---------- team pages (server-rendered, read in the background): full names by player id, rosters, slots, injury tags
function teamPage(d){
  const ids={}, rows=[], names=[];
  [...d.querySelectorAll('a[href*="/nfl/players/"]')].forEach(a=>{const m=(a.getAttribute('href')||'').match(/players\/(\d+)/);const n=cl(a.textContent);
    if(m&&n&&!/Note|Video|Forecast/.test(n))ids[m[1]]=n;});
  [...d.querySelectorAll('table tbody tr')].forEach(r=>{
    const a=r.querySelector('a[href*="/nfl/players/"]:not([href*="news"])')||r.querySelector('a[href*="/nfl/teams/"]');
    const nm=a?cl(a.textContent):''; if(!nm||/Note|Video/.test(nm))return;
    const slot=cl((r.querySelector('.pos-label')||r.querySelector('td'))?.textContent);
    if(!/^(QB|RB|WR|TE|W\/R\/T|W\/R|Q\/W\/R\/T|SUPER|K|DEF|BN|IR)$/.test(slot))return;
    const st=cl((r.querySelector('.F-injury,.ysf-player-status')||{}).textContent);
    rows.push({slot,player:nm,status:st}); names.push(nm);});
  const seen=new Set(); const R=rows.filter(x=>{const k=x.slot+'|'+x.player;if(seen.has(k))return false;seen.add(k);return true;});
  return {ids,rows:R,names:[...new Set(names)]};}

// ---------- matchup page (rendered tab): both layouts, columns found by their header names
function readMatchup(names){
  const tables=[...document.querySelectorAll('table')].filter(t=>{const h=t.querySelector('tr');return h&&/Player/.test(h.textContent)&&/Pos/.test(h.textContent);});
  if(!tables.length)return null;
  const me=[],op=[];
  const num=s=>{const m=(s||'').match(/\d+\.\d{2}/g);return m?m:[];};
  const info=(cell)=>{
    if(!cell)return null;
    const idEl=cell.querySelector('[data-ys-playerid]'); let id=idEl?idEl.getAttribute('data-ys-playerid'):null;
    const a=cell.querySelector('a[href*="/nfl/players/"]'); if(!id&&a){const m=a.getAttribute('href').match(/players\/(\d+)/);id=m&&m[1];}
    const t=cl(cell.textContent); if(!t)return null;
    const tp=t.match(/([A-Za-z]{2,3}) - (QB|RB|WR|TE|K|DEF)/);
    let short=cl((idEl&&idEl.querySelector('div'))?.textContent)||(a?cl(a.textContent):'')||(tp?t.slice(0,t.indexOf(tp[0])):t);
    short=short.replace(/(Video Forecast|No new player Notes|New Player Note|Player Notes?).*$/,'').trim();
    let name=(id&&names[id])||short;
    const after=t.split(/No new player Notes|New Player Notes?|Player Notes?/).slice(-1)[0]||'';
    const sm=after.match(/^\s*(IR-R|IR|SUSP|PUP|NA|Q|D|O)(?=\s*(Sun|Mon|Tue|Wed|Thu|Fri|Sat|Final|No Game|1st|2nd|3rd|4th|OT|Half|End|$))/);
    let st=sm?sm[1]:'';
    if(!st){const om=t.match(new RegExp(short.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(IR-R|IR|SUSP|PUP|Q|D|O)(?=Video|Player|No new|New)'));if(om)st=om[1];}
    const ko=(t.match(/(Thu|Fri|Sat|Sun|Mon|Tue) (\d{1,2}:\d{2}) ([AP]M)/i)||[]);
    const game=/Final/.test(after)?'final':(/(1st|2nd|3rd|4th|OT|Half|End)/.test(after)?'live':(ko[0]?'pre':(/No Game|Bye/i.test(after)?'none':'')));
    const gid=(cell.querySelector('a[href*="gid="]')?.getAttribute('href')||'').match(/gid=(\d{8})/);
    return {id,name,team:tp?tp[1]:'',pos:tp?tp[2]:'',status:st,ko:ko[0]?`${ko[1]} ${ko[2]} ${ko[3].toLowerCase()}`:'',game,gdate:gid?gid[1]:''};};
  for(const tb of tables){
    const rows=[...tb.querySelectorAll('tr')]; const h=[...rows[0].children].map(x=>cl(x.textContent));
    const P=h.map((x,i)=>x==='Pos'?i:-1).filter(i=>i>=0); if(!P.length)continue;
    const L=(lab)=>{let k=-1;h.forEach((x,i)=>{if(x===lab&&i<P[0])k=i;});return k;};
    const R=(lab)=>h.findIndex((x,i)=>x===lab&&i>P[P.length-1]);
    const lc={pl:h.indexOf('Player'),pr:L('Proj'),pt:L('Fan Pts')}, rc={pl:R('Player'),pr:R('Proj'),pt:R('Fan Pts')};
    for(const r of rows.slice(1)){
      const c=[...r.children]; const slot=cl(c[P[0]]?.textContent); if(!slot||/total/i.test(slot))continue;
      for(const [side,ix,out] of [['me',lc,me],['op',rc,op]]){
        const f=info(c[ix.pl]); if(!f)continue;
        const pr=num(c[ix.pr]?.textContent), ptv=num(c[ix.pt]?.textContent);
        out.push({slot,...f,proj:pr[0]||'',projLive:pr[1]||pr[0]||'',pts:ptv[0]||''});}}}
  const body=cl(document.body.innerText);
  const recs=[...body.matchAll(/(\d+) ?- ?(\d+) ?- ?(\d+) \| (\d+(?:st|nd|rd|th))/g)].map(m=>`${m[1]}-${m[2]}-${m[3]}/${m[4]}`);
  const fav=body.match(/(Favorite|Underdog) (\d+)%[^%]{0,80}?(\d+)% (Favorite|Underdog)/);
  const lg=(location.pathname.match(/f1\/(\d+)/)||[])[1], mid=new URLSearchParams(location.search).get('mid1');
  const tl=[...document.querySelectorAll('a')].map(a=>[(a.getAttribute('href')||'').match(new RegExp('/f1/'+lg+'/(\\d+)$')),cl(a.textContent)]).filter(x=>x[0]&&x[1]&&!/^My Team$/i.test(x[1])).map(x=>[x[0][1],x[1]]);
  let mine=tl.find(x=>x[0]===mid), opp=mine?tl.slice(tl.indexOf(mine)+1).find(x=>x[0]!==mid):null;
  const big=[...document.querySelectorAll('.Fz-xxl.Ell')].map(e=>cl(e.textContent));
  return {me,op,recs,fav:fav?[fav[2],fav[3]]:['',''],mine:mine?mine[1]:(big[0]||''),opp:opp?opp[1]:(big[1]||''),oppId:opp?opp[0]:null,
          week:(body.match(/Week (\d+):/)||[])[1]};}

// kickoff windows: 0 THU/FRI/SAT · 1 SUN before 9am · 2 SUN 9-12 · 3 SUN 12-4pm · 4 SUN night · 5 MON/TUE (same as the method of record)
function win(p){const m=(p.ko||'').match(/(Thu|Fri|Sat|Sun|Mon|Tue) (\d+):(\d+) (am|pm)/i);
  if(!m){if(p.gdate){const d=new Date(Date.UTC(+p.gdate.slice(0,4),+p.gdate.slice(4,6)-1,+p.gdate.slice(6,8))).getUTCDay();if(d>=4&&d<=6)return 0;if(d===1||d===2)return 5;}return -1;}
  const h=+m[2]%12+(m[4].toLowerCase()==='pm'?12:0),d=m[1];if(d=='Thu'||d=='Fri'||d=='Sat')return 0;if(d=='Mon'||d=='Tue')return 5;if(h<9)return 1;if(h<12)return 2;if(h<16)return 3;return 4;}
function winLine(lg,team,rec,pct,S){const w=[0,0,0,0,0,0],c=[0,0,0,0,0,0];let tot=0,nog=0;
  S.forEach(r=>{if(/^(BN|IR)/.test(r.slot))return;const v=parseFloat(r.game==='final'?r.pts:(r.game==='live'?r.projLive:r.proj))||0,x=win(r);if(x<0){nog++;return;}w[x]+=v;c[x]++;tot+=v;});
  return [lg,team,rec,pct,w.map(v=>v.toFixed(2)).join(' '),c.join(' '),tot.toFixed(2),nog].join('~');}
const side=S=>S.filter(r=>!/^(BN|IR)/.test(r.slot)).map(r=>[r.slot,r.name,r.team,r.status,r.ko,r.proj||'–',r.pts||'–'].join('^')).join('|');

const DK={
 async start(force){            // force = 'mon'|'tue'|'wed' to override the weekday (testing)
  const T=pt(), day=force||T.day, wk=T.week; const S={t:T,day,log:[],names:{},files:{},queue:[],dom:{},win:{},seen:{},done:0};
  const fullW=wk;                                       // the week ahead (Tue..Mon window that holds today)
  const pmW=(day==='mon')?wk:(day==='tue'?wk-1:null);  // the week being looked back on
  S.pmW=pmW; S.fullW=(day==='mon')?null:fullW;
  // team pages for every team in all four leagues: full names, Dom's rosters, every roster (Radar)
  const allR=[], dr={source:"Yahoo team pages (Dom's four teams), read in Chrome by the scheduled Yahoo read",pulled_pt:T.pulled,week:S.fullW||pmW,leagues:{}};
  let bad=0;
  for(const lg of Object.keys(LGN)) for(let t=1;t<=LGN[lg];t++){
    let tp; try{tp=teamPage(await doc(`/f1/${lg}/${t}`));}catch(e){bad++;S.log.push('team page failed '+lg+'/'+t);continue;}
    Object.assign(S.names,tp.ids);
    if(!tp.names.length){S.log.push(`team ${lg}/${t}: no rows`);}
    allR.push([IDX[lg],t,tp.names.join('|')].join('~'));
    if(+t===DOM[lg]) dr.leagues[LAB[lg]]={league_id:lg,players:tp.rows,count:tp.rows.length};}
  S.allR=allR; S.dr=dr;
  if(S.fullW){                 // standings (server-rendered)
    const out=[];for(const lg of Object.keys(DOM)){const d=await doc(`/f1/${lg}`);
      const t=d.querySelector('#standingstable')||[...d.querySelectorAll('table')].find(x=>/W-L-T|Pts For/i.test(x.textContent));
      out.push(lg+'#'+(t?[...t.querySelectorAll('tbody tr')].map(r=>[...r.children].map(c=>cl(c.textContent)).join('^')).join('|'):'NONE'));}
    S.standings=out.join('\n');}
  if(pmW&&(day==='tue')) for(const lg of Object.keys(DOM)) S.queue.push({k:'pm',lg,w:pmW,mid:DOM[lg]});
  if(day==='mon') for(const lg of Object.keys(DOM)) S.queue.push({k:'pm',lg,w:pmW,mid:DOM[lg]});
  if(S.fullW) for(const lg of Object.keys(DOM)) S.queue.push({k:'all',lg,w:S.fullW,mid:DOM[lg]});
  S.total=S.queue.length; save(S);
  location.href=this._url(S.queue[0]);
  return `started ${day} (PT ${T.stamp}) | look-back week ${pmW||'-'} | week ahead ${S.fullW||'-'} | team pages read ${allR.length}/48${bad?' ('+bad+' failed)':''} | first page loading`;},
 _url(q){return `https://football.fantasysports.yahoo.com/f1/${q.lg}/matchup?week=${q.w}&mid1=${q.mid}`;},
 async step(){
  const S=load(); if(!S)return 'no pull in progress - run DK.start() first';
  if(!S.queue.length)return 'done - run DK.handoff()';
  const q=S.queue[0]; const want=`/f1/${q.lg}/matchup`;
  if(!location.pathname.startsWith(want)||new URLSearchParams(location.search).get('mid1')!=String(q.mid)||new URLSearchParams(location.search).get('week')!=String(q.w)){location.href=this._url(q);return 'navigating to '+this._url(q);}
  let M=null, bye=false;
  for(let i=0;i<40;i++){M=readMatchup(S.names);if(M&&M.me.length>=8&&M.op.length>=8&&M.mine)break;
    if(/Week \d+:[^]{0,40}?BYE vs\./.test(cl(document.body.innerText).slice(0,1500))){bye=true;break;}await sleep(500);}
  const body0=cl(document.body.innerText); const med=(body0.match(/Median (\d+\.\d+)/)||[])[1];
  if(bye){S.log.push(`${LAB[q.lg]} team ${q.mid}: BYE this week (empty team slot) - nothing to read`);}
  else if(!M||M.me.length<8){S.log.push(`FAILED to read ${q.lg} week ${q.w} mid ${q.mid}`);}
  else{
    const st=M.me.filter(r=>!/^(BN|IR)/.test(r.slot)).length, so=M.op.filter(r=>!/^(BN|IR)/.test(r.slot)).length;
    if(q.k==='pm'||+q.mid===DOM[q.lg]){(q.k==='pm'?(S.pmDom=S.pmDom||{}):S.dom)[q.lg]=q.lg+'#'+side(M.me)+'##'+side(M.op);
      if(med){S.med=S.med||{};S.med[q.k+q.lg]=med;}}
    if(q.k==='all'){
      S.win[q.lg]=S.win[q.lg]||[];
      S.win[q.lg].push(winLine(q.lg,M.mine,M.recs[0]||'',M.fav[0],M.me),winLine(q.lg,M.opp,M.recs[1]||'',M.fav[1],M.op));
      if(M.oppId)(S.seen[q.lg]=S.seen[q.lg]||[]).push(+M.oppId); else S.log.push(`no opponent id on ${q.lg}/${q.mid}`);}
    S.log.push(`${LAB[q.lg]} wk${q.w} ${M.mine} vs ${M.opp}: ${st}+${so} starters`);}
  if(q.k==='all'){S.seen[q.lg]=S.seen[q.lg]||[]; S.seen[q.lg].push(+q.mid);          // the sweep carries on even after a failed or bye page
    for(let t=1;t<=LGN[q.lg];t++) if(!S.seen[q.lg].includes(t)&&!S.queue.some(x=>x.lg===q.lg&&x.mid===t&&x.k==='all')){S.queue.splice(1,0,{k:'all',lg:q.lg,w:q.w,mid:t});S.total++;break;}}
  S.queue.shift(); S.done++; save(S);
  if(S.queue.length){location.href=this._url(S.queue[0]);return `read ${S.done} of ${S.total} so far - next page loading`;}
  return 'done - run DK.handoff()';},
 files(){
  const S=load(), T=S.t, F={};
  const hdrM=w=>`# Yahoo Week ${w} matchup pages for Dom's four teams, ${T.stamp}. lg#ME starters ## OPP starters ; slot^player^team^status^kickoff(PT)^yahoo proj^points (scheduled Yahoo read)`;
  const medL=k=>(S.med&&S.med[k+'864215'])?`# DK IV league median (Yahoo, same read): ${S.med[k+'864215']}\n`:'';
  if(S.pmDom&&Object.keys(S.pmDom).length) F[`wk${S.pmW}/dom_matchups_${T.tag}.txt`]=hdrM(S.pmW)+'\n'+medL('pm')+Object.keys(DOM).filter(l=>S.pmDom[l]).map(l=>S.pmDom[l]).join('\n')+'\n';
  if(S.fullW){
    const w=S.fullW;
    if(Object.keys(S.dom).length) F[`wk${w}/dom_matchups_${T.tag}.txt`]=hdrM(w)+'\n'+medL('all')+Object.keys(DOM).filter(l=>S.dom[l]).map(l=>S.dom[l]).join('\n')+'\n';
    const n=Object.values(S.win).reduce((a,v)=>a+v.length,0), byes=S.log.filter(l=>/BYE this week/.test(l)).length;
    F[`wk${w}/league_windows_${T.tag}.txt`]=`# Yahoo Week ${w} matchup pages, every team's SET lineup, ${T.stamp}. lg~team~record~yahoo win%~6 windows (THU, SUN early, SUN 10a, SUN 1p, SUN night, MON)~counts~total~starters w/o game\n# ${n} of 48 teams pulled${byes?` (${byes} empty team slot${byes>1?'s':''} on a bye)`:''}. Pairs listed consecutively. (scheduled Yahoo read)\n`+Object.keys(DOM).map(l=>(S.win[l]||[]).join('\n')).filter(Boolean).join('\n')+'\n';
    if(S.standings) F[`wk${w}/standings_${T.tag}.txt`]=`# Yahoo league home standings tables, ${T.stamp}. Rows: rank^team^W-L-T^div rec^PF^PA^streak^FAAB^waiver^moves ; NEXTDOOR has no divisions/FAAB: rank^team^W-L-T^PF^PA^streak^waiver^moves. Bare words = division headers.\n`+S.standings+'\n';
    F[`wk${w}/dom_rosters.json`]=JSON.stringify(S.dr,null,1)+'\n';
    F[`wk${w}/all_rosters_${T.tag}.txt`]=`# Yahoo team pages, every team in all four leagues, ${T.stamp}. league(1=DK I 269381, 2=DK II 1519795, 3=DK III 1507991, 4=DK IV 864215)~team id~players (DEF listed by nickname). (scheduled Yahoo read)\n`+S.allR.join('\n')+'\n';}
  return F;},
 report(){const S=load();if(!S)return 'nothing';const F=this.files();
  return {day:S.day,read:S.t.stamp,lookback:S.pmW,ahead:S.fullW,files:Object.fromEntries(Object.entries(F).map(([k,v])=>[k,v.length])),
          leagues_read:Object.fromEntries(Object.entries(S.win).map(([k,v])=>[LAB[k],v.length])),log:S.log.slice(-14)};},
 async handoff(){
  const S=load(), F=this.files(); const body=JSON.stringify({read_pt:S.t.stamp,day:S.day,lookback_week:S.pmW,week_ahead:S.fullW,log:S.log,files:F});
  const h=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(body)))).map(b=>b.toString(16).padStart(2,'0')).join('').slice(0,16);
  const path=`yahoo_drop/_inbox/pull_${S.t.file}.json`;
  setTimeout(()=>{location.href=`https://github.com/DomFantasy01/dk-feeds/new/main?filename=${path}#dk=${encodeURIComponent(body)}&h=${h}`;},200);
  return {path,sha16:h,bytes:body.length};},
 reset(){sessionStorage.removeItem(SK);return 'cleared';}
};
window.DK=DK;
})();
