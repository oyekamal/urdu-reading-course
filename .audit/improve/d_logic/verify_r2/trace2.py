import sys, json, math, random
from lib import *
style = sys.argv[1]; only = sys.argv[2] if len(sys.argv) > 2 else None
FORMS=['isolated','initial','medial','final']
def mk_variants(P, rnd):
    sk = zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)))
    cs = cover_strokes(sk, P.dot)
    if not cs: return None
    body = max(cs,key=len); b = thin(body,4); extra=[thin(c,4) for c in cs if c is not body]; marks=P.comps[1:]
    def mk_strokes(squig=False, off=0, circles=False):
        out=[]
        for m in marks:
            if m['area']<420 or True and m['area']<420:
                c=m['c']
                if squig: out.append([(c[0]+14*math.sin(i),c[1]+9*math.cos(i*1.7)) for i in range(7)])
                elif circles: out.append([(c[0]+9*math.cos(t/6*6.28),c[1]+9*math.sin(t/6*6.28)) for t in range(8)])
                else: out.append(('tap',(c[0]+off,c[1]+off)))
            else:
                k=zs(m['mask']); w=thin(walk(k,(m['c'][0]+60,m['c'][1])),4); out.append(w)
        return out
    V={}
    V['natural']=([b]+extra, mk_strokes())
    V['marks_squiggle']=([b]+extra, mk_strokes(squig=True))
    V['marks_circles']=([b]+extra, mk_strokes(circles=True))
    V['marks_tap_off7']=([b]+extra, mk_strokes(off=7))
    n=len(b); t=n//3
    if n>12: V['lift2']=([b[:t+1],b[t:2*t+1],b[2*t:]]+extra, mk_strokes())
    if n>12: V['lift1_gap']=([b[:n//2], b[n//2+2:]]+extra, mk_strokes())
    def sm(p,w):
        o=[]
        for i in range(len(p)):
            a=max(0,i-w); c=min(len(p)-1,i+w); xs=[q[0] for q in p[a:c+1]]; ys=[q[1] for q in p[a:c+1]]; o.append((sum(xs)/len(xs),sum(ys)/len(ys)))
        return o
    def wander(path,amp):
        ph=[rnd.uniform(0,6.28) for _ in range(3)]; wl=[rnd.uniform(50,110) for _ in range(3)]; out=[]; d=0
        for i,(x,y) in enumerate(path):
            if i: d+=math.hypot(x-path[i-1][0],y-path[i-1][1])
            out.append((x+sum(math.sin(d/wl[k]*6.28+ph[k]) for k in range(3))/3*amp, y+sum(math.cos(d/wl[k]*6.28+ph[k]*1.3) for k in range(3))/3*amp))
        return out
    V['shaky3']=([sm([(x+rnd.gauss(0,3),y+rnd.gauss(0,3)) for x,y in thin(body,3)],2)]+extra, mk_strokes())
    V['wander6']=([wander(b,6)]+extra, mk_strokes())
    # start 30 px off the dot, overshoot at the end
    x0,y0=b[0]; x1,y1=b[-1]; dx,dy=x1-b[-4][0] if n>4 else 0, y1-b[-4][1] if n>4 else 0; nn=math.hypot(dx,dy) or 1
    V['offstart_overshoot']=([[(x0+20,y0-20)]+b+[(x1+dx/nn*25,y1+dy/nn*25)]]+extra, mk_strokes())
    return V
res=[]; rnd=random.Random(5)
with sync_playwright() as p:
    b, pg = browser(p)
    pg.goto(URL); pg.wait_for_timeout(1500)
    allch = pg.evaluate("async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.letters.letters.map(l=>[l.ch,l.joiner,l.family])}")
    print(len(allch),'letters',flush=True)
    for ch, joiner, fam in allch:
        if only and ch not in only: continue
        pg.evaluate(MOUNT,[[ch,'ا' if ch!='ا' else 'ب'],style]); pg.wait_for_timeout(300)
        for fi,f in enumerate(FORMS):
            if not joiner and f in('initial','medial'): continue
            pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(200)
            glyph = ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,glyph,style)
            if not P.comps: continue
            V=mk_variants(P,rnd)
            if not V: res.append({'ch':ch,'form':f,'err':'nobody'}); continue
            for name,(bodies,marks) in V.items():
                P.clear(); P.refresh()
                cl=lambda q:(min(357,max(3,q[0])),min(297,max(3,q[1])))
                for bd in bodies: P.drag([cl(q) for q in bd])
                for m in marks:
                    if isinstance(m,tuple): P.tap(cl(m[1]))
                    else: P.drag([cl(q) for q in m])
                v=P.verdict(); res.append({'ch':ch,'form':f,'var':name,'ok':v['ok'],'t':v['t'],'fam':fam,'nmarks':len(P.comps)-1})
            print(ch,f,sum(1 for r in res if r['ch']==ch and r['form']==f and not r.get('ok',True)),'bad',flush=True)
    print('errors',pg.errors[:5])
    b.close()
json.dump(res,open(f'trace2_{style}{"_"+only if only else ""}.json','w'),ensure_ascii=False,indent=0)
bad=[r for r in res if not r.get('ok')]
print('TOTAL',len(res),'BAD',len(bad))
