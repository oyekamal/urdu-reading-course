import sys; sys.path.insert(0,'.')
from common import *
import json, tempfile, time, random
BASE='http://localhost:5371/'
N=int(sys.argv[1]) if len(sys.argv)>1 else 200000
now=int(time.time()*1000)
att=[{'id':'mg%08x%06x'%(i*7919,i),'profileId':'mgp0001','unit':i%12,'drill':'dictation','item':'بابا','correct':bool(i%3),'ms':1200+i%900,'ts':now-i*1000,'updatedAt':now-i*1000} for i in range(N)]
d={'format':'urdu-qaida-backup','version':1,'exportedAt':'2026-10-03T00:00:00Z','device':'x','profiles':[{'id':'mgp0001','kind':'learner','name':'Big','track':'child','grade':'2','createdAt':now,'updatedAt':now}],'attempts':att}
raw=json.dumps(d,ensure_ascii=False); print('bytes',len(raw.encode()), 'limit', 40*1024*1024)
f='/tmp/claude-1000/vr3_big.json'; open(f,'w').write(raw)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(2500)
    t0=time.time()
    with pg.expect_file_chooser(timeout=8000) as fc: click(pg,'.ob-restore')
    fc.value.set_files(f)
    for i in range(170):
        pg.wait_for_timeout(1000); t=toast(pg)
        if t and ('Restored' in t or 'large' in t or 'could not' in t or 'Nothing' in t): break
    print('after',round(time.time()-t0,1),'s toast:',toast(pg),'| errs',pg._errs[:2])
    pg.wait_for_timeout(3000); print({k:v for k,v in counts(pg)[0].items() if v}); print(pg.inner_text('#app')[:60].replace('\n',' | '))
