import json, h
from playwright.sync_api import sync_playwright
JS = '''async () => {
 const D = await import('/src/drills.js'); const Cn = await import('/src/content.js'); await Cn.loadContent(); const C = Cn.C;
 const taught = k => C.units.filter(u=>u.n<=k).flatMap(u=>u.letters).filter(c=>C.by[c]);
 const out={}, bad=[];
 for (const u of C.units) { if(!u.letters.length) continue;
   let wordOpts=[], nitems=[]; 
   for (let r=0;r<1000;r++) {
     const items = D.placementItems(u, taught(u.n), ()=>r%2===0);
     nitems.push(items.length);
     const L = items.filter(i=>i.kind==='letter'), Wd = items.filter(i=>i.kind==='word');
     const tg = L.map(i=>i.target).sort().join(''), want=[...u.letters.filter(c=>C.by[c])].sort().join('');
     if (tg!==want) bad.push({u:u.n,why:'letters not each once',tg,want});
     if (Wd.length!==1) bad.push({u:u.n,why:'words '+Wd.length});
     for (const it of items) {
       const rights = it.options.filter(o=>o.right).length; if (rights!==1) bad.push({u:u.n,why:'rights '+rights,kind:it.kind});
       const txt = it.options.map(o=>o.text); if (new Set(txt).size!==txt.length) bad.push({u:u.n,why:'dup options',txt});
       if (!Cn.C.audio[it.audio]) bad.push({u:u.n,why:'no audio '+it.audio});
       if (it.kind==='letter') { if (it.options.length!==Math.min(6,taught(u.n).length)) bad.push({u:u.n,why:'letter opts '+it.options.length}); 
          // same-sound options? names-based so acceptable; record count
       } else { wordOpts.push(it.options.length);
          const t = it.options.find(o=>o.right).text; }
     }
   }
   out[u.n]={items:[...new Set(nitems)], wordOpts:[...new Set(wordOpts)]};
 }
 // audio of the word item actually the target's word?
 return {out, nbad:bad.length, bad:bad.slice(0,10)};
}'''
with sync_playwright() as p:
    b, pg = h.bare(p); r = pg.evaluate(JS); print(json.dumps(r, ensure_ascii=False, indent=1)); h.save('t4_items.json', r); print(h.real_errors(pg)); b.close()
