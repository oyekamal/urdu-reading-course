import json, h, sys
from t6_trace2 import *
ch=sys.argv[1]
with sync_playwright() as p:
    b,pg=h.bare(p,420,900); pg.evaluate(MOUNT.replace("['ا','ب']",json.dumps([ch,'ا'],ensure_ascii=False))); pg.wait_for_timeout(300)
    select(pg,ch,'isolated'); pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(200)
    pad=Pad(pg); sol=solve2(pad,pg.evaluate(NEXP,[ch,'isolated'])); M=sol['multi']
    parts=[x for i,m in enumerate(M) for x in (split(m,2) if i==0 else [m])]
    marks=[]; 
    for k,v in sol['marks']:
        if k=='tap': x,y=v; marks.append([(x-4,y-3),(x,y),(x+4,y+3)])
        else: marks.append(v)
    js="""async ([strokes,dot,ch]) => { const D=await import('/src/drills.js'); const cv=document.createElement('canvas'); cv.width=360;cv.height=300; const g=cv.getContext('2d',{willReadFrequently:true}); g.fillStyle=getComputedStyle(document.body).getPropertyValue('--line'); g.font='170px "Noto Naskh Arabic"'; g.textAlign='center'; g.textBaseline='middle'; g.direction='rtl'; g.fillText(ch,180,150); const ref=g.getImageData(0,0,360,300).data;
      return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'}); }"""
    print('dot',pad.dot,'parts',[(p_[0],p_[-1]) for p_ in parts])
    for name,st in (('nolift',M+marks),('lift2',parts+marks),('lift1',[x for i,m in enumerate(M) for x in (split(m,1) if i==0 else [m])]+marks)):
        print(name,json.dumps(pg.evaluate(js,[[[[float(x),float(y)] for x,y in s] for s in st],list(pad.dot),ch])))
    b.close()
