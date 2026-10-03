import sys, json, math, random
from lib import *
style = sys.argv[1]; only = sys.argv[2] if len(sys.argv) > 2 else None
FORMS=['isolated','initial','medial','final']
def cl(q): return (min(357,max(3,q[0])),min(297,max(3,q[1])))
def line_at(c, L, ang): 
    dx,dy=math.cos(ang)*L/2, math.sin(ang)*L/2
    return [cl((c[0]-dx+dx*2*i/6, c[1]-dy+dy*2*i/6)) for i in range(7)]
def variants(P, rnd):
    mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    sk=zs(mask); cs=cover_strokes(sk,P.dot)
    if not cs: return None,None
    body=max(cs,key=len); b=thin(body,4); extra=[thin(c,4) for c in cs if c is not body]
    wk=thin(walk(sk,P.dot),4)
    marks=P.comps[1:]
    n=len(b); t=max(2,n//3)
    # body-top start (for letters whose green dot sits on a mark)
    ys,xs=np.nonzero(mask); top=min(ys); cand=[(x,y) for x,y in zip(xs,ys) if y<=top+3]; tp=max(cand)  # rightmost of topmost
    cs2=cover_strokes(sk,tp); b2=thin(max(cs2,key=len),4) if cs2 else b; ex2=[thin(c,4) for c in cs2 if c is not max(cs2,key=len)] if cs2 else []
    def mk(kind,off=0):
        o=[]
        for i,m in enumerate(marks):
            c=m['c']
            if kind=='tap': o.append(('tap',cl((c[0]+off,c[1]+off))))
            elif kind=='tap_big': o.append(('tap',cl((c[0]+14,c[1]-6))))
            elif kind=='l30': o.append(line_at(c,30,0.0))
            elif kind=='l60d': o.append(line_at(c,60,0.8+i))
            elif kind=='l45v': o.append(line_at(c,45,1.57))
            elif kind=='sq': o.append([cl((c[0]+12*math.sin(k),c[1]+8*math.cos(k*1.7))) for k in range(7)])
            elif kind=='nat':
                if m['area']<420: o.append(('tap',cl(c)))
                else:
                    k=zs(m['mask']); o.append([cl(q) for q in thin(walk(k,(m['c'][0]+60,m['c'][1])),4)])
        return o
    def wander(path,amp,wl0=(60,120)):
        ph=[rnd.uniform(0,6.28) for _ in range(3)]; wl=[rnd.uniform(*wl0) for _ in range(3)]; out=[]; d=0
        for i,(x,y) in enumerate(path):
            if i: d+=math.hypot(x-path[i-1][0],y-path[i-1][1])
            out.append(cl((x+sum(math.sin(d/wl[k]*6.28+ph[k]) for k in range(3))/3*amp, y+sum(math.cos(d/wl[k]*6.28+ph[k]*1.3) for k in range(3))/3*amp)))
        return out
    V={}
    V['shaky3_b']=([wander(b,3)]+[wander(e,3) for e in extra], mk('nat'))
    V['shaky5_b']=([wander(b,5)]+[wander(e,5) for e in extra], mk('nat'))
    V['shaky5_b_line']=([wander(b,5)]+[wander(e,5) for e in extra], mk('l30'))
    V['lift1_nat']=([b[:n//2+1], b[n//2:]]+extra, mk('nat')) if n>12 else ([b]+extra, mk('nat'))
    # negatives
    N={}
    N={}
    return V,N
res=[]; rnd=random.Random(5)
with sync_playwright() as p:
    b, pg = browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
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
            if not P.comps: res.append({'ch':ch,'form':f,'err':'nocomps'}); continue
            V,N=variants(P,rnd)
            if not V: res.append({'ch':ch,'form':f,'err':'nobody'}); continue
            for kind,D in (('pos',V),('neg',N)):
                for name,(bodies,marks) in D.items():
                    P.clear(); P.refresh()
                    try:
                        for bd in bodies: P.drag([cl(q) for q in bd]) if len(bd)>1 else None
                        for m in marks:
                            if isinstance(m,tuple): P.tap(m[1])
                            else: P.drag(m)
                        v=P.verdict()
                    except Exception as e:
                        v={'ok':None,'t':'EXC '+str(e)[:80]}
                    res.append({'ch':ch,'form':f,'kind':kind,'var':name,'ok':v['ok'],'t':v['t'],'fam':fam,'nmarks':len(P.comps)-1})
            bad=sum(1 for r in res if r['ch']==ch and r['form']==f and r.get('kind')=='pos' and not r.get('ok'))
            fa=sum(1 for r in res if r['ch']==ch and r['form']==f and r.get('kind')=='neg' and r.get('ok'))
            print(ch,f,'falseRej',bad,'falseAcc',fa,flush=True)
    print('errors',pg.errors[:5])
    b.close()
json.dump(res,open(f't1d_{style}{"_"+only if only else ""}.json','w'),ensure_ascii=False,indent=0)
pos=[r for r in res if r.get('kind')=='pos']; neg=[r for r in res if r.get('kind')=='neg']
print('POS',len(pos),'falseRej',sum(1 for r in pos if not r['ok']),'NEG',len(neg),'falseAcc',sum(1 for r in neg if r['ok']))
