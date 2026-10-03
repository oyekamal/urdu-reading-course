from common import *
import sys, json
CLICKALL = """async()=>{ const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let n=0;
  const skip=/Leave|Back|Units|Learn|Review|Read|Me|Progress|More|Today|Switch|^$/;
  for(let round=0; round<3; round++){
   const bs=[...document.querySelectorAll('.t-kids button, #app main button, main button, .lesson button')].filter(b=>!b.closest('.bottom')&&!b.closest('.page-head')&&!b.disabled);
   for(const b of bs){ try{ b.click(); n++ }catch(e){} await sleep(15) }
   await sleep(400);
  }
  return n }"""
def snap(pg):
    c, d = counts(pg); return {'c': c, 'progress': d['progress'], 'cards': len(d['cards']), 'attempts': len(d['attempts']), 'sessions': len(d['sessions']), 'settings': {s['key']: s['value'] for s in d['settings'] if s['key'] not in ('deviceId',)}}
def open_unit(pg, n):
    pg.evaluate("document.querySelector(\".bottom button[data-k='today']\").click()"); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelector('.all-units').click()"); pg.wait_for_timeout(900)
    pg.evaluate("n=>{const b=[...document.querySelectorAll('.ucard')].find(x=>x.getAttribute('aria-label').startsWith('Unit '+n+','));b.click()}", n); pg.wait_for_timeout(1200)
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx, pg = newpage(b); dialogs = []
        pg.remove_listener('dialog', pg.listeners('dialog')[0]) if hasattr(pg, 'listeners') else None
        quick_profile(pg, 'Gate')
        pg.on('dialog', lambda d: dialogs.append(d.type + ':' + d.message[:50]))
        before = snap(pg); print('before', before['c'], before['progress'])
        for n in [1, 2, 4, 5, 6, 10, 11, 12]:
            open_unit(pg, n)
            head = pg.inner_text('#app')[:80].replace('\n', ' | ')
            clicked = pg.evaluate(CLICKALL); pg.wait_for_timeout(1500)
            after = snap(pg)
            print(f'unit {n}: preview-note={bool(pg.query_selector(".preview-note"))} clicked={clicked} head={head[:50]!r} attempts={after["attempts"]} cards={after["cards"]} sessions={after["sessions"]} progress_same={after["progress"]==before["progress"]} settings={after["settings"].keys()} errs={pg._errs[:2]}', flush=True)
        print('dialogs', dialogs)
        b.close()
