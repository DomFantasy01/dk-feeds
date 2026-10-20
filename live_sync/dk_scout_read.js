// THE SCOUT'S YAHOO READ (Oct 10 2026; Oct 20 waiver-list fixes). Run in any Yahoo Fantasy tab of Dom's Chrome. READ-ONLY on Yahoo.
// Reads every team page in all four leagues (slot, player, NFL team, position, injury tag) and each league's waiver list,
// writes the eight files the Scout reads (dkN_rosters_live.txt, dkN_waivers.txt), then carries them to GitHub's upload
// page for yahoo_drop/scout/ inside the link. The Dispatch build copies yahoo_drop/scout/ into the Scout before it runs.
//   await DKS.run()   -> builds the files, returns a one-line summary per league
//   DKS.handoff()     -> moves the tab to GitHub's upload page carrying the files
window.DKS = {
  L: [[1,'DK I','269381',12],[2,'DK II','1519795',12],[3,'DK III','1507991',14],[4,'DK IV','864215',11]],
  SLOT: /^(QB|RB|WR|TE|W\/R\/T|Q\/W\/R\/T|K|DEF|BN|IR)$/,
  async page(u){ const r=await fetch(u,{credentials:'include'}); if(r.status!==200) return null; return new DOMParser().parseFromString(await r.text(),'text/html'); },
  stamp(){ const d=new Date(); const p=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'short',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}).formatToParts(d).map(x=>[x.type,x.value]));
    return `${p.weekday} ${p.month} ${p.day} ${p.year} ${p.hour}:${p.minute} ${p.dayPeriod} PT`; },
  async run(){
    const F={}, rep=[], at=this.stamp();
    for(const [n,lab,id,N] of this.L){
      const out=[]; let teams=0;
      for(let t=1;t<=N;t++){
        const d=await this.page(`https://football.fantasysports.yahoo.com/f1/${id}/${t}`); if(!d) continue; let k=0;
        d.querySelectorAll('table tbody tr').forEach(tr=>{
          const c=tr.querySelector('td'); if(!c) return; const slot=c.textContent.trim(); if(!this.SLOT.test(slot)) return;
          const txt=tr.textContent.replace(/\s+/g,' ');
          const a=[...tr.querySelectorAll('a')].find(x=>/\/players\/\d+/.test(x.getAttribute('href')||'')&&x.textContent.trim().length>1&&!/Note|Video/.test(x.textContent));
          let nm,cell;
          if(a){ nm=a.textContent.trim(); cell=a.closest('td').textContent.replace(/\s+/g,' '); }
          else { const m=txt.match(/([A-Za-z0-9]+)\s*(?:No new player Notes|New Player Note|Player Note)?\s*([A-Z][A-Za-z]{1,2}) - DEF/); if(!m) return; nm=m[1]; cell=txt; }   // defenses are not linked like players
          const after=cell.slice(cell.indexOf(nm)+nm.length);
          const st=(after.match(/^\s*(IR-R|PUP-R|IR|NA|SUSP|Q|D|O)(?=\s|Video|Player|No new|New|[A-Z][a-z])/)||['',''])[1];
          const tp=cell.match(/\b([A-Z][A-Za-z]{1,2}) - ([A-Z,]+)\b/);
          out.push([t,slot,nm,tp?tp[1]:'?',tp?tp[2].split(',')[0]:'?',st].join('|')); k++;
        });
        if(k) teams++;
      }
      F[`dk${n}_rosters_live.txt`]=`# ${lab} (${id}) all ${teams} rosters, Yahoo team pages read live ${at} (Chrome read). team|slot|name|team|pos|status\n`+out.join('\n')+'\n';
      const W=new Map();
      for(const pos of ['O','K','DEF']) for(const cnt of (pos==='O'?[0,25,50,75,100]:[0,25])){   // Oct 20 (Dom): top 125 offensive waiver players, not 50
        await new Promise(r=>setTimeout(r,600)); const d=await this.page(`https://football.fantasysports.yahoo.com/f1/${id}/players?status=W&pos=${pos}&cut_type=33&stat1=S_S_2026&myteam=0&sort=OR&sdir=1&count=${cnt}`); if(!d) continue;
        const tb=[...d.querySelectorAll('table')].find(x=>/Fan Pts/.test(x.textContent)); if(!tb) continue;
        tb.querySelectorAll('tbody tr').forEach(tr=>{
          const a=[...tr.querySelectorAll('a')].find(x=>/\/players\/\d+/.test(x.getAttribute('href')||'')&&x.textContent.trim().length>1&&!/Note|Video/.test(x.textContent));
          const nm=a?a.textContent.trim():(tr.textContent.replace(/\s+/g,' ').match(/([A-Za-z0-9]+)\s*(?:No new player Notes|New Player Note|Player Note)?\s*[A-Z][A-Za-z]{1,2} - DEF/)||[])[1];   // Oct 20 (Dom): GB, KC, NO, SF, TB, LV, NE, NYJ... were missed
          const m=tr.textContent.match(/W \((\w{3} \d{1,2})\)/); if(nm&&m) W.set(nm,m[1]);
        });
      }
      F[`dk${n}_waivers.txt`]=`# ${lab} waivers (Yahoo, read live ${at}, by % rostered); every unrostered TB/DAL player also on waivers until Oct 14\n`+[...W].map(([a,b])=>a+'/'+b).join('|')+'\n';
      rep.push(`${lab}: ${teams} teams, ${out.length} players, ${W.size} on waivers`);
    }
    sessionStorage.setItem('dks_files',JSON.stringify(F)); this.F=F; return at+' | '+rep.join(' | ');
  },
  handoff(){ const F=this.F||JSON.parse(sessionStorage.getItem('dks_files')||'null'); if(!F) throw new Error('run DKS.run() first');
    const enc=encodeURIComponent(JSON.stringify(F)); setTimeout(()=>{location.href='https://github.com/DomFantasy01/dk-feeds/upload/main/yahoo_drop/scout#F='+enc;},300); return 'to GitHub, '+enc.length+' chars'; }
};
'DKS loaded';
