import json, time, re
from h import *
from s6_data import newpage, counts, nav, do_rules
from s7_robust import CLOCK, T
BASE = 'http://localhost:5301/'
def main():
  with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    def t_onb():
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2000); click(pg, "text=Let's begin"); click(pg, '.ob-sleeper'); pg.wait_for_timeout(2600)
        pg.evaluate("()=>{const b=document.querySelector('.ob-cta');b.click();b.click()}"); pg.wait_for_timeout(900)
        onb = pg.evaluate("__dump().then(d=>d.settings.find(s=>s.key==='onb'))"); print('colour screen CTA double-click: saved i =', onb['value']['i'], '(colour=2 -> who=3 expected after one click; 4 = a screen skipped)')
        print('screen now:', pg.evaluate("document.querySelector('.ob')?.innerText.slice(0,50)").replace('\n',' '))
        click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', 'Zara'); click(pg, '.ob-cta'); pg.wait_for_timeout(600)
        pg.reload(); pg.wait_for_timeout(2500); print('killed at goal screen -> after reload:', pg.evaluate("document.querySelector('.ob')?.innerText.slice(0,60)").replace('\n',' '), '| saved:', pg.evaluate("__dump().then(d=>JSON.stringify(d.settings.find(s=>s.key==='onb').value))"))
        ctx.close()
    T('onboarding double-tap + resume', t_onb)
    def t_clock():
        ctx, pg = newpage(b, init=CLOCK); quick_profile(pg, BASE, 'Amal')
        pg.evaluate("""async()=>{const pid=(await __dump()).settings.find(s=>s.key==='activeProfile').value;const DAY=864e5;
          for(let i=0;i<3;i++) await __put('attempts',{id:'a'+i,profileId:pid,unit:0,drill:'x',item:'ا',correct:true,ms:1,ts:Date.now()-i*DAY,updatedAt:Date.now()});
          for(const [c,box,due] of [['ا',3,Date.now()+2*DAY],['ب',2,Date.now()+1*DAY],['ک',1,Date.now()-1000]]) await __put('cards',{id:pid+':'+c,profileId:pid,item:c,kind:'letter',box,due,seen:1,updatedAt:Date.now()});}""")
        def state(lab):
            pg.reload(); pg.wait_for_timeout(1800); today = re.sub(r'\s+', ' ', pg.inner_text('#app')); chip = re.findall(r'(First day today|\d+ days? practised[^ ]*|\d+ days?[^.]{0,20})', today)[:2]; mins = re.findall(r'(\d+ / \d+ min)', today)
            nav(pg, 'review'); rv = re.sub(r'\s+', ' ', pg.inner_text('#app'))[:100]; print(f'{lab:>26}: chip={chip} goal={mins} | review: {rv}')
        state('t0 (3 attempts: 0,-1,-2d)')
        for off, lab in [(1.5 * 86400000, '+1.5 days'), (3 * 86400000, '+3 days'), (30 * 86400000, '+30 days'), (-3 * 86400000, '-3 days'), (-400 * 86400000, '-400 days')]:
            pg.evaluate("o=>localStorage.setItem('__off',o)", off); state(lab)
        print('errors', pg._errs); ctx.close()
    T('clock with seeded attempts/cards', t_clock)
    def t_corrupt():
        # (a) a store missing (partial DB at version 1)
        ctx, pg = newpage(b); pg.goto(BASE + 'nonexistent-warm.html'); 
        pg.evaluate("""()=>new Promise(r=>{indexedDB.deleteDatabase('urdu-reader').onsuccess=()=>{const q=indexedDB.open('urdu-reader',1);q.onupgradeneeded=()=>{q.result.createObjectStore('settings',{keyPath:'key'});q.result.createObjectStore('profiles',{keyPath:'id'})};q.onsuccess=()=>{q.result.close();r()}}})""")
        pg.goto(BASE); pg.wait_for_timeout(3000); print('(a) DB missing stores -> screen:', pg.inner_text('#app')[:80].replace('\n', ' | '), '| errs', pg._errs[:2]); pg.screenshot(path=OUT + '/s8_corrupt_missing_store.png'); ctx.close()
        # (b) malformed progress record: units null
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal')
        pg.evaluate("""async()=>{const pid=(await __dump()).settings.find(s=>s.key==='activeProfile').value;await __put('progress',{id:pid,units:null,wpm:'x'})}"""); pg.reload(); pg.wait_for_timeout(2500)
        print('(b) progress.units=null -> screen:', pg.inner_text('#app')[:80].replace('\n', ' | '), '| errs', pg._errs[:2]); ctx.close()
        # (c) activeProfile points at deleted profile
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal'); pg.evaluate("""async()=>{await __put('settings',{key:'activeProfile',value:'gone'})}"""); pg.reload(); pg.wait_for_timeout(2500)
        print('(c) activeProfile dangling -> screen:', pg.inner_text('#app')[:60].replace('\n', ' | ')); ctx.close()
        # (d) mode set but profile record malformed (no name / track)
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal'); pg.evaluate("""async()=>{const pid=(await __dump()).settings.find(s=>s.key==='activeProfile').value;await __put('profiles',{id:pid})}"""); pg.reload(); pg.wait_for_timeout(2500)
        print('(d) profile without name/track -> screen:', pg.inner_text('#app')[:80].replace('\n', ' | '), '| errs', pg._errs[:2]); ctx.close()
        # (e) indexedDB unavailable
        ctx, pg = newpage(b, init="Object.defineProperty(window,'indexedDB',{get(){return undefined}})"); pg.goto(BASE); pg.wait_for_timeout(3000); print('(e) no indexedDB -> screen:', pg.inner_text('#app')[:80].replace('\n', ' | '), '| errs', pg._errs[:2]); pg.screenshot(path=OUT + '/s8_no_idb.png'); ctx.close()
        # (f) IDB commit fails with quota abort after boot
        QUOTA = "(()=>{const p=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v,k){if(window.__q&&this.name!=='settings'){const r=p.call(this,v,k);try{this.transaction.abort()}catch(e){}return r}return p.call(this,v,k)}})()"
        ctx, pg = newpage(b, init=QUOTA); quick_profile(pg, BASE, 'Amal'); pg.evaluate("window.__q=1")
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(700)
        for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(600)
        pg.wait_for_timeout(2500); print('(f) writes abort (quota) at lesson end -> celebrate shown?', pg.query_selector('.celebrate') is not None, '| screen:', pg.inner_text('#app')[:70].replace('\n', ' | '), '| errs', pg._errs[:2]); pg.screenshot(path=OUT + '/s8_quota.png'); ctx.close()
    T('corrupt / quota / no idb', t_corrupt)
    b.close()
if __name__ == '__main__': main()
