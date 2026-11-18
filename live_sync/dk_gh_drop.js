/* Nov 18 2026: GitHub side of the Chrome reads' handoff. Run on https://github.com/DomFantasy01/dk-feeds/upload/main/<folder>#F=...
   (where a read's handoff() lands): it turns the files carried in the address into real files in the upload box, writes the commit
   message and presses Commit. Returns what it committed. Usage:  await DKG.drop('<commit message>') */
window.DKG={sl:ms=>new Promise(r=>setTimeout(r,ms)),
async drop(msg){if(!/github\.com$/.test(location.host)||!/\/upload\//.test(location.pathname))throw new Error('run on a github.com upload page');
 const m=location.hash.match(/^#F=(.*)$/);if(!m)throw new Error('no files in the address');const F=JSON.parse(decodeURIComponent(m[1]));
 const inp=document.querySelector('input[type=file]');if(!inp)throw new Error('no upload box');const dt=new DataTransfer();
 for(const [n,t] of Object.entries(F))dt.items.add(new File([t],n,{type:'text/plain'}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
 const names=Object.keys(F);for(let i=0;i<60;i++){await this.sl(500);const t=document.body.innerText;if(names.every(n=>t.includes(n))&&!/Uploading/i.test(t))break}
 const mi=document.querySelector('input[name=message]');if(mi){mi.value=msg||('Chrome read: '+names.join(', '));mi.dispatchEvent(new Event('input',{bubbles:true}))}
 const b=[...document.querySelectorAll('button')].find(b=>/^Commit changes$/.test(b.innerText.trim()));if(!b)throw new Error('no Commit button');
 for(let i=0;i<40&&b.disabled;i++)await this.sl(500);if(b.disabled)throw new Error('Commit button stayed disabled - upload did not finish');
 history.replaceState(null,'',location.pathname);b.click();return 'committed '+names.join(', ')+' ('+Object.values(F).map(t=>t.length).join('+')+' chars)'}};
