import json, math, random, sys, time, numpy as np, cv2
import h
from trace_lib import *
from playwright.sync_api import sync_playwright
MOUNT = '''async () => { const D=await import('/src/drills.js'); const Cn=await import('/src/content.js'); await Cn.loadContent(); await document.fonts.load('170px "Noto Naskh Arabic"'); await document.fonts.load('170px "Noto Nastaliq Urdu"');
  document.body.innerHTML='<div id="tw" style="width:390px;padding:8px"></div>'; window.__rec=[]; const u=Cn.C.units[1];
  const node=D.writeIt(u,{record:(d,i,ok)=>window.__rec.push([d,i,ok])},()=>'naskh',()=>{},['ا','ب']); document.getElementById('tw').append(node); }'''
MASK = """() => { const cv=document.querySelector('canvas.trace'); const r=cv.getBoundingClientRect(); const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; const W=cv.width,H=cv.height;
  const ink=new Uint8Array(W*H); for(let i=0;i<W*H;i++) if(d[i*4+3]>20) ink[i]=1;
  const dot=document.querySelector('.trace-start'); const st=getComputedStyle(dot); const dr=dot.getBoundingClientRect();
  return {l:r.left,t:r.top,sx:r.width/W,sy:r.height/H,W,H,ink:Array.from(ink),dot:[(dr.left+dr.width/2-r.left)/(r.width/W),(dr.top+dr.height/2-r.top)/(r.height/H)], on: document.querySelector('.trace-wrap').dataset.on||''}; }"""
class Pad:
    def __init__(s, pg):
        s.pg=pg; m=pg.evaluate(MASK); s.m=m; s.W=m['W']; s.H=m['H']
        s.ink=np.array(m['ink'],dtype=np.uint8).reshape(s.H,s.W); s.dot=tuple(m['dot'])
    def sc(s,x,y): return (s.m['l']+x*s.m['sx'], s.m['t']+y*s.m['sy'])
    def drag(s, pts, wait=0):
        pg=s.pg; q=[s.sc(*p) for p in pts]; pg.mouse.move(*q[0]); pg.mouse.down()
        for i,p in enumerate(q[1:]):
            pg.mouse.move(*p)
            if wait and i%4==0: pg.wait_for_timeout(wait)
        pg.mouse.up()
    def tap(s, p): s.pg.mouse.move(*s.sc(*p)); s.pg.mouse.down(); s.pg.mouse.up()
def solve(pad):
    """natural strokes from the pixels of the real canvas: body skeleton (from the green dot), then dots"""
    m = cv2.morphologyEx(pad.ink, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
    # fill holes (outline only dotted + fill)
    lab, comps, cent = components(m)
    if not comps: return None
    body_id = comps[0][1]; body = (lab==body_id).astype(np.uint8); sk = zhang_suen(body)
    strokes = body_strokes(sk, pad.dot)
    dots = [tuple(cent[i]) for a,i in comps[1:] if a >= 60]
    dots.sort(key=lambda p:-p[0])
    return {'strokes':[thin_path(s,4) for s in strokes], 'dots':dots, 'body_area':int(comps[0][0]), 'all':[(int(a)) for a,i in comps]}
def jitter(path, sig, rnd):
    return [(x+rnd.gauss(0,sig), y+rnd.gauss(0,sig)) for x,y in path]
def variants(sol, pad, rnd):
    V = {}
    body = sol['strokes']; dots = sol['dots']
    clean = [list(s) for s in body]
    V['good'] = (clean, dots, True)
    V['good_smooth'] = ([smooth_pts(s,2) for s in clean], dots, True)
    V['shaky1.5'] = ([smooth_pts(jitter(s,1.5,rnd),1) for s in clean], dots, True)
    V['shaky3'] = ([jitter(s,3,rnd) for s in clean], dots, True)
    V['wobbly6'] = ([smooth_pts(jitter(s,6,rnd),3) for s in clean], dots, True)
    def wander(path, amp, rnd):
        ph=[rnd.uniform(0,6.28) for _ in range(3)]; wl=[rnd.uniform(50,110) for _ in range(3)]; out=[]; d=0
        for i,(x,y) in enumerate(path):
            if i: d+=math.hypot(x-path[i-1][0],y-path[i-1][1])
            dx=sum(math.sin(d/wl[k]*6.28+ph[k]) for k in range(3))/3*amp; dy=sum(math.cos(d/wl[k]*6.28+ph[k]*1.3) for k in range(3))/3*amp
            out.append((x+dx+rnd.gauss(0,1),y+dy+rnd.gauss(0,1)))
        return out
    V['wander5'] = ([wander(s,5,rnd) for s in clean], dots, True)
    V['wander9'] = ([wander(s,9,rnd) for s in clean], dots, True)
    # lift once or twice in the middle of the longest stroke
    def split(s,k):
        n=len(s); cuts=[int(n*(i+1)/(k+1)) for i in range(k)]; out=[]; a=0
        for c in cuts: out.append(s[a:c]); a=min(n-1,c+2)
        out.append(s[a:]); return [o for o in out if len(o)>1]
    big = max(range(len(clean)), key=lambda i: len(clean[i]))
    for k in (1,2):
        ss=[]; 
        for i,s in enumerate(clean): ss += split(s,k) if i==big else [s]
        V[f'lift{k}'] = (ss, dots, True)
    # start off the dot by 20 px (leader)
    off=[list(s) for s in clean]; s0=off[0][0]; lead=(s0[0]+12, s0[1]-18)
    off[0] = [lead]+[((lead[0]+(s0[0]-lead[0])*t/3),(lead[1]+(s0[1]-lead[1])*t/3)) for t in range(1,4)]+off[0]
    V['start_off20'] = (off, dots, True)
    # overshoot hook at the end
    ov=[list(s) for s in clean]; e=ov[-1][-1]; pr=ov[-1][-4] if len(ov[-1])>4 else ov[-1][0]; dx,dy=e[0]-pr[0],e[1]-pr[1]; n=math.hypot(dx,dy) or 1
    ov[-1]=ov[-1]+[(e[0]+dx/n*i*3,e[1]+dy/n*i*3) for i in range(1,6)]
    V['overshoot15'] = (ov, dots, True)
    # dots drawn as short dashes rather than taps
    V['dots_as_dashes'] = (clean, [('dash',d) for d in dots], True)
    # BAD ones
    V['bad_reversed'] = ([list(reversed(s)) for s in reversed(clean)], dots, False)
    xs=[p[0] for s in clean for p in s]; ys=[p[1] for s in clean for p in s]; cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2; w=max(xs)-min(xs); hh=max(ys)-min(ys)
    V['bad_tiny_dot'] = ([[ (pad.dot[0],pad.dot[1]) ]], [], False)
    scr=[]; 
    for i in range(60): scr.append((cx+(w/2+10)*math.sin(i*1.9)*(1 if i%2 else -1)*random.random(), cy+(hh/2+10)*math.cos(i*2.3)*random.random()))
    V['bad_scribble'] = ([scr], [], False)
    scr2=[(cx+(w/2+5)*math.sin(i*0.9+rnd.random()), cy+(hh/2+5)*math.cos(i*1.3+rnd.random())) for i in range(160)]
    V['bad_scribble_dense'] = ([scr2], [], False)
    dash=[]
    for i in range(10):
        x=min(xs)+rnd.random()*w; y=min(ys)+rnd.random()*hh; dash.append([(x,y),(x+rnd.uniform(-25,25),y+rnd.uniform(-25,25))])
    V['bad_dashes10'] = (dash, [], False)
    V['bad_dots_first'] = (([[ (d[0],d[1]), (d[0]+1,d[1]+1)] for d in dots] if dots else []) + clean, [], False if dots else True)
    V['bad_left_start'] = ([list(reversed(s)) for s in clean], dots, False)
    return V
def perform(pad, pg, strokes, dots, rnd, slow=False):
    for s in strokes:
        if len(s)==1: pad.tap(s[0])
        else: pad.drag(s, wait=8 if slow else 0)
    for d in dots:
        if isinstance(d, tuple) and d and d[0]=='dash': 
            x,y=d[1]; pad.drag([(x-4,y-3),(x,y),(x+4,y+3)])
        else: pad.tap(d)
def verdict(pg):
    pg.evaluate("document.querySelector('.btn-check').click()"); pg.wait_for_timeout(120)
    return pg.evaluate("[document.querySelector('.trace-out').textContent, document.querySelector('.trace-out').className]")
def select(pg, ch, form):
    ok = pg.evaluate("""([ch,f])=>{const lc=[...document.querySelectorAll('.tchip:not(.pchip)')].find(b=>b.querySelector('.ur')?.textContent===ch); if(lc) lc.click(); 
      const FI={isolated:0,initial:1,medial:2,final:3}; const pc=document.querySelectorAll('.pchip')[FI[f]]; if(!pc||pc.classList.contains('na')) return 'na'; pc.click(); return 'ok'}""", [ch, form])
    pg.wait_for_timeout(250); return ok
def run(letters, forms_by, seeds=(1,), outname='t6_core.json'):
    rnd = random.Random(7); res=[]
    with sync_playwright() as p:
        b, pg = h.bare(p, 420, 900); pg.evaluate(MOUNT); pg.wait_for_timeout(300)
        # make sure the pad has ALL letters selectable: remount with the right letters list
        for ch in letters:
            pg.evaluate(MOUNT.replace("['ا','ب']", json.dumps([ch,'ا' if ch!='ا' else 'ب'], ensure_ascii=False))); pg.wait_for_timeout(300)
            for form in forms_by(ch):
                if select(pg, ch, form)=='na': continue
                pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(150)
                pad = Pad(pg)
                if not pad.m['on']: res.append({'ch':ch,'form':form,'err':'pad not ready'}); continue
                sol = solve(pad)
                if not sol: res.append({'ch':ch,'form':form,'err':'no glyph'}); continue
                V = variants(sol, pad, rnd)
                import os
                ONLY=os.environ.get('ONLY'); 
                for vn,(strokes,dots,expect) in V.items():
                    if ONLY and vn not in ONLY.split(','): continue
                    pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(120)
                    try:
                        perform(pad, pg, strokes, dots, rnd, slow=(vn=='good_smooth'))
                        txt, cls = verdict(pg)
                    except Exception as e: txt, cls = 'EXC '+str(e)[:80], ''
                    ok = 'ok' in cls.split()
                    res.append({'ch':ch,'form':form,'variant':vn,'expect_ok':expect,'got_ok':ok,'msg':txt,'nstrokes':len(strokes)+len(dots),'dot':[round(pad.dot[0]),round(pad.dot[1])]})
                print(ch, form, [ (r['variant'],r['got_ok']) for r in res if r.get('ch')==ch and r.get('form')==form and r.get('got_ok')!=r.get('expect_ok')], flush=True)
        errs=h.real_errors(pg); b.close()
    json.dump({'res':res,'errors':errs}, open(h.HERE+'/'+outname,'w'), ensure_ascii=False, indent=1)
    return res
if __name__=='__main__':
    letters = sys.argv[2:] if len(sys.argv)>2 else ['ا','د','ر']
    forms_sel = sys.argv[1]
    fb = (lambda ch: ['isolated']) if forms_sel=='iso' else (lambda ch: ['isolated','initial','medial','final'])
    run(letters, fb, outname=f't6_{forms_sel}_{"".join(letters)}.json')
