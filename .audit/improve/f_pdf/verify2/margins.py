import subprocess,glob,os,json
import numpy as np
from PIL import Image
P=os.path.expanduser('~/Documents/free_work/urdu-reading-course/mobile/public/pdf/')
res=[]
for f in sorted(glob.glob(P+'*.pdf')):
    b=os.path.basename(f)[:-4]
    subprocess.run(['pdftoppm','-r','50','-gray','-png',f,'mg/'+b])
    for p in sorted(glob.glob(f'mg/{b}-*.png')):
        a=np.array(Image.open(p).convert('L'));h,w=a.shape
        ys,xs=np.where(a<235)
        mmpp=25.4/50
        l=xs.min()*mmpp;r=(w-1-xs.max())*mmpp;t=ys.min()*mmpp;bt=(h-1-ys.max())*mmpp
        res.append((b,os.path.basename(p),round(l,1),round(r,1),round(t,1),round(bt,1),w,h))
        os.remove(p)
json.dump(res,open('margins.json','w'))
bad=[x for x in res if min(x[2:6])<9]
print(len(res),len(bad))
for x in bad[:60]: print(x)
import collections
print(sorted(set((x[6],x[7]) for x in res)))
print('min each', [min(x[i] for x in res) for i in range(2,6)])
