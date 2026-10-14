import cairosvg, io, glob, os, sys, json
from PIL import Image, ImageDraw
fs=sorted(glob.glob('art/*.svg'), key=lambda f:int(os.path.basename(f)[:-4])); n=len(fs); cols=6; S=180
W=Image.new('RGB',(cols*S,((n+cols-1)//cols)*(S+22)),'white'); d=ImageDraw.Draw(W)
for i,f in enumerate(fs):
    p=Image.open(io.BytesIO(cairosvg.svg2png(url=f,output_width=S-10,output_height=S-10))).convert('RGBA'); x=(i%cols)*S; y=(i//cols)*(S+22)
    W.paste(p,(x+5,y),p); d.text((x+6,y+S-4),os.path.basename(f)[:-4],fill='black')
W.save(sys.argv[1] if len(sys.argv)>1 else '/tmp/art_all.png'); print(n)
