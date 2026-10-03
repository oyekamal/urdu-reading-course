import numpy as np, math, random, json, h, collections
W_, H_ = 360, 300
def zhang_suen(img):
    img = img.copy().astype(np.uint8); changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = np.pad(img, 1); p2=P[:-2,1:-1]; p3=P[:-2,2:]; p4=P[1:-1,2:]; p5=P[2:,2:]; p6=P[2:,1:-1]; p7=P[2:,:-2]; p8=P[1:-1,:-2]; p9=P[:-2,:-2]
            B = p2+p3+p4+p5+p6+p7+p8+p9
            seq = [p2,p3,p4,p5,p6,p7,p8,p9,p2]; A = sum(((seq[i]==0)&(seq[i+1]==1)).astype(np.uint8) for i in range(8))
            if step==0: c1=(p2*p4*p6)==0; c2=(p4*p6*p8)==0
            else: c1=(p2*p4*p8)==0; c2=(p2*p6*p8)==0
            m = (img==1)&(B>=2)&(B<=6)&(A==1)&c1&c2
            if m.any(): img[m]=0; changed=True
    return img
def components(mask):
    import cv2
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    comps = [(stats[i,cv2.CC_STAT_AREA], i) for i in range(1,n)]; comps.sort(reverse=True)
    return lab, comps, cent
def bfs(skel_pts, src):
    S = set(skel_pts); dist = {src:0}; par = {src:None}; q = collections.deque([src])
    while q:
        u = q.popleft()
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx==dy==0: continue
                v=(u[0]+dx,u[1]+dy)
                if v in S and v not in dist: dist[v]=dist[u]+1; par[v]=u; q.append(v)
    return dist, par
def body_strokes(skel, start, maxn=6, cover_r=9):
    pts = [(int(x),int(y)) for y,x in zip(*np.nonzero(skel))]
    if not pts: return []
    cur = start_pixel(pts, start); unc = set(pts); strokes = []
    total = len(pts)
    while len(unc) > 0.06*total and len(strokes) < maxn:
        dist, par = bfs(pts, cur)
        cand = [p for p in unc if p in dist]
        if not cand: cand = list(unc); cur = min(cand, key=lambda p: (p[0]-cur[0])**2+(p[1]-cur[1])**2); continue
        # farthest uncovered point reachable (prefer far along the path)
        tgt = max(cand, key=lambda p: dist[p])
        path = []; u = tgt
        while u is not None: path.append(u); u = par[u]
        path.reverse(); strokes.append(path)
        pset = path
        for p in list(unc):
            if any((p[0]-q[0])**2+(p[1]-q[1])**2 <= cover_r**2 for q in pset[::2]): unc.discard(p)
        cur = tgt
        if len(unc) > 0.06*total: cur = min(unc, key=lambda p: (p[0]-tgt[0])**2+(p[1]-tgt[1])**2)
    return strokes
def thin_path(path, step=4):
    out=[path[0]]; acc=0
    for a,b in zip(path,path[1:]):
        acc += math.hypot(b[0]-a[0],b[1]-a[1])
        if acc>=step: out.append(b); acc=0
    if out[-1]!=path[-1]: out.append(path[-1])
    return out
def smooth_pts(p, w=2):
    o=[]
    for i in range(len(p)):
        a=max(0,i-w); b=min(len(p)-1,i+w); xs=[q[0] for q in p[a:b+1]]; ys=[q[1] for q in p[a:b+1]]; o.append((sum(xs)/len(xs),sum(ys)/len(ys)))
    return o
def turning(p):  # same as the app (on given resampled pts)
    T=0; prev=None
    for i in range(2,len(p)):
        a=math.atan2(p[i][1]-p[i-2][1],p[i][0]-p[i-2][0])
        if prev is not None:
            d=abs(a-prev); d = 2*math.pi-d if d>math.pi else d; T+=d
        prev=a
    return T

def start_pixel(pts, dot):
    S=set(pts); d2=lambda p:(p[0]-dot[0])**2+(p[1]-dot[1])**2
    ends=[p for p in pts if sum(((p[0]+dx,p[1]+dy) in S) for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)==1]
    e=min(ends,key=d2) if ends else None
    if e is not None and d2(e)<=40**2: return e
    return min(pts,key=d2)
