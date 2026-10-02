import glob,os,sys
from PIL import Image, ImageDraw
for run in sorted(glob.glob('runs/*')):
    tag=os.path.basename(run); fs=sorted(glob.glob(run+'/shots/*.jpg'))
    ims=[Image.open(f) for f in fs]; w,h=ims[0].size
    th=360 if h>=500 else 240; sc=th/h; tw=int(w*sc)
    cols=max(4,min(10,2400//tw)); rows=(len(ims)+cols-1)//cols
    S=Image.new('RGB',(cols*tw,rows*(th+14)),'white'); d=ImageDraw.Draw(S)
    for i,(im,f) in enumerate(zip(ims,fs)):
        x=(i%cols)*tw; y=(i//cols)*(th+14); S.paste(im.resize((tw,th)),(x,y+14)); d.text((x+2,y+1),os.path.basename(f)[:-4][:34],fill='black')
    S.save(f'sheets/{tag}.jpg',quality=80); print(tag,S.size)
