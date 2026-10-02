import json, sys, time, os
from h import *
BASE = 'http://localhost:5301/'
R = {}
IDB = """
const idb = () => new Promise((res, rej) => { const r = indexedDB.open('urdu-reader'); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
window.__dump = async () => { const d = await idb(); const out = {}; for (const n of d.objectStoreNames) { out[n] = await new Promise(r => { const q = d.transaction(n).objectStore(n).getAll(); q.onsuccess = () => r(q.result); }); } d.close(); return out; };
window.__put = async (s, v) => { const d = await idb(); await new Promise(r => { const t = d.transaction(s, 'readwrite'); t.objectStore(s).put(v); t.oncomplete = r; }); d.close(); };
"""
def newpage(b, init=None, **kw):
    ctx = b.new_context(viewport=VP, service_workers='block', accept_downloads=True, **kw); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160])); pg.on('dialog', lambda d: d.accept('5'))
    pg.add_init_script(IDB)
    if init: pg.add_init_script(init)
    pg._errs = errs; return ctx, pg
def counts(pg): d = pg.evaluate('__dump()'); return {k: len(v) for k, v in d.items()}, d
def nav(pg, k): pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`).click()", k); pg.wait_for_timeout(700)
def do_rules(pg):
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(700)
    for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(500)

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        # ---------- A. export/import round trip + no restore on fresh install
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal'); do_rules(pg)
        pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(600)
        for _ in range(2):  # a few more records: nav around
            nav(pg, 'review')
        nav(pg, 'me'); pg.screenshot(path=OUT + '/s6_me_child.png')
        me_txt = pg.inner_text('#app'); R['child_me_has_export'] = 'Export' in me_txt; R['child_me_has_import_input'] = pg.query_selector('input[type=file]') is not None
        c0, d0 = counts(pg); print('before export', c0)
        # try to trigger export on child Me tab
        btns = pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean)"); print('child Me buttons', btns)
        ctx.close()
        # adult profile Me/More tab has Data card
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Sam', 'adult'); pg.wait_for_timeout(500)
        for k in ['more']: nav(pg, k)
        adult_btns = pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean)")
        print('adult More buttons', adult_btns); R['adult_has_file_input'] = pg.query_selector('input[type=file]') is not None
        # seed data: attempts and cards for round trip
        pg.evaluate("""async()=>{const pid=(await __dump()).settings.find(s=>s.key==='activeProfile').value;
          for(let i=0;i<30;i++) await __put('attempts',{id:'a'+i,profileId:pid,unit:1,drill:'x',item:'ب',correct:i%2==0,ms:500,ts:Date.now()-i*1e5,updatedAt:Date.now()});
          for(const c of ['ا','ب','ک']) await __put('cards',{id:pid+':'+c,profileId:pid,item:c,kind:'letter',box:2,due:Date.now(),seen:1,updatedAt:Date.now()});
          await __put('progress',{id:pid,units:{0:{passed:true,score:10,total:10,at:Date.now()}},wpm:[],sessions:3,updatedAt:Date.now()});}""")
        c0, d0 = counts(pg); print('adult before export', c0)
        # export via UI -> download (navigator.share absent in headless chromium? fall back anchor download)
        pg.evaluate("()=>{navigator.canShare=undefined}")
        with pg.expect_download(timeout=10000) as dl: pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()")
        path = OUT + '/s6_backup.json'; dl.value.save_as(path); exp = json.load(open(path))
        print('exported keys', {k: (len(v) if isinstance(v, list) else v) for k, v in exp.items()}); R['export_has_teacherPin_field'] = any(s['key'] == 'teacherPin' for s in exp['settings'])
        # wipe DB, reload: fresh install
        pg.evaluate("()=>new Promise(r=>{const q=indexedDB.deleteDatabase('urdu-reader');q.onsuccess=r;q.onblocked=r})"); 
        pg.goto(BASE); pg.wait_for_timeout(2500)
        fresh_txt = pg.inner_text('#app'); R['fresh_install_offers_restore'] = bool(__import__('re').search('restore|import', fresh_txt, 2)); pg.screenshot(path=OUT + '/s6_fresh_after_wipe.png')
        print('fresh install screen:', fresh_txt[:120].replace('\n', ' | '), '| file input?', pg.query_selector('input[type=file]') is not None)
        # create throwaway learner, import
        quick_profile(pg, BASE, 'Temp', 'adult'); nav(pg, 'more')
        pg.set_input_files('input[type=file]', path); pg.wait_for_timeout(1500)
        toast = pg.evaluate("document.getElementById('toast')?.innerText"); print('toast after import:', toast)
        c1, d1 = counts(pg); print('after import', c1)
        # diff
        for s in ['attempts', 'cards', 'progress', 'sessions', 'profiles']:
            ids0 = {r.get('id') for r in d0.get(s, [])}; ids1 = {r.get('id') for r in d1.get(s, [])}; print(s, 'missing after restore:', len(ids0 - ids1), ' extra:', len(ids1 - ids0))
        # activeProfile / mode after restore
        st = {s['key']: s['value'] for s in d1['settings']}; st0 = {s['key']: s['value'] for s in d0['settings']}
        print('activeProfile before-export:', st0.get('activeProfile'), 'after-import:', st.get('activeProfile'), '| deviceId same?', st0.get('deviceId') == st.get('deviceId'))
        pg.reload(); pg.wait_for_timeout(2000); print('after reload shows:', pg.inner_text('#app')[:90].replace('\n', ' | '))
        pg.screenshot(path=OUT + '/s6_after_restore.png')
        # import corrupt files
        open('/tmp/claude-1000/bad1.json', 'w').write('{not json'); open('/tmp/claude-1000/bad2.json', 'w').write(json.dumps({'profiles': [None, {'id': 'x', 'name': 'ok', 'updatedAt': 1}], 'attempts': [{'noid': 1}]}))
        for bf in ['bad1', 'bad2']:
            pg.evaluate("document.getElementById('toast')&&(document.getElementById('toast').innerText='')"); n_err = len(pg._errs)
            nav(pg, 'more'); pg.set_input_files('input[type=file]', f'/tmp/claude-1000/{bf}.json'); pg.wait_for_timeout(1200)
            print(bf, 'toast:', repr(pg.evaluate("document.getElementById('toast')?.innerText")), 'new page errors:', pg._errs[n_err:])
        # settings overwrite by import (mode / activeProfile)
        evil = {'settings': [{'key': 'mode', 'value': 'school', 'updatedAt': int(time.time() * 1000) + 10**7}, {'key': 'teacherPin', 'value': '0000', 'updatedAt': int(time.time() * 1000) + 10**7}]}
        json.dump(evil, open('/tmp/claude-1000/evil.json', 'w')); nav(pg, 'more'); pg.set_input_files('input[type=file]', '/tmp/claude-1000/evil.json'); pg.wait_for_timeout(1200)
        s2 = {s['key']: s['value'] for s in pg.evaluate('__dump()')['settings']}; print('after importing settings-only file: mode =', s2.get('mode'), 'teacherPin =', s2.get('teacherPin'))
        ctx.close()
        json.dump(R, open(OUT + '/s6_a.json', 'w'), indent=1); print(R)
        b.close()
if __name__=='__main__': main()
