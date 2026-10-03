from common import *
from t1_teacher import setup, unlock, tab
import json
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); setup(pg); unlock(pg); tab(pg,'Reports')
    f={'format':'urdu-qaida-backup','version':1,'assessments':[{'id':'imp1','profileId':'t2','ts':9999999999999 if False else 2000000000000}]}
    p_=tempfile.mktemp(suffix='.json'); open(p_,'w').write(json.dumps(f))
    with pg.expect_file_chooser(timeout=8000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup/.test(b.innerText)).click()"); gate_pass(pg)
    fc.value.set_files(p_); pg.wait_for_timeout(2000)
    print('toast:', toast(pg), '| errs:', pg._errs[-2:])
    print('Reports body now:', pg.inner_text('#app')[:120].replace('\n',' | '))
    for t in ['Class','Groups','Assess','Reports']:
        before=len(pg._errs); tab(pg,t); print(t, 'new errors:', pg._errs[before:], '| shows:', pg.inner_text('#app')[60:110].replace('\n',' | '))
    b.close()
