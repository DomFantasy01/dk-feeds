/* Nov 18 2026 (Dom: "add them ... to my DK Live"): DRAFT SHARKS weekly projections - a free LOOK-AHEAD CHECK beside Clay.
   Reads ONLY what the free public page shows (Rankings tab, PPR): Floor / Consensus / DS / Ceiling / 3D projection for about
   250 players, for the current week and every week through 18. The full stat lines are a paid Insider feature - never read.
   Run in Chrome on https://www.draftsharks.com/weekly-rankings/<week>/ppr :  await DKD.run()  then  DKD.handoff()
   (handoff opens the GitHub upload page for yahoo_drop/draftsharks with the file in the address, like the FTN read). */
window.DKD={sl:ms=>new Promise(r=>setTimeout(r,ms)),T:x=>(x&&x.innerText||'').replace(/\s+/g,' ').trim(),
stamp(){const e=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'short',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).formatToParts(new Date).map(t=>[t.type,t.value]));return `${e.weekday} ${e.month} ${e.day} ${e.year} ${e.hour}:${e.minute} ${e.dayPeriod} PT`},
rows(){return [...document.querySelectorAll('[data-player-row]')]},
cur(){const b=document.querySelector('button.ds-dropdown__toggle');return b?+(this.T(b).match(/Week (\d+)/)||[])[1]||0:0},
async loadAll(){let n=-1;for(let i=0;i<30;i++){window.scrollTo(0,document.body.scrollHeight);await this.sl(700);const m=this.rows().length;if(m===n&&m>=200)break;n=m}window.scrollTo(0,0);return this.rows().length},
parse(){const out=[];for(const r of this.rows()){const tr=r.querySelector('tr.player-row')||r;const cells=[...tr.querySelectorAll('td')].map(td=>this.T(td));const nums=cells.map(c=>c.match(/^-?\d+(\.\d+)?$/)?+c:null);
 const tail=nums.slice(-5);if(tail.some(v=>v===null))continue;const pc=cells.find(c=>/\b(QB|RB|WR|TE|K|DEF)\d+\b/.test(c))||'';const tm=(pc.match(/\b([A-Z]{2,3})\s+(QB|RB|WR|TE|K|DEF)\d+/)||[])[1]||'';
 out.push({n:r.getAttribute('data-player-name')||'',pos:r.getAttribute('data-fantasy-position')||'',tm,floor:tail[0],cons:tail[1],ds:tail[2],ceil:tail[3],p3d:tail[4]})}return out},
async week(w){if(this.cur()===w)return true;const it=[...document.querySelectorAll('button.ds-dropdown__menu-item')].find(b=>this.T(b)===('Week '+w));if(!it)return false;const before=(this.rows()[0]&&this.T(this.rows()[0]))||'';
 document.querySelector('button.ds-dropdown__toggle').click();await this.sl(300);it.click();for(let i=0;i<40;i++){await this.sl(500);if(this.cur()===w&&this.rows().length&&this.T(this.rows()[0])!==before)break}await this.sl(1500);return this.cur()===w},
async run(){if(!/draftsharks\.com$/.test(location.host)||!/\/weekly-rankings\/\d+\/ppr/.test(location.pathname))throw new Error('run on draftsharks.com/weekly-rankings/<week>/ppr');
 const ppr=[...document.querySelectorAll('button.ds-nav-item')].find(b=>this.T(b)==='PPR');if(!ppr||!/active/.test(ppr.className))throw new Error('PPR is not selected');
 const at=this.stamp(),upd=(document.body.innerText.match(/Reviewed By[^\n|]*\|?\s*([A-Z][a-z]{2} \d+, \d{4} at [\d:]+[ap]m)/)||[])[1]||'',W0=this.cur(),weeks={},rep=[];
 for(let w=W0;w<=18;w++){if(!(await this.week(w))){rep.push('Wk'+w+' not reached');continue}const n=await this.loadAll();const P=this.parse();weeks[w]=P;rep.push('Wk'+w+' '+P.length+'/'+n)}
 await this.week(W0);this.F={'ds_weekly.json':JSON.stringify({read:at,site_updated:upd,week:W0,scoring:'PPR (Draft Sharks default)',source:'Draft Sharks weekly rankings, free public page (Rankings tab): floor/consensus/DS/ceiling/3D',weeks})};
 sessionStorage.setItem('dkd_files',JSON.stringify(this.F));return at+' | site updated '+upd+' | '+rep.join(', ')},
handoff(){const t=this.F||JSON.parse(sessionStorage.getItem('dkd_files')||'null');if(!t)throw new Error('run DKD.run() first');const e=encodeURIComponent(JSON.stringify(t));setTimeout(()=>{location.href='https://github.com/DomFantasy01/dk-feeds/upload/main/yahoo_drop/draftsharks#F='+e},300);return 'to GitHub, '+e.length+' chars'}};
