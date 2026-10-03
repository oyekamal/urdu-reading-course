from common import *
import json, tempfile, time
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'Heavy')
    t0 = time.time()
    pg.evaluate("""async()=>{ const d=await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader'); r.onsuccess=()=>res(r.result)}); const pid=(await __dump()).profiles[0].id;
      await new Promise(r=>{const t=d.transaction('attempts','readwrite'); const s=t.objectStore('attempts'); for(let i=0;i<62000;i++) s.put({id:'h'+i,profileId:pid,unit:1,drill:'tell',item:'ا',correct:i%2==0,ms:500,ts:Date.now()-i,updatedAt:Date.now()}); t.oncomplete=r}); d.close(); }""")
    pg.reload(); t1=time.time()
    pg.wait_for_selector('.bottom', timeout=60000); print('learner screen after', round(time.time()-t1,1), 's', pg.inner_text('#app')[:40].replace(chr(10),' | '))
    nav(pg, 'me'); pg.wait_for_selector('text=Export backup', timeout=60000)
    with pg.expect_download(timeout=60000) as dl:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()"); gate_pass(pg)
    raw = open(dl.value.path()).read(); print('export ok, bytes', len(raw), 'attempts', json.loads(raw)['attempts'].__len__(), 'secs', round(time.time() - t0))
    ctx2, pg2 = newpage(b); pg2.goto(BASE); pg2.wait_for_timeout(2200)
    f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(raw)
    with pg2.expect_file_chooser(timeout=6000) as fc:
        pg2.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(f); pg2.wait_for_timeout(4000)
    print('restore of own export on new phone ->', toast(pg2), '| profiles', counts(pg2)[0]['profiles'])
    b.close()
