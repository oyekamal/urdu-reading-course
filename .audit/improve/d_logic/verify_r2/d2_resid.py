import json, math, sys
from lib import *
style=sys.argv[1]; chs=sys.argv[2]
cl=lambda q:(min(357,max(3,q[0])),min(297,max(3,q[1])))
R=[]
def loop(c,Rr,k=10): return [cl((c[0]+Rr*math.cos(t/k*6.28),c[1]+Rr*math.sin(t/k*6.28))) for t in range(k+1)]
def line(c,L,ang=0.5): return [cl((c[0]-L/2*math.cos(ang)+L*i/8*math.cos(ang),c[1]-L/2*math.sin(ang)+L*i/8*math.sin(ang))) for i in range(9)]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in chs:
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
        P=Pad(pg,ch,style); P.refresh()
        sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); cs=cover_strokes(sk,P.dot); body=[cl(q) for q in thin(max(cs,key=len),4)]; n=len(body); marks=P.comps[1:]
        def run(name,bodies,mk):
            P.clear(); P.refresh()
            for s in bodies: P.drag(s)
            for m in marks: mk(m)
            R.append((style,ch,name,P.verdict()['t']))
        for L in (20,30,45,60):
            run(f'1piece_markline{L}',[body],lambda m,L=L: P.drag(line(m['c'],L)))
        for Rr in (5,8,12):
            run(f'1piece_markloop_r{Rr}',[body],lambda m,Rr=Rr: P.drag(loop(m['c'],Rr)))
        for L in (20,30,45):
            run(f'2piece_markline{L}',[body[:n//2],body[n//2:]],lambda m,L=L: P.drag(line(m['c'],L)))
        run('2piece_tap',[body[:n//2],body[n//2:]],lambda m: P.tap(cl(m['c'])))
        run('3piece_markline30',[body[:n//3+1],body[n//3:2*n//3+1],body[2*n//3:]],lambda m: P.drag(line(m['c'],30)))
        print(style,ch,'body len',n*4,'marks',[c['area'] for c in marks],flush=True)
    b.close()
for r in R: print(*r)
json.dump(R,open(f'd2_{style}_{chs}.json','w'),ensure_ascii=False)
