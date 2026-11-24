/* DR. ROTO WEEKLY PROJECTIONS - Chrome read (Nov 24 2026, Dom subscribed to Dr. Roto All Access and said: "put them on our meter ...
   Ratcliffe and Dr. Roto as the top pillars"). Run on https://drroto.com/nfl/dashboard/ while signed in (Dom's login, "Remember me").
   The dashboard's numbers (DraftKings scoring, full PPR + yardage bonuses; "Tools, projections and data powered by DailyAmbush.com")
   come from the site's own feed for the slate picked in the page. This script picks the CURRENT week and the "Full week" slate
   with the most games (every game, Wed/Thu through Mon), lets the page load it, and keeps what the page received:
   name, pos, team, opponent, DK points, FD points, floor, ceiling, targets, carries, snap %, ownership.
   Nothing is typed, clicked on any account page, or changed on the site. READ ONLY.
   Usage:  await DKR.run()   then   DKR.handoff()   (moves the tab to the GitHub upload page for yahoo_drop/drroto;
           finish there with dk_gh_drop.js and  await DKG.drop('<message>') ) */
window.DKR={sl:ms=>new Promise(r=>setTimeout(r,ms)),
stamp(){const e=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'short',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).formatToParts(new Date).map(t=>[t.type,t.value]));return `${e.weekday} ${e.month} ${e.day} ${e.year} ${e.hour}:${e.minute} ${e.dayPeriod} PT`},
hook(){if(window.__dkrHook)return;window.__dkrHook=1;window.__dkrCap=[];const of=window.fetch;window.fetch=async(...a)=>{const r=await of(...a);try{const u=String(a[0]&&a[0].url||a[0]);if(u.includes('view=dashboard'))r.clone().json().then(j=>window.__dkrCap.push({u,j})).catch(()=>{})}catch(e){}return r};
 const oo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u,...x){this.addEventListener('load',()=>{try{if(String(u).includes('view=dashboard'))window.__dkrCap.push({u:String(u),j:JSON.parse(this.responseText)})}catch(e){}});return oo.call(this,m,u,...x)}},
sel(){return [...document.querySelectorAll('select')]},
async pick(s,val){if(s.value===val)return false;s.value=val;s.dispatchEvent(new Event('change',{bubbles:true}));return true},
async run(){if(!/drroto\.com$/.test(location.host)||!/\/nfl\/dashboard/.test(location.pathname))throw new Error('run on drroto.com/nfl/dashboard/');
 if(/log ?in|sign ?in/i.test((document.querySelector('header')||document.body).innerText)&&!/Dashboard/.test(document.body.innerText))throw new Error('not signed in to Dr. Roto');
 this.hook();for(let i=0;i<40&&this.sel().length<2;i++)await this.sl(500);const S=this.sel();if(S.length<2)throw new Error('week/slate menus not found');
 const wk=S[0],weeks=[...wk.options].map(o=>+o.value).filter(Boolean),W=Math.max(...weeks);await this.pick(wk,String(W));await this.sl(3500);
 const sl=this.sel()[1],full=[...sl.options].filter(o=>/^Full week/.test(o.text)).map(o=>({v:o.value,t:o.text,g:+((o.text.match(/(\d+) games\s*$/)||[])[1]||0)})).sort((a,b)=>b.g-a.g)[0];
 if(!full)throw new Error('no Full week slate for Week '+W);
 window.__dkrCap=[];const changed=await this.pick(sl,full.v);if(!changed){const o=[...sl.options].find(o=>o.value!==full.v);await this.pick(sl,o.value);await this.sl(2500);window.__dkrCap=[];await this.pick(sl,full.v)}
 let got=null;for(let i=0;i<40&&!got;i++){await this.sl(500);got=(window.__dkrCap||[]).reverse().find(c=>c.u.includes('slateid='+full.v)&&c.j&&c.j.players)}
 if(!got)throw new Error('the Full week slate did not load');const P=got.j.players;if(P.length<150)throw new Error('only '+P.length+' players came back');
 const n=v=>v===null||v===undefined||v===''?null:+v;
 const rows=P.map(p=>({n:p.playername,pos:p.position,tm:p.teamalias,opp:p.opponent,dk:n(p.dk_proj),fd:n(p.fd_proj),floor:n(p.floor_proj),ceil:n(p.ceiling_proj),tgt:n(p.targets),ra:n(p.rush_att),snap:n(p.snap_pct),own:n(p.dk_ownership),ha:p.home_away||'',ou:n(p.game_ou),tt:n(p.team_total)}));
 const at=this.stamp(),m=got.u.match(/gamedate=([\d-]+)/);
 const F={week:W,read:at,slate:full.t,slateid:full.v,gamedate:m?m[1]:'',scoring:'DraftKings (full PPR, 4-pt pass TD, -1 INT, +3 at 300 pass / 100 rush / 100 rec yds)',source:"Dr. Roto NFL Dashboard (drroto.com, Dom's All Access login; projections powered by DailyAmbush.com)",players:rows};
 this.F={'drroto_weekly.json':JSON.stringify(F)};sessionStorage.setItem('dkr_files',JSON.stringify(this.F));
 return at+' | Week '+W+' '+full.t+' | '+rows.length+' players ('+['QB','RB','WR','TE','DST'].map(p=>p+' '+rows.filter(r=>r.pos===p).length).join(', ')+')'},
handoff(){const t=this.F||JSON.parse(sessionStorage.getItem('dkr_files')||'null');if(!t)throw new Error('run DKR.run() first');const e=encodeURIComponent(JSON.stringify(t));setTimeout(()=>{location.href='https://github.com/DomFantasy01/dk-feeds/upload/main/yahoo_drop/drroto?t='+Date.now()+'#F='+e},300);return 'to GitHub, '+e.length+' chars'}};
