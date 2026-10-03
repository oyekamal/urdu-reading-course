import sys,subprocess,glob,os
from PIL import Image
P=os.path.expanduser('~/Documents/free_work/urdu-reading-course/mobile/public/pdf/')
def sheet(b,dpi=55,cols=4,gray=False):
    for f in glob.glob(f'png/{b}-*.png'): os.remove(f)
    args=['pdftoppm','-r',str(dpi),'-png']+(['-gray'] if gray else [])+[P+b+'.pdf','png/'+b]
    subprocess.run(args)
    fs=sorted(glob.glob(f'png/{b}-*.png'));ims=[Image.open(f).convert('RGB') for f in fs]
    w,h=ims[0].size;rows=(len(ims)+cols-1)//cols
    s=Image.new('RGB',(w*cols,h*rows),'white')
    for i,im in enumerate(ims): s.paste(im,((i%cols)*w,(i//cols)*h))
    s.save(f'sheet_{b}.png');print(b,len(ims),s.size)
if __name__=='__main__':
    for b in sys.argv[3:]: sheet(b,int(sys.argv[1]),int(sys.argv[2]))
