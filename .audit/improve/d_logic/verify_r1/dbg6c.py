import json, h, sys
from t6_trace2 import *
ch=sys.argv[1]
with sync_playwright() as p:
    b,pg=h.bare(p,420,900); pg.evaluate(MOUNT.replace("['ا','ب']",json.dumps([ch,'ا'],ensure_ascii=False))); pg.wait_for_timeout(300)
    select(pg,ch,'isolated'); pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(200)
    pad=Pad(pg); sol=solve2(pad,pg.evaluate(NEXP,[ch,'isolated'])); S=sol['single']
    print('dot',pad.dot,'S0',S[0],'S-1',S[-1],len(S), 'sample', S[::10])
    js="""async ([strokes,dot,ch]) => { const D=await import('/src/drills.js'); const cv=document.createElement('canvas'); cv.width=360;cv.height=300; const g=cv.getContext('2d',{willReadFrequently:true}); g.fillStyle=getComputedStyle(document.body).getPropertyValue('--line'); g.font='170px "Noto Naskh Arabic"'; g.textAlign='center'; g.textBaseline='middle'; g.direction='rtl'; g.fillText(ch,180,150); const ref=g.getImageData(0,0,360,300).data;
      return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'}); }"""
    for name,st in (('fwd',S),('rev',S[::-1])):
        print(name,json.dumps(pg.evaluate(js,[[[[float(x),float(y)] for x,y in st]],list(pad.dot),ch])))
    b.close()
