s=open('trace_all.py').read()
a=s.index("    V['shaky3']"); b=s.index("    # start 30 px off")
new='''    def sm(p,w):
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
    V['shaky3']=([sm([(x+rnd.gauss(0,3),y+rnd.gauss(0,3)) for x,y in thin(body,3)],2)], mk_strokes())
    V['wander6']=([wander(b,6)], mk_strokes())
'''
open('trace_all.py','w').write(s[:a]+new+s[b:])
