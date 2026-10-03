import json
from lib import *
JS='''async()=>{const D=await import('/src/drills.js');const Cn=await import('/src/content.js');await Cn.loadContent();const C=Cn.C; const out={};
 for(const u of C.units){ const learned=C.units.filter(x=>x.n<u.n).flatMap(x=>x.letters).concat(u.letters).filter(c=>C.by[c]);
  const cons=u.letters.map(c=>C.by[c]).filter(L=>L&&L.role==='consonant'&&!L.never_initial); const syl=[['a','ا'],['i','ی'],['u','و']].filter(x=>learned.includes(x[1]));
  const all=cons.flatMap(L=>syl.map(sy=>({L,sy}))); if(!all.length){out[u.n]={none:true};continue}
  let bad=0,minOpt=9,maxOpt=0,noTarget=0,dupText=0,SAME=Cn.soundOf; const cnt={};
  for(let t=0;t<1000;t++){ const target=all[Math.floor(Math.random()*all.length)]; const o=D.blendOptions(all,target); minOpt=Math.min(minOpt,o.length); maxOpt=Math.max(maxOpt,o.length);
    if(o.filter(x=>x===target).length!==1) noTarget++; const snds=o.map(x=>Cn.soundOf(x.L.ch)+x.sy[0]); if(new Set(snds).size!==snds.length) bad++; const tx=o.map(x=>x.L.ch+x.sy[1]); if(new Set(tx).size!==tx.length) dupText++;
    // independent same-sound check with my own table
    const fam={'ض':'z','ظ':'z','ذ':'z','ز':'z','ث':'s','س':'s','ص':'s','ت':'t','ط':'t','ح':'h','ہ':'h','ع':'a','ا':'a'}; const f=o.map(x=>(fam[x.L.ch]||x.L.ch)+x.sy[0]); if(new Set(f).size!==f.length) bad+=1000;
  }
  out[u.n]={cons:cons.map(l=>l.ch).join(''),nAll:all.length,bad,minOpt,maxOpt,noTarget,dupText};
 } return out}'''
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500); r=pg.evaluate(JS); b.close()
for k,v in r.items(): print(k,v)
