import json
from lib import *
FORMS=['isolated','initial','medial','final']
out=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    allch=pg.evaluate("async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.letters.letters.map(l=>[l.ch,l.joiner])}")
    for style in ('naskh','nastaliq'):
        pg.evaluate(MOUNT,[['ا','ب'],style]); pg.wait_for_timeout(300)
        for ch,joiner in allch:
            for f in FORMS:
                if not joiner and f in('initial','medial'): continue
                g= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
                # render glyph & comps with the same helper (needs trace canvas present): reuse GLYPH
                P=Pad(pg,g,style)
                body=P.comps[0]; ys,xs=np.nonzero(body['mask']); by0,by1=ys.min(),ys.max(); bcy=ys.mean()
                marks=[(m['area'],m['c'][1]) for m in P.comps[1:]]
                dot=pg.evaluate("([c,f])=>{return import('/src/content.js').then(m=>m.dotInfo(c,f))}",[ch,f])
                out.append({'style':style,'ch':ch,'form':f,'ncomp_marks':len(marks),'above':sum(1 for a,y in marks if y<by0+ (by1-by0)*0.3),'below':sum(1 for a,y in marks if y>by1-(by1-by0)*0.3),'areas':[int(a) for a,y in marks],'dot':dot})
    b.close()
json.dump(out,open('dots_truth.json','w'),ensure_ascii=False)
bad=[]
for o in out:
    d=o['dot']; exp=d['n']+(1 if d['mark'] else 0)
    if o['ncomp_marks']!=exp and o['ch'] not in 'کگ': bad.append((o['style'],o['ch'],o['form'],o['ncomp_marks'],exp,d,o['areas']))
for x in bad: print(x)
print(len(out),'cases',len(bad),'count mismatches')
