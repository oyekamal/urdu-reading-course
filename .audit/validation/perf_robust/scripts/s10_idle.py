from h import *
from s6_data import newpage
BASE='http://localhost:5301/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE,args=['--no-sandbox']); ctx,pg=newpage(b); quick_profile(pg,BASE,'Amal'); pg.wait_for_timeout(2500)
    cdp=ctx.new_cdp_session(pg); cdp.send('Performance.enable')
    def cpu(lab,ms=6000):
        m0={x['name']:x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; pg.wait_for_timeout(ms)
        m1={x['name']:x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
        d={k:round((m1[k]-m0[k])/ (ms/1000)*100) for k in ['TaskDuration','ScriptDuration','RecalcStyleDuration','LayoutDuration']}
        print(f'{lab:42}', 'main-thread busy % of wall:', d)
    print('css animations running:', pg.evaluate("document.getAnimations().length"), 'by name:', pg.evaluate("Object.entries(document.getAnimations().reduce((a,x)=>{const n=x.animationName||x.constructor.name;a[n]=(a[n]||0)+1;return a},{})).slice(0,12)"))
    cpu('Today, everything running')
    pg.evaluate("document.getAnimations().forEach(a=>a.pause())"); cpu('CSS animations paused')
    pg.evaluate("document.querySelectorAll('.marko').forEach(m=>{m._marko&&m._marko.anim&&m._marko.anim.pause()})"); cpu('+ Marko lottie paused')
    print('app reduced-motion variant:')
    ctx2=b.new_context(viewport=VP,service_workers='block',reduced_motion='reduce'); pg2=ctx2.new_page(); quick_profile(pg2,BASE,'Amal'); pg2.wait_for_timeout(2500); cdp=ctx2.new_cdp_session(pg2); cdp.send('Performance.enable'); pg=pg2
    cpu('Today with prefers-reduced-motion')
    b.close()
