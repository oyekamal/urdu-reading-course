import sys, json, math
from lib import *
style=sys.argv[1]; chs=sys.argv[2]
FORMS=['isolated','initial','medial','final']
def cl(q): return (min(357,max(3,q[0])),min(297,max(3,q[1])))
res=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    allch=pg.evaluate("async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.letters.letters.map(l=>[l.ch,l.joiner])}")
    for ch,joiner in allch:
        if ch not in chs: continue
        pg.evaluate(MOUNT,[[ch,'ا' if ch!='ا' else 'ب'],style]); pg.wait_for_timeout(300)
        for fi,f in enumerate(FORMS):
            if not joiner and f in('initial','medial'): continue
            pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(200)
            glyph= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,glyph,style)
            mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask)
            cs=cover_strokes(sk,P.dot); body=thin(max(cs,key=len),4); extra=[thin(c,4) for c in cs if c is not max(cs,key=len)]
            marks=[('tap',cl(m['c'])) for m in P.comps[1:]]
            V={'from_dot':([[cl(P.dot)]+[cl(q) for q in body]]+extra, marks),
               'from_dot_marks_first':([],[]),  # placeholder replaced below
               'body_start':([[cl(q) for q in body]]+extra, marks)}
            del V['from_dot_marks_first']
            for name,(bodies,mk) in V.items():
                P.clear(); P.refresh()
                for bd in bodies: P.drag(bd)
                for m in mk: P.tap(m[1])
                v=P.verdict(); res.append({'ch':ch,'form':f,'var':name,'ok':v['ok'],'t':v['t'],'dot':P.dot,'start':body[0]})
    b.close()
json.dump(res,open(f't1c_{style}.json','w'),ensure_ascii=False,indent=0)
for r in res:
    if not r['ok']: print(r['ch'],r['form'],r['var'],r['t'],[round(x) for x in r['dot']],[round(x) for x in r['start']])
print('n',len(res),'bad',sum(1 for r in res if not r['ok']))
