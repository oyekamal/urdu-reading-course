import os, json, math, random, collections, numpy as np, cv2
from playwright.sync_api import sync_playwright
PORT = os.environ.get('PORT', '5490')
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
HERE = os.path.dirname(os.path.abspath(__file__))
URL = f'http://localhost:{PORT}/?skiponb'
def browser(p, w=420, h=1000):
    b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': w, 'height': h}); pg = ctx.new_page()
    pg.errors = []; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept())
    return b, pg
def zs(img):
    img = img.copy().astype(np.uint8); ch = True
    while ch:
        ch = False
        for step in (0, 1):
            P = np.pad(img, 1); p2=P[:-2,1:-1];p3=P[:-2,2:];p4=P[1:-1,2:];p5=P[2:,2:];p6=P[2:,1:-1];p7=P[2:,:-2];p8=P[1:-1,:-2];p9=P[:-2,:-2]
            B = p2+p3+p4+p5+p6+p7+p8+p9; seq=[p2,p3,p4,p5,p6,p7,p8,p9,p2]; A=sum(((seq[i]==0)&(seq[i+1]==1)).astype(np.uint8) for i in range(8))
            c1,c2 = ((p2*p4*p6)==0,(p4*p6*p8)==0) if step==0 else ((p2*p4*p8)==0,(p2*p6*p8)==0)
            m=(img==1)&(B>=2)&(B<=6)&(A==1)&c1&c2
            if m.any(): img[m]=0; ch=True
    return img
def walk(skel, start):
    """one continuous child-like stroke: start at skeleton pixel nearest `start`, then keep going to the nearest unvisited skeleton pixel (walking along the skeleton)."""
    pts = [(int(x),int(y)) for y,x in zip(*np.nonzero(skel))]
    if not pts: return []
    S=set(pts); nb=lambda u:[(u[0]+dx,u[1]+dy) for dx in(-1,0,1) for dy in(-1,0,1) if (dx or dy) and (u[0]+dx,u[1]+dy) in S]
    ends=[p for p in pts if len(nb(p))==1]
    d2=lambda p,q:(p[0]-q[0])**2+(p[1]-q[1])**2
    cand = ends or pts
    cur=min(cand,key=lambda p:d2(p,start))
    if d2(cur,start)>60**2: cur=min(pts,key=lambda p:d2(p,start))
    path=[cur]; unv=set(pts); unv.discard(cur)
    # cover radius: pixels within 3px of the path are visited
    while unv:
        # BFS to nearest unvisited
        prev={cur:None}; q=collections.deque([cur]); tgt=None
        while q:
            u=q.popleft()
            if u in unv and u!=cur: tgt=u; break
            for v in nb(u):
                if v not in prev: prev[v]=u; q.append(v)
        if tgt is None: break
        seg=[]; u=tgt
        while u!=cur: seg.append(u); u=prev[u]
        seg.reverse(); path+=seg
        for s in seg:
            for dx in range(-2,3):
                for dy in range(-2,3): unv.discard((s[0]+dx,s[1]+dy))
        cur=tgt
    return path
def thin(path, step=4):
    out=[path[0]]; acc=0
    for a,b in zip(path,path[1:]):
        acc+=math.hypot(b[0]-a[0],b[1]-a[1])
        if acc>=step: out.append(b); acc=0
    if out[-1]!=path[-1]: out.append(path[-1])
    return out
MOUNT = '''async ([chs, style]) => { const D=await import('/src/drills.js'); const Cn=await import('/src/content.js'); await Cn.loadContent();
  await document.fonts.load('170px "Noto Naskh Arabic"'); await document.fonts.load('170px "Noto Nastaliq Urdu"');
  document.body.innerHTML='<div id="tw" style="width:390px;padding:8px"></div>'; window.__rec=[]; const u=Cn.C.units[1];
  const node=D.writeIt(u,{record:(d,i,ok)=>window.__rec.push([d,i,ok])},()=>style,()=>{},chs); document.getElementById('tw').append(node); }'''
GLYPH = '''([g, style]) => { const c=document.createElement('canvas'); c.width=360;c.height=300; const x=c.getContext('2d',{willReadFrequently:true}); const fam= style==='nastaliq'?'"Noto Nastaliq Urdu"':'"Noto Naskh Arabic"';
  x.fillStyle='#ccc'; x.font='170px '+fam; x.textAlign='center'; x.textBaseline='middle'; x.direction='rtl'; x.fillText(g,180,150);
  const d=x.getImageData(0,0,360,300).data; const a=[]; for(let i=0;i<360*300;i++) a.push(d[i*4+3]>40?1:0);
  const cv=document.querySelector('canvas.trace'); const r=cv.getBoundingClientRect(); const dot=document.querySelector('.trace-start'); const dr=dot.getBoundingClientRect();
  return {ink:a,l:r.left,t:r.top,sx:r.width/360,sy:r.height/300,dot:[(dr.left+dr.width/2-r.left)/(r.width/360),(dr.top+dr.height/2-r.top)/(r.height/300)],on:document.querySelector('.trace-wrap').dataset.on||''}; }'''
class Pad:
    def __init__(s, pg, g, style):
        s.pg=pg; m=pg.evaluate(GLYPH,[g,style]); s.m=m; s.on=m['on']
        s.ink=np.array(m['ink'],dtype=np.uint8).reshape(300,360); s.dot=tuple(m['dot'])
        k=cv2.morphologyEx(s.ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); n,lab,stats,cent=cv2.connectedComponentsWithStats(k,connectivity=8)
        comps=sorted([(stats[i,cv2.CC_STAT_AREA],i) for i in range(1,n)],reverse=True); s.comps=[]
        for a,i in comps: s.comps.append({'area':int(a),'mask':(lab==i).astype(np.uint8),'c':tuple(cent[i])})
    def refresh(s):
        r=s.pg.evaluate("()=>{const cv=document.querySelector('canvas.trace'); cv.scrollIntoView({block:'center'}); const r=cv.getBoundingClientRect(); return [r.left,r.top,r.width/360,r.height/300]}")
        s.m['l'],s.m['t'],s.m['sx'],s.m['sy']=r
    def sc(s,x,y): return (s.m['l']+x*s.m['sx'], s.m['t']+y*s.m['sy'])
    def drag(s, pts):
        pg=s.pg; q=[s.sc(*p) for p in pts]; pg.mouse.move(*q[0]); pg.mouse.down()
        for p in q[1:]: pg.mouse.move(*p)
        pg.mouse.up()
    def tap(s,p): s.pg.mouse.move(*s.sc(*p)); s.pg.mouse.down(); s.pg.mouse.up()
    def verdict(s):
        s.pg.click('.btn-check'); s.pg.wait_for_timeout(30)
        return s.pg.evaluate("()=>{const o=document.querySelector('.trace-out');return {t:o.textContent,ok:o.classList.contains('ok')}}")
    def clear(s): s.pg.click('.trace-clear'); s.pg.wait_for_timeout(30)

def cover_strokes(skel, start, maxn=5, r=9):
    """child-like: the longest smooth path from the start end, then further strokes for uncovered branches (lifted pen)."""
    pts=[(int(x),int(y)) for y,x in zip(*np.nonzero(skel))]
    if not pts: return []
    S=set(pts); nb=lambda u:[(u[0]+dx,u[1]+dy) for dx in(-1,0,1) for dy in(-1,0,1) if (dx or dy) and (u[0]+dx,u[1]+dy) in S]
    d2=lambda p,q:(p[0]-q[0])**2+(p[1]-q[1])**2
    ends=[p for p in pts if len(nb(p))==1]
    cur=min(ends or pts,key=lambda p:d2(p,start))
    if d2(cur,start)>60**2: cur=min(pts,key=lambda p:d2(p,start))
    unc=set(pts); strokes=[]
    def bfs(src):
        prev={src:None}; dist={src:0}; q=collections.deque([src])
        while q:
            u=q.popleft()
            for v in nb(u):
                if v not in prev: prev[v]=u; dist[v]=dist[u]+1; q.append(v)
        return prev,dist
    while len(unc)>0.05*len(pts) and len(strokes)<maxn:
        prev,dist=bfs(cur); cand=[p for p in unc if p in dist]
        if not cand: cur=min(unc,key=lambda p:d2(p,cur)); continue
        tgt=max(cand,key=lambda p:dist[p]); path=[]; u=tgt
        while u is not None: path.append(u); u=prev[u]
        path.reverse(); strokes.append(path)
        for q in list(unc):
            if any(d2(q,s)<=r*r for s in path[::2]): unc.discard(q)
        if unc: cur=min(unc,key=lambda p:d2(p,tgt))
    return strokes
