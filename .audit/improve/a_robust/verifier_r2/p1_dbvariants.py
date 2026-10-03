from common import *
import sys
def mkdb(pg, js):
    return pg.evaluate("async()=>{" + js + "}")
STORES = "['settings','profiles','attempts','cards','sessions','progress','assessments']"
CASES = {
 'other_version_5_full': """await new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader'); q.onsuccess=r; q.onblocked=r});
   await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader',5); r.onupgradeneeded=()=>{const d=r.result; const S={settings:'key',profiles:'id',attempts:'id',cards:'id',sessions:'id',progress:'id',assessments:'id'}; for(const [n,k] of Object.entries(S)){const s=d.createObjectStore(n,{keyPath:k}); if(['attempts','cards','sessions','assessments'].includes(n)) s.createIndex('profileId','profileId'); if(n==='attempts'||n==='assessments') s.createIndex('ts','ts'); if(n==='cards') s.createIndex('due','due');}}; r.onsuccess=()=>{r.result.close();res()}; r.onerror=()=>rej(r.error)});""",
 'empty_v1': """await new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader'); q.onsuccess=r; q.onblocked=r});
   await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader',1); r.onsuccess=()=>{r.result.close();res()}; r.onerror=()=>rej(r.error)});""",
 'only_settings_v1': """await new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader'); q.onsuccess=r; q.onblocked=r});
   await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader',1); r.onupgradeneeded=()=>{r.result.createObjectStore('settings',{keyPath:'key'})}; r.onsuccess=()=>{r.result.close();res()}; r.onerror=()=>rej(r.error)});""",
 'stores_without_indexes': """await new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader'); q.onsuccess=r; q.onblocked=r});
   await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader',1); r.onupgradeneeded=()=>{const d=r.result; const S={settings:'key',profiles:'id',attempts:'id',cards:'id',sessions:'id',progress:'id',assessments:'id'}; for(const [n,k] of Object.entries(S)) d.createObjectStore(n,{keyPath:k});}; r.onsuccess=()=>{r.result.close();res()}; r.onerror=()=>rej(r.error)});""",
 'profiles_store_wrong_keypath': """await new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader'); q.onsuccess=r; q.onblocked=r});
   await new Promise((res,rej)=>{const r=indexedDB.open('urdu-reader',1); r.onupgradeneeded=()=>{const d=r.result; const S={settings:'key',profiles:'name',attempts:'id',cards:'id',sessions:'id',progress:'id',assessments:'id'}; for(const [n,k] of Object.entries(S)) d.createObjectStore(n,{keyPath:k});}; r.onsuccess=()=>{r.result.close();res()}; r.onerror=()=>rej(r.error)});""",
}
def state(pg):
    return pg.evaluate("""()=>({text:document.getElementById('app').innerText.replace(/\\s+/g,' ').slice(0,90), recovery:!!document.querySelector('.recovery'), buttons:[...document.querySelectorAll('#app button')].map(b=>b.innerText.trim()).slice(0,5)})""")
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name in (sys.argv[1:] or list(CASES)):
            ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
            pg.evaluate("""async()=>{ const d=await new Promise((res)=>{const r=indexedDB.open('urdu-reader'); r.onsuccess=()=>res(r.result)}); d.close(); }""")
            # close the app's own connection by deleting through a fresh page is not possible; use a second page of the same context
            pg2 = ctx.new_page(); pg2.add_init_script(IDB); pg2.goto(BASE + 'robots.txt'); pg2.wait_for_timeout(300)
            pg.goto('about:blank')
            try: mkdb(pg2, CASES[name])
            except Exception as e: print(name, 'SETUP FAIL', str(e)[:100]); continue
            pg2.close(); pg3 = ctx.new_page(); errs = []; pg3.on('pageerror', lambda e: errs.append(str(e)[:100])); pg3.goto(BASE + '?skiponb')
            res = []
            for t in [2500, 9000, 16000]:
                pg3.wait_for_timeout(t - (res[-1][0] if res else 0)); res.append((t, state(pg3)))
            s = res[-1][1]
            # add a learner if mode picker visible, then check it works
            print(f'{name:30} 2.5s: {res[0][1]["text"][:50]!r} | 16s: {s["text"][:60]!r} rec={s["recovery"]} btn={s["buttons"]} errs={errs[:2]}', flush=True)
            try:
                click(pg3, 'text=Just me'); pg3.wait_for_timeout(500); click(pg3, 'text=+ Add a learner'); pg3.wait_for_timeout(400)
                pg3.fill('input[placeholder=Name]', 'Zed'); click(pg3, "button:has-text('Start')"); pg3.wait_for_timeout(3000)
                a = state(pg3); pg3.wait_for_timeout(12000); a2 = state(pg3)
                print('     after add learner 3s:', a['text'][:60], '| 15s:', a2['text'][:60], 'rec', a2['recovery'], 'errs', errs[:2], flush=True)
            except Exception as e: print('     flow EXC', str(e)[:100])
            ctx.close()
        b.close()
