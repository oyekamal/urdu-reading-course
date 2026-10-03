import json, math, random, sys, os, numpy as np, cv2
import h
from trace_lib import *
from t6_trace import MOUNT, Pad, select, verdict, MASK
from playwright.sync_api import sync_playwright
NEXP = "([ch,f])=>import('/src/content.js').then(m=>{const d=m.dotInfo(ch,f);return d.n+(d.mark?1:0)})"
def walk_cover(skel, start):
    """one continuous stroke over the whole skeleton (retracing allowed), starting at the endpoint nearest the dot"""
    pts=[(int(x),int(y)) for y,x in zip(*np.nonzero(skel))]
    if not pts: return []
    S=set(pts); nb=lambda p:[(p[0]+dx,p[1]+dy) for dx in (-1,0,1) for dy in (-1,0,1) if (dx or dy) and (p[0]+dx,p[1]+dy) in S]
    cur=start_pixel(pts,start)
    seen={cur}; path=[cur]; unc=set(pts)-{cur}
    def bfs_to_unc(src):
        dist={src:0};par={src:None};q=collections.deque([src])
        while q:
            u=q.popleft()
            if u in unc and u!=src: 
                r=[];x=u
                while x is not None: r.append(x); x=par[x]
                return r[::-1]
            for v in nb(u):
                if v not in dist: dist[v]=dist[u]+1; par[v]=u; q.append(v)
        return None
    while unc and len(path)<20000:
        # prefer an unvisited neighbour straight ahead, else shortest path to nearest uncovered pixel (retrace)
        r=bfs_to_unc(path[-1])
        if not r: break
        for p in r[1:]: path.append(p); unc.discard(p)
    # cut after the last newly covered pixel is implicit
    return path
def marks_of(pad, sol_lab_comps, cent, lab, nexp):
    out=[]; comps=sol_lab_comps[1:]
    items=[]
    for a,i in comps:
        if a<40: continue
        ys,xs=np.nonzero(lab==i); items.append((a,i,np.column_stack([xs,ys]).astype(np.float32)))
    # split merged dot clusters
    if items and nexp>len(items):
        items.sort(key=lambda t:-t[0]); a,i,P=items[0]; k=nexp-len(items)+1
        _,labels,centers=cv2.kmeans(P,k,None,(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,50,0.5),5,cv2.KMEANS_PP_CENTERS)
        items=items[1:]+[(a//k,-1,P[labels.ravel()==j]) for j in range(k)]
    for a,i,P in items:
        c=P.mean(axis=0); u,s,vt=np.linalg.svd(P-c,full_matrices=False); ext=(P-c)@vt[0]; L=ext.max()-ext.min()
        if L>26: 
            d=vt[0]; p0=c+d*(ext.min()+4); p1=c+d*(ext.max()-4); out.append(('drag',[(float(q[0]),float(q[1])) for q in (p0,c,p1)]))
        else: out.append(('tap',(float(c[0]),float(c[1]))))
    out.sort(key=lambda m:-(m[1][0] if m[0]=='tap' else m[1][1][0]))
    return out
def solve2(pad, nexp):
    m=cv2.morphologyEx(pad.ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); lab,comps,cent=components(m)
    if not comps: return None
    body=(lab==comps[0][1]).astype(np.uint8); sk=zhang_suen(body)
    single=walk_cover(sk,pad.dot); multi=body_strokes(sk,pad.dot)
    return {'single':thin_path(single,4),'multi':[thin_path(s,4) for s in multi],'marks':marks_of(pad,comps,cent,lab,nexp),'ncomps':[c[0] for c in comps]}
def do_marks(pad, marks):
    mode=os.environ.get('DOTMODE','tap')
    for k,v in marks:
        if k=='tap':
            if mode=='tap': pad.tap(v)
            else: x,y=v; pad.drag([(x-4,y-3),(x,y),(x+4,y+3)])
        else: pad.drag(v)
def jitter(path,sig,rnd): return [(x+rnd.gauss(0,sig),y+rnd.gauss(0,sig)) for x,y in path]
def wander(path, amp, rnd):
    ph=[rnd.uniform(0,6.28) for _ in range(3)]; wl=[rnd.uniform(50,110) for _ in range(3)]; out=[]; d=0
    for i,(x,y) in enumerate(path):
        if i: d+=math.hypot(x-path[i-1][0],y-path[i-1][1])
        dx=sum(math.sin(d/wl[k]*6.28+ph[k]) for k in range(3))/3*amp; dy=sum(math.cos(d/wl[k]*6.28+ph[k]*1.3) for k in range(3))/3*amp
        out.append((x+dx+rnd.gauss(0,1),y+dy+rnd.gauss(0,1)))
    return out
def split(s,k):
    n=len(s); cuts=[int(n*(i+1)/(k+1)) for i in range(k)]; out=[]; a=0
    for c in cuts: out.append(s[a:c]); a=min(n-1,c+2)
    out.append(s[a:]); return [o for o in out if len(o)>1]
def variants2(sol,pad,rnd):
    S=sol['single']; V={}
    V['single_good']=([S],True)
    V['single_smooth_slow']=([smooth_pts(S,2)],True)
    V['single_shaky1.5']=([smooth_pts(jitter(S,1.5,rnd),1)],True)
    V['single_shaky3']=([jitter(S,3,rnd)],True)
    V['single_wander5']=([wander(S,5,rnd)],True)
    V['single_wander9']=([wander(S,9,rnd)],True)
    V['single_lift1']=(split(S,1),True)
    V['single_lift2']=(split(S,2),True)
    s0=S[0]; lead=(s0[0]+12,s0[1]-18); off=[lead]+[(lead[0]+(s0[0]-lead[0])*t/3,lead[1]+(s0[1]-lead[1])*t/3) for t in range(1,4)]+S
    V['single_start_off20']=([off],True)
    e=S[-1]; pr=S[-4] if len(S)>4 else S[0]; dx,dy=e[0]-pr[0],e[1]-pr[1]; n=math.hypot(dx,dy) or 1
    V['single_overshoot15']=([S+[(e[0]+dx/n*i*3,e[1]+dy/n*i*3) for i in range(1,6)]],True)
    V['multi_good']=(sol['multi'],True)
    V['multi_wander5']=([wander(m,5,rnd) for m in sol['multi']],True)
    V['multi_wander9']=([wander(m,9,rnd) for m in sol['multi']],True)
    V['multi_shaky1.5']=([smooth_pts(jitter(m,1.5,rnd),1) for m in sol['multi']],True)
    V['multi_shaky3']=([jitter(m,3,rnd) for m in sol['multi']],True)
    V['multi_startdot']=([[tuple(pad.dot)]+sol['multi'][0]]+sol['multi'][1:],True)
    V['multi_lift2']=([x for i,m in enumerate(sol['multi']) for x in (split(m,2) if i==0 else [m])],True)
    M=sol['multi']; V['bad_reversed']=([list(reversed(M[0]))] if len(M)==1 else [list(reversed(m)) for m in reversed(M)],False)
    V['reversed_with_marks']=(V['bad_reversed'][0],False)
    xs=[p[0] for p in S]; ys=[p[1] for p in S]; cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2; w=max(xs)-min(xs)+20; hh=max(ys)-min(ys)+20
    V['bad_tiny_dot']=([[tuple(pad.dot)]],False)
    V['bad_scribble']=([[(cx+w/2*math.sin(i*1.9)*rnd.random()*(1 if i%2 else -1), cy+hh/2*math.cos(i*2.3)*rnd.random()) for i in range(60)]],False)
    V['bad_dashes10']=([[(x,y),(x+rnd.uniform(-25,25),y+rnd.uniform(-25,25))] for x,y in [(min(xs)+rnd.random()*w,min(ys)+rnd.random()*hh) for _ in range(10)]],False)
    V['bad_zigzag_fill']=([[ (min(xs)-5+ (i%2)*(w+10), min(ys)-5 + i*(hh+10)/24) for i in range(25)]],False)
    return V
def run(letters, forms_by, outname, only=None, style='naskh'):
    rnd=random.Random(11); res=[]
    with sync_playwright() as p:
        b,pg=h.bare(p,420,900)
        for ch in letters:
            pg.evaluate(MOUNT.replace("['ا','ب']",json.dumps([ch,'ا' if ch!='ا' else 'ب'],ensure_ascii=False)).replace("()=>'naskh'",f"()=>'{style}'")); pg.wait_for_timeout(300)
            for form in forms_by(ch):
                if select(pg,ch,form)=='na': continue
                pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(150)
                pad=Pad(pg)
                if not pad.m['on']: res.append({'ch':ch,'form':form,'err':'pad not ready'}); continue
                nexp=pg.evaluate(NEXP,[ch,form]); sol=solve2(pad,nexp)
                if not sol: continue
                V=variants2(sol,pad,rnd)
                for vn,(strokes,expect) in V.items():
                    if only and vn not in only: continue
                    pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(100)
                    try:
                        for s in strokes:
                            if len(s)==1: pad.tap(s[0])
                            else: pad.drag(s, wait=6 if 'slow' in vn else 0)
                        if not vn.startswith('bad_') or vn=='reversed_with_marks': do_marks(pad, sol['marks'])
                        txt,cls=verdict(pg)
                    except Exception as e: txt,cls='EXC '+str(e)[:80],''
                    res.append({'ch':ch,'form':form,'variant':vn,'expect_ok':expect,'got_ok':'ok' in cls.split(),'msg':txt,'nbody':len(strokes),'nmarks':len(sol['marks']),'nexp':nexp})
                print(ch,form,[(r['variant'],r['got_ok']) for r in res if r.get('ch')==ch and r.get('form')==form and r.get('got_ok')!=r.get('expect_ok')],flush=True)
        errs=h.real_errors(pg); b.close()
    json.dump({'res':res,'errors':errs},open(h.HERE+'/'+outname,'w'),ensure_ascii=False,indent=1)
if __name__=='__main__':
    mode=sys.argv[1]; letters=sys.argv[2:]
    fb=(lambda ch:['isolated']) if mode=='iso' else (lambda ch:['isolated','initial','medial','final'])
    only=os.environ.get('ONLY'); only=only.split(',') if only else None
    run(letters,fb,f't6b_{mode}_{"".join(letters)[:8]}{os.environ.get("TAG","")}.json',only,os.environ.get('STYLE','naskh'))
