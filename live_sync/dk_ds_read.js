/* Nov 18 2026 (Dom: "add them ... to my DK Live"): DRAFT SHARKS weekly projections - a free LOOK-AHEAD CHECK beside Clay.
   Reads ONLY what the free public page shows (Rankings tab, PPR): Floor / Consensus / DS / Ceiling / 3D projection for about
   250 players, for the current week and every week through 18. The full stat lines are a paid Insider feature - never read.
   Each week is its own page, so the read is one call per page (the site reloads the page to change weeks):
     open https://www.draftsharks.com/weekly-rankings/<W>/ppr  ->  await DKD.grab()   (it prints the next page to open)
     ... repeat for each week through 18 ...  ->  DKD.handoff()  (opens the GitHub upload page for yahoo_drop/draftsharks,
     the file rides in the address, same as the FTN read).  DKD.reset() clears a half-finished read. */
window.DKD={sl:ms=>new Promise(r=>setTimeout(r,ms)),T:x=>(x&&x.innerText||'').replace(/\s+/g,' ').trim(),
stamp(){const e=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'short',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).formatToParts(new Date).map(t=>[t.type,t.value]));return `${e.weekday} ${e.month} ${e.day} ${e.year} ${e.hour}:${e.minute} ${e.dayPeriod} PT`},
rows(){return [...document.querySelectorAll('[data-player-row]')]},
store(){try{return JSON.parse(sessionStorage.getItem('dkd_store')||'null')}catch(e){return null}},
reset(){sessionStorage.removeItem('dkd_store');return 'cleared'},
async loadAll(){let n=-1;for(let i=0;i<30;i++){window.scrollTo(0,document.body.scrollHeight);await this.sl(700);const m=this.rows().length;if(m===n&&m>=200)break;n=m}window.scrollTo(0,0);return this.rows().length},
parse(){const out=[];for(const r of this.rows()){const tr=r.querySelector('tr.player-row')||r;const cells=[...tr.querySelectorAll('td')].map(td=>this.T(td));const nums=cells.map(c=>/^-?\d+(\.\d+)?$/.test(c)?+c:null);
 const tail=nums.slice(-5);if(tail.length<5||tail.some(v=>v===null))continue;const pc=cells.find(c=>/\b(QB|RB|WR|TE|K|DEF)\d+\b/.test(c))||'';const tm=(pc.match(/\b([A-Z]{2,3})\s+(QB|RB|WR|TE|K|DEF)\d+/)||[])[1]||'';
 out.push({n:r.getAttribute('data-player-name')||'',pos:r.getAttribute('data-fantasy-position')||'',tm,floor:tail[0],cons:tail[1],ds:tail[2],ceil:tail[3],p3d:tail[4]})}return out},
async grab(){if(!/draftsharks\.com$/.test(location.host))throw new Error('run on draftsharks.com');const m=location.pathname.match(/\/weekly-rankings\/(\d+)\/ppr/);if(!m)throw new Error('open /weekly-rankings/<week>/ppr');const w=+m[1];
 for(let i=0;i<30&&!this.rows().length;i++)await this.sl(500);
 const ppr=[...document.querySelectorAll('button.ds-nav-item')].find(b=>this.T(b)==='PPR');if(!ppr||!/active/.test(ppr.className))throw new Error('PPR is not selected on this page');
 const n=await this.loadAll(),P=this.parse();if(P.length<150)throw new Error('only '+P.length+' rows read for Week '+w);
 let S=this.store();if(!S||(S.week0&&w<S.week0)){S={read:this.stamp(),week0:w,site_updated:(document.body.innerText.match(/Reviewed By[^\n]*?\|\s*([A-Z][a-z]{2} \d+, \d{4} at [\d:]+\s*[ap]m)/)||[])[1]||'',weeks:{}}}
 S.weeks[w]=P;sessionStorage.setItem('dkd_store',JSON.stringify(S));const nx=w<18?`https://www.draftsharks.com/weekly-rankings/${w+1}/ppr`:'done - run DKD.handoff()';
 return `Week ${w}: ${P.length} of ${n} rows | weeks so far ${Object.keys(S.weeks).join(',')} | next: ${nx}`},
handoff(){const S=this.store();if(!S||!Object.keys(S.weeks).length)throw new Error('nothing read - run DKD.grab() on each week first');
 const F={'ds_weekly.json':JSON.stringify(Object.assign({scoring:'PPR (Draft Sharks default)',source:'Draft Sharks weekly rankings, free public page (Rankings tab): floor/consensus/DS/ceiling/3D'},S))};
 const e=encodeURIComponent(JSON.stringify(F));sessionStorage.removeItem('dkd_store');setTimeout(()=>{location.href='https://github.com/DomFantasy01/dk-feeds/upload/main/yahoo_drop/draftsharks#F='+e},300);return 'to GitHub, '+e.length+' chars, weeks '+Object.keys(S.weeks).join(',')}};
