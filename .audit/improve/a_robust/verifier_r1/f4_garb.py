from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    for s in ['profiles','attempts','cards','sessions','progress','assessments']:
      for bval in ["5","[1]","{x:1}","true"]:
        ctx,pg=newpage(b); quick_profile(pg,'Gar')
        pg.evaluate("async([s,v])=>{ const b=eval(v); await __put(s,{id:b,profileId:b,name:b,track:b,ts:b,units:b,wpm:b,orf:b,band:b,by:b,item:b,kind:b,due:b,box:b,seen:b}).catch(e=>0)}",[s,bval]) if False else None
        # eval is blocked by CSP; pass JSON instead
        import json
        vals={"5":5,"[1]":[1],"{x:1}":{"x":1},"true":True}
        r=pg.evaluate("async([s,b])=>{ try{ await __put(s,{id:b,profileId:b,name:b,track:b,ts:b,units:b,wpm:b,orf:b,band:b,by:b,item:b,kind:b,due:b,box:b,seen:b}); return 'put ok'}catch(e){return 'put failed '+e}}",[s,vals[bval]])
        pg.reload(); pg.wait_for_timeout(1800)
        t=pg.inner_text('#app')[:60].replace('\n',' | ')
        why=pg.evaluate("document.querySelector('.rec-why')?.textContent")
        if 'could not open' in t or pg._errs: print(s,bval,r,'->',t[:40],'| why:',why,pg._errs[:1])
        ctx.close()
    b.close()
