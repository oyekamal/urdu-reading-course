import json, math, h, sys
from t6_trace2 import *
out=[]
with sync_playwright() as p:
    b,pg=h.bare(p,420,900)
    for ch in ['ڈ','ڑ','ز','ذ','ژ','ٹ']:
        pg.evaluate(MOUNT.replace("['ا','ب']",json.dumps([ch,'ا'],ensure_ascii=False))); pg.wait_for_timeout(300); select(pg,ch,'isolated')
        for mark_style in ('dash8','squiggle','loop'):
            pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(120)
            pad=Pad(pg); sol=solve2(pad,pg.evaluate(NEXP,[ch,'isolated']))
            body=[ [tuple(pad.dot)]+sol['multi'][0] ] if sol['multi'] else []     # start AT the green dot, then join the stroke
            if len(sol['multi'])>1: body=[[tuple(pad.dot)]+sol['multi'][0]]+sol['multi'][1:]
            for s in body: pad.drag(s)
            for k,v in sol['marks']:
                c = v if k=='tap' else v[1]
                x,y=c
                if k=='drag' or mark_style!='dash8':
                    pass
                if mark_style=='dash8': pad.drag([(x-4,y-3),(x,y),(x+4,y+3)])
                elif mark_style=='squiggle': pad.drag([(x-14,y+4),(x-6,y-6),(x,y+3),(x+6,y-6),(x+14,y+4),(x+8,y+7),(x-2,y+6)])
                else: pad.drag([(x+9*math.cos(t/6*6.283+3), y+7*math.sin(t/6*6.283+3)) for t in range(8)])
            txt,cls=verdict(pg); L=sum(math.hypot(a[0]-b_[0],a[1]-b_[1]) for s in body for a,b_ in zip(s,s[1:]))
            out.append({'ch':ch,'mark':mark_style,'ok':'ok' in cls.split(),'msg':txt,'body_len':round(L),'dot':pad.dot,'start':sol['multi'][0][0] if sol['multi'] else None})
            print(out[-1],flush=True)
    b.close()
h.save('t6_tah.json',out)
