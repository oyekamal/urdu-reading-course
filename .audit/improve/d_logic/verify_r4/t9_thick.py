import sys, json, math, random
from lib import *
style = sys.argv[1]; only = sys.argv[2]
FORMS=['isolated','initial','medial','final']
def cl(q): return (min(357,max(3,q[0])),min(297,max(3,q[1])))
rnd=random.Random(11)
def offset_path(path, off):  # constant perpendicular offset
    out=[]
    for i,(x,y) in enumerate(path):
        a=path[max(0,i-1)]; b=path[min(len(path)-1,i+1)]; dx,dy=b[0]-a[0],b[1]-a[1]; n=math.hypot(dx,dy) or 1
        out.append(cl((x+off*(-dy)/n, y+off*dx/n)))
    return out
def wander(path,amp):
    ph=[rnd.uniform(0,6.28) for _ in range(3)]; wl=[rnd.uniform(40,90) for _ in range(3)]; out=[]; d=0
    for i,(x,y) in enumerate(path):
        if i: d+=math.hypot(x-path[i-1][0],y-path[i-1][1])
        out.append(cl((x+sum(math.sin(d/wl[k]*6.28+ph[k]) for k in range(3))/3*amp, y+sum(math.cos(d/wl[k]*6.28+ph[k]*1.3) for k in range(3))/3*amp)))
    return out
res=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    allch=pg.evaluate("async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.letters.letters.map(l=>[l.ch,l.joiner,l.family])}")
    for ch,joiner,fam in allch:
        if ch not in only: continue
        pg.evaluate(MOUNT,[[ch,'ا' if ch!='ا' else 'ب'],style]); pg.wait_for_timeout(300)
        for fi,f in enumerate(FORMS):
            if not joiner and f in('initial','medial'): continue
            pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(200)
            glyph = ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,glyph,style)
            mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask); cs=cover_strokes(sk,P.dot)
            if not cs: continue
            body=max(cs,key=len); bt=thin(body,4); extra=[thin(c,4) for c in cs if c is not body]
            ys,xs=np.nonzero(mask); top=min(ys); tp=max([(x,y) for x,y in zip(xs,ys) if y<=top+3])
            cs2=cover_strokes(sk,tp); b2=thin(max(cs2,key=len),4) if cs2 else bt; ex2=[thin(c,4) for c in cs2 if c is not max(cs2,key=len)] if cs2 else []
            marks=[('tap',cl(m['c'])) for m in P.comps[1:]]
            V={'center':([bt]+extra,marks),'center_bodytop':([b2]+ex2,marks),
               'off+6':([offset_path(bt,6)]+[offset_path(e,6) for e in extra],marks),'off-6':([offset_path(bt,-6)]+[offset_path(e,-6) for e in extra],marks),
               'wob9':([wander(bt,9)]+[wander(e,9) for e in extra],marks),'wob9_bodytop':([wander(b2,9)]+[wander(e,9) for e in ex2],marks)}
            for name,(bodies,mk) in V.items():
                P.clear(); P.refresh()
                try:
                    for bd in bodies:
                        if len(bd)>1: P.drag(bd)
                    for m in mk: P.tap(m[1])
                    v=P.verdict()
                except Exception as e: v={'ok':None,'t':'EXC '+str(e)[:80]}
                res.append({'ch':ch,'form':f,'var':name,'ok':v['ok'],'t':v['t']})
    print('errors',pg.errors[:5]); b.close()
json.dump(res,open(f'o_t9_{style}_{only}.json','w'),ensure_ascii=False)
bad=[r for r in res if not r['ok']]
print('N',len(res),'rej',len(bad)); [print(r['ch'],r['form'],r['var'],r['t']) for r in bad]
