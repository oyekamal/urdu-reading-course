# ground truth for glyph marks, from pixels (Naskh), independent of dotInfo
import json, h
from playwright.sync_api import sync_playwright
JS = '''async () => {
 const Cn = await import('/src/content.js'); await Cn.loadContent(); const C = Cn.C;
 await document.fonts.load('60px "Noto Naskh Arabic"'); await document.fonts.load('60px "Noto Nastaliq Urdu"');
 const W=300, cv=document.createElement('canvas'); cv.width=W; cv.height=W; const g=cv.getContext('2d',{willReadFrequently:true});
 function blobs(fam,text){ g.clearRect(0,0,W,W); g.fillStyle='#000'; g.font='140px '+fam; g.direction='rtl'; g.textAlign='center'; g.textBaseline='alphabetic'; g.fillText(text,150,170);
   const d=g.getImageData(0,0,W,W).data, lab=new Int32Array(W*W), res=[]; let id=0; const st=[];
   for(let i=0;i<W*W;i++){ if(d[i*4+3]<100||lab[i]) continue; id++; let n=0,sx=0,sy=0,x0=W,x1=0,y0=W,y1=0; st.push(i); lab[i]=id;
     while(st.length){ const q=st.pop(); n++; const x=q%W,y=(q/W)|0; sx+=x; sy+=y; if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y;
       for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy; if(nx<0||ny<0||nx>=W||ny>=W)continue; const k=ny*W+nx; if(!lab[k]&&d[k*4+3]>=100){lab[k]=id;st.push(k);} } }
     res.push({n,cx:sx/n,cy:sy/n,x0,x1,y0,y1}); }
   return res; }
 const out=[]; for(const l of C.letters.letters) for(const [form,glyph] of Cn.forms(l)){ if(!glyph) continue;
   out.push({ch:l.ch,form,naskh:blobs('"Noto Naskh Arabic"',glyph),nast:blobs('"Noto Nastaliq Urdu"',glyph)}); }
 return out; }'''
with sync_playwright() as p:
    b, pg = h.bare(p); r = pg.evaluate(JS); h.save('t1_blobs.json', r); print(len(r), 'glyphs'); b.close()
