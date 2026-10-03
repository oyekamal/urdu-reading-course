import sys, json
from lib import *
FORMS=['isolated','initial','medial','final']
out=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    allch=pg.evaluate("async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.letters.letters.map(l=>[l.ch,l.joiner,l.family])}")
    for style in ('naskh','nastaliq'):
        for ch,joiner,fam in allch:
            pg.evaluate(MOUNT,[[ch,'ا' if ch!='ا' else 'ب'],style]); pg.wait_for_timeout(150)
            for fi,f in enumerate(FORMS):
                if not joiner and f in('initial','medial'): continue
                pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(120)
                glyph = ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
                P=Pad(pg,glyph,style)
                ys,xs=np.nonzero(P.comps[0]['mask'])
                d=np.hypot(xs-P.dot[0],ys-P.dot[1]); i=d.argmin()
                allys,allxs=np.nonzero(P.ink); da=np.hypot(allxs-P.dot[0],allys-P.dot[1])
                out.append((style,ch,fam,f,round(float(d.min())),round(float(da.min())),[round(P.dot[0]),round(P.dot[1])],[int(xs[i]),int(ys[i])]))
    b.close()
json.dump(out,open('o_dd.json','w'),ensure_ascii=False)
for o in sorted(out,key=lambda o:-o[4])[:40]: print(o)
