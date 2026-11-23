/* Nov 18 2026: GitHub side of the Chrome reads' handoff. Run on https://github.com/DomFantasy01/dk-feeds/upload/main/<folder>?t=..#F=...
   (where a read's handoff() lands): it turns the files carried in the address into real files in the upload box, writes the commit
   message and commits. Usage:  await DKG.drop('<commit message>')
   Nov 23 2026 (Dom: "Fix." - the 8:12 AM Yahoo projections save died on GitHub "HTTP ERROR 400"). Cause found: when the upload page
   is not freshly loaded (only the #F= part of the address changed, so Chrome keeps the old page), GitHub's upload slot is already
   used and every commit gets 400. Now: (1) every read's handoff adds ?t=<time> so the upload page always loads fresh; (2) the
   commit is sent from inside the page and checked against GitHub's own commit list (never saved twice); (3) if GitHub still refuses,
   the files are kept in this tab, a fresh upload page is loaded, and the answer says
   "NOT SAVED YET - fresh page loading: run dk_gh_drop.js again and await DKG.drop()" - doing that finishes the save (3 tries max). */
window.DKG={log:[],sl:ms=>new Promise(r=>setTimeout(r,ms)),K:'dkg_pending',
async landed(folder,msg,since){try{const r=await fetch('https://api.github.com/repos/DomFantasy01/dk-feeds/commits?per_page=5&path='+encodeURIComponent(folder)+'&since='+since,{cache:'no-store'});if(!r.ok)return null;const j=await r.json();return j.some(c=>(c.commit&&c.commit.message||'').split('\n')[0]===msg)}catch(e){return null}},
async drop(msg){if(!/github\.com$/.test(location.host)||!/\/upload\//.test(location.pathname))throw new Error('run on a github.com upload page');
 const folder=decodeURIComponent(location.pathname.replace(/^.*\/upload\/main\/?/,''))||'.';
 let P=null;try{P=JSON.parse(sessionStorage.getItem(this.K)||'null')}catch(e){}
 const m=location.hash.match(/^#F=(.*)$/);
 if(m)P={F:JSON.parse(decodeURIComponent(m[1])),msg:null,tries:0,errs:[],since:new Date(Date.now()-120e3).toISOString(),folder};
 else if(!P||P.folder!==folder)throw new Error('no files in the address');
 if(window.__dkgUsed)throw new Error('this upload page was already used - load it fresh (add ?t=<time> to the address) and run again');
 const F=P.F;msg=P.msg||msg||('Chrome read: '+Object.keys(F).join(', '));P.msg=msg;
 const names=Object.keys(F),sizes=names.join(', ')+' ('+Object.values(F).map(t=>t.length).join('+')+' chars)',tree='https://github.com/DomFantasy01/dk-feeds/tree/main/'+folder;
 const done=(how)=>{sessionStorage.removeItem(this.K);setTimeout(()=>{location.href=tree},300);return 'committed '+sizes+' - '+how+(P.errs.length?' (earlier: '+P.errs.join(', ')+')':'')};
 if(P.tries>0&&await this.landed(folder,msg,P.since))return done('it had landed after all');
 sessionStorage.setItem(this.K,JSON.stringify(P));history.replaceState(null,'',location.pathname);
 const inp=document.querySelector('input[type=file]');if(!inp)throw new Error('no upload box');const dt=new DataTransfer();
 for(const [n,t] of Object.entries(F))dt.items.add(new File([t],n,{type:'text/plain'}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
 for(let i=0;i<60;i++){await this.sl(500);const t=document.body.innerText;if(names.every(n=>t.includes(n)))break}
 const mi=document.querySelector('input[name=message]');if(mi){mi.value=msg;mi.dispatchEvent(new Event('input',{bubbles:true}))}
 const b=[...document.querySelectorAll('button')].find(b=>/^Commit changes$/.test(b.innerText.trim()));if(!b)throw new Error('no Commit button');
 await this.sl(1500);for(let i=0;i<60&&b.disabled;i++)await this.sl(500);if(b.disabled)throw new Error('Commit button stayed disabled - upload did not finish');
 const form=b.closest('form');window.__dkgUsed=true;
 if(!form){sessionStorage.removeItem(this.K);b.click();return 'committed '+sizes+' (clicked; no form to check)'}
 let st='';try{const fd=new FormData(form);if(b.name)fd.append(b.name,b.value||'');
  const r=await fetch(form.action,{method:'POST',body:fd,credentials:'same-origin',redirect:'follow'});st='HTTP '+r.status;this.log.push('try '+(P.tries+1)+' '+st);
  if(r.ok){for(let i=0;i<10;i++){await this.sl(2500);const d=await this.landed(folder,msg,P.since);if(d===true)return done('checked on GitHub');if(d===null)return done('GitHub said OK (commit list not reachable to double-check)')}st+=' but no commit showed up'}
 }catch(e){st='network '+e.message}
 await this.sl(3000);if(await this.landed(folder,msg,P.since))return done('checked on GitHub');
 P.tries++;P.errs.push('try '+P.tries+': '+st);
 if(P.tries>=3){sessionStorage.removeItem(this.K);throw new Error('GitHub commit failed 3 times - '+P.errs.join(' | '))}
 sessionStorage.setItem(this.K,JSON.stringify(P));setTimeout(()=>{location.href=location.origin+location.pathname+'?t='+Date.now()},300);
 return 'NOT SAVED YET - GitHub answered '+st+'. A fresh upload page is loading: wait ~3 s, run dk_gh_drop.js again and await DKG.drop() to finish (try '+(P.tries+1)+' of 3).'}};
