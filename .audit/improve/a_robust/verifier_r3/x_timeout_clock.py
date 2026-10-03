import sys; sys.path.insert(0,'.')
from common import *
import json, time
BASE='http://localhost:5371/'
N=120000; now=int(time.time()*1000)
att=[{'id':'mg%08x%06x'%(i*7919,i),'profileId':'mgp0001','unit':i%12,'drill':'dictation','item':'بابا','correct':bool(i%3),'ms':1200+i%900,'ts':now-i*1000,'updatedAt':now-i*1000} for i in range(N)]
d={'format':'urdu-qaida-backup','version':1,'exportedAt':'2026-10-03T00:00:00Z','profiles':[{'id':'mgp0001','kind':'learner','name':'Big','track':'child','grade':'2','createdAt':now,'updatedAt':now}],'attempts':att}
f='/tmp/claude-1000/vr3_mid.json'; open(f,'w').write(json.dumps(d,ensure_ascii=False))
with sync_playwright() as p:
    b=p.chromium.launch()
    for delay in (4000,8000):
        ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(2500)
        pg.clock.install(); pg.clock.resume() if hasattr(pg.clock,'resume') else None
        with pg.expect_file_chooser(timeout=8000) as fc: click(pg,'.ob-restore')
        fc.value.set_files(f); pg.wait_for_timeout(delay)
        pg.clock.fast_forward(130000); pg.wait_for_timeout(1500)
        t1=toast(pg); c1=counts(pg)[0].get('attempts')
        pg.wait_for_timeout(25000); c2=counts(pg)[0].get('attempts')
        print(f'delay {delay}: toast right after timeout={t1!r}; attempts then={c1}; attempts 25s later={c2}; screen={pg.inner_text("#app")[:40]!r}',flush=True); ctx.close()
