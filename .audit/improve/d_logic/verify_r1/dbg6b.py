import json, h, sys
from t6_trace2 import *
ch=sys.argv[1]
with sync_playwright() as p:
    b,pg=h.bare(p,420,900); pg.evaluate(MOUNT.replace("['ا','ب']",json.dumps([ch,'ا'],ensure_ascii=False))); pg.wait_for_timeout(300)
    select(pg,ch,'isolated'); pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(200)
    pad=Pad(pg); sol=solve2(pad,pg.evaluate(NEXP,[ch,'isolated']))
    print('dot',pad.dot,'single len',len(sol['single']),'start',sol['single'][0],'end',sol['single'][-1],'multi',[ (s[0],s[-1],len(s)) for s in sol['multi']],'marks',sol['marks'])
    js="""async ([strokes,ref0,dot,ch]) => { const D=await import('/src/drills.js'); const cv=document.createElement('canvas'); cv.width=360;cv.height=300; const g=cv.getContext('2d',{willReadFrequently:true}); g.fillStyle=getComputedStyle(document.body).getPropertyValue('--line'); g.font='170px "Noto Naskh Arabic"'; g.textAlign='center'; g.textBaseline='middle'; g.direction='rtl'; g.fillText(ch,180,150); const ref=g.getImageData(0,0,360,300).data;
      return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'}); }"""
    for name,st in (('single',[sol['single']]),('multi',sol['multi'])):
        S=[[[float(x),float(y)] for x,y in s] for s in st]
        # marks as short strokes
        for k,v in sol['marks']:
            if k=='tap': x,y=v; S.append([[x-4,y-3],[x,y],[x+4,y+3]])
            else: S.append([[float(a),float(b_)] for a,b_ in v])
        print(name, json.dumps(pg.evaluate(js,[S,None,list(pad.dot),ch])))
    b.close()
