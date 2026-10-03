import json, h
from playwright.sync_api import sync_playwright
JS = '''async () => {
 const D = await import('/src/drills.js'); const Cn = await import('/src/content.js'); await Cn.loadContent(); const C = Cn.C;
 const VOW=[['a','ا'],['i','ی'],['u','و']]; const out = {};
 const bad = [];
 for (const u of C.units) {
   const learned = C.units.filter(x=>x.n<u.n).flatMap(x=>x.letters).concat(u.letters).filter(c=>C.by[c]);
   const syl = VOW.filter(x=>learned.includes(x[1]));
   const cons = u.letters.map(c=>C.by[c]).filter(L=>L&&L.role==='consonant'&&!L.never_initial);
   const all = cons.flatMap(L=>syl.map(sy=>({L,sy})));
   if(!all.length){out[u.n]={all:0};continue;}
   const sounds = new Set(all.map(x=>Cn.soundOf(x.L.ch)+x.sy[0]));
   let min=9, rounds=0, short=0;
   for(let r=0;r<1500;r++){
     const t = all[Math.floor(Math.random()*all.length)]; const o = D.blendOptions(all,t); rounds++;
     const sn = o.map(x=>Cn.soundOf(x.L.ch)+x.sy[0]); const raw=o.map(x=>x.L.ch+x.sy[0]);
     const ts = o.filter(x=>x===t).length;
     if (new Set(sn).size!==sn.length) bad.push({u:u.n,why:'dup sound',raw});
     if (new Set(raw).size!==raw.length) bad.push({u:u.n,why:'dup tile',raw});
     if (ts!==1) bad.push({u:u.n,why:'target count '+ts,raw});
     const want = Math.min(4, sounds.size); if (o.length<want) {short++; if(short<3) bad.push({u:u.n,why:'short '+o.length+' want '+want,raw});}
     min=Math.min(min,o.length);
   }
   out[u.n]={all:all.length, sounds:sounds.size, min, rounds, short};
 }
 return {out, bad: bad.slice(0,20), nbad: bad.length};
}'''
with sync_playwright() as p:
    b, pg = h.bare(p)
    r = pg.evaluate(JS); print(json.dumps(r, ensure_ascii=False, indent=1)); h.save('t3_blend.json', r)
    print('errors', h.real_errors(pg)); b.close()
