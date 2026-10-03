import sys
from lib import *
FORMS=['isolated','initial','medial','final']
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for style,brush in (('nastaliq',28),('nastaliq',20),('naskh',20)):
        for ch,f in (('ا','isolated'),('ر','final'),('ط','isolated'),('ک','initial'),('ب','isolated'),('ل','isolated')):
            pg.evaluate(MOUNT,[[ch,'ب' if ch!='ب' else 'ا'],style]); pg.wait_for_timeout(250)
            pg.click(f'.pchip:nth-child({FORMS.index(f)+1})'); pg.wait_for_timeout(200)
            glyph= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,glyph,style); ink=P.ink
            mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask); body=thin(max(cover_strokes(sk,P.dot),key=len),3)
            cv=np.zeros((300,360),np.uint8); pts=np.array([[int(x),int(y)] for x,y in body],np.int32).reshape(-1,1,2); cv2.polylines(cv,[pts],False,1,brush,cv2.LINE_AA)
            for m in P.comps[1:]: c=m['c']; cv2.circle(cv,(int(c[0]),int(c[1])),22,1,-1)
            g=int(ink.sum()); hit=int(((cv>0)&(ink>0)).sum()); stray=int(((cv>0)&(ink==0)).sum()); marks=len(P.comps)-1
            print(style,brush,ch,f,'g',g,'cov',round(100*hit/g),'stray',stray,'limit',round(g*0.8+1500+700*marks),'neat',stray<g*0.8+1500+700*marks)
    b.close()
