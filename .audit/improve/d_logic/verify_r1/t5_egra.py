import json, h, sys
from playwright.sync_api import sync_playwright
BOOT = '''async () => { const E = await import('/src/egra.js'); const {db} = await import('/src/db.js'); const Cn = await import('/src/content.js'); await Cn.loadContent();
  document.body.innerHTML = '<div id="eg"></div>'; window.__done = null; await db.put('profiles',{id:'pE',kind:'learner',name:'Kid',track:'child'});
  E.runEgra(document.getElementById('eg'), null, {id:'pE', name:'Kid'}, r => { window.__done = r; }); }'''
def btn(pg, text, exact=True):
    return pg.evaluate("""([t,ex])=>{const b=[...document.querySelectorAll('#eg button')].find(b=>ex?b.textContent.trim()===t:b.textContent.includes(t)); if(!b) return 'missing'; if(b.disabled) return 'disabled'; b.click(); return 'ok'}""", [text, exact])
def words(pg): return pg.evaluate("document.querySelectorAll('#eg .item').length")
def wclick(pg, i): pg.evaluate("i=>document.querySelector('#eg .item[data-i=\"'+i+'\"]').click()", i)
def note(pg): return pg.evaluate("[...document.querySelectorAll('#eg .muted')].map(e=>e.textContent).join(' | ')")
def toastt(pg): return pg.evaluate("document.getElementById('toast')?.textContent||''")
def start(p, comp='skip', label=''):
    b = p.chromium.launch(executable_path=h.EXE); pg = b.new_context(viewport={'width':390,'height':800}).new_page(); pg.errors=[]; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept())
    pg.clock.install(time=1_700_000_000_000); pg.goto(h.URL); pg.wait_for_timeout(1500); pg.clock.pause_at(1_700_000_100_000)
    pg.evaluate(BOOT); pg.wait_for_timeout(200)
    for _ in range(3): 
        assert btn(pg,'Skip')=='ok'; pg.wait_for_timeout(50)
    assert 'Passage' in pg.inner_text('#eg h2'), pg.inner_text('#eg h2')
    return b, pg
def finish_to_result(pg, comp):
    # comprehension
    pg.wait_for_timeout(100)
    h2 = pg.inner_text('#eg h2')
    if 'Comprehension' in h2:
        if comp is None: btn(pg,'Skip')
        else:
            for i in range(5):
                btn(pg, 'Correct' if i < comp else 'Incorrect')
    pg.wait_for_timeout(100)
    rows = pg.evaluate("[...document.querySelectorAll('#eg tr')].map(r=>[...r.children].map(c=>c.textContent))")
    return dict(rows)
def save(pg):
    btn(pg,'Save assessment'); pg.wait_for_timeout(300)
    return pg.evaluate("window.__done")
CASES = {}
def case(name):
    def d(f): CASES[name]=f; return f
    return d
def advance(pg, ms): pg.clock.run_for(ms); pg.wait_for_timeout(30)
@case('finish at 0s, never marked, then wait to expiry -> must ask where the child got to')
def c1(pg):
    r = {}; r['click0'] = btn(pg,'Child finished'); r['note0'] = note(pg)[:90]; r['still_passage'] = 'Passage' in pg.inner_text('#eg h2')
    advance(pg, 60500); r['after_expiry_note'] = note(pg)[:140]; r['scoreit_state'] = btn(pg,'Score it'); r['h2'] = pg.inner_text('#eg h2')[:30]
    return r
@case('finish at 1s / 14s / 14.9s ignored; 15s accepted with mark')
def c2(pg):
    r={}; wclick(pg,0); 
    btn(pg,'Mark last word reached'); wclick(pg,19)
    advance(pg,1000); btn(pg,'Child finished'); r['t1']= 'Passage' in pg.inner_text('#eg h2')
    advance(pg,13000); btn(pg,'Child finished'); r['t14']='Passage' in pg.inner_text('#eg h2')
    advance(pg,900); btn(pg,'Child finished'); r['t14.9']='Passage' in pg.inner_text('#eg h2')
    advance(pg,100); btn(pg,'Child finished'); r['t15_moved_on']= 'Passage' not in pg.inner_text('#eg h2')
    r['res']=finish_to_result(pg, 5); return r
@case('60s expiry with mark at word 30, 3 errors')
def c3(pg):
    r={}; [wclick(pg,i) for i in (2,5,9)]; btn(pg,'Mark last word reached'); wclick(pg,29); advance(pg,60500); r['res']=finish_to_result(pg,5); r['rec']=save(pg); return r
@case('all words wrong then mark last 52, finish at 40s')
def c4(pg):
    r={}; [wclick(pg,i) for i in range(52)]; btn(pg,'Mark last word reached'); wclick(pg,51); advance(pg,40000); btn(pg,'Child finished'); r['res']=finish_to_result(pg,0); return r
@case('forgot mark, finish at 30s, says read to end -> seconds 30')
def c5(pg):
    r={}; advance(pg,30000); btn(pg,'Child finished'); r['ask_visible']=pg.evaluate("[...document.querySelectorAll('#eg .row')].some(x=>x.textContent.includes('whole passage')&&x.style.display!=='none')"); r['yes']=btn(pg,'Read to the end'); r['res']=finish_to_result(pg,4); r['rec']=save(pg); return r
@case('mark word 10 then change mark to word 4, finish at 20s')
def c6(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,10); btn(pg,'Mark last word reached'); wclick(pg,4); advance(pg,20000); btn(pg,'Child finished'); r['res']=finish_to_result(pg,3); return r
@case('mark then accidental quick Finish at 2s, continue, timer expiry')
def c7(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,12); advance(pg,2000); btn(pg,'Child finished'); r['still']= 'Passage' in pg.inner_text('#eg h2'); advance(pg,60000); r['res']=finish_to_result(pg,5); return r
@case('Skip passage then comprehension 5/5')
def c8(pg):
    r={}; btn(pg,'Skip'); r['res']=finish_to_result(pg,5); r['rec']=save(pg); return r
@case('double-click Finish at 20s with mark (two clicks same tick)')
def c9(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,40); advance(pg,20000)
    pg.evaluate("()=>{const b=[...document.querySelectorAll('#eg button')].find(b=>b.textContent.trim()==='Child finished'); b.click(); b.click();}")
    r['res']=finish_to_result(pg,5); r['rec']=save(pg); r['n_records']=pg.evaluate("async()=>{const {db}=await import('/src/db.js');return (await db.all('assessments')).length}"); return r
@case('expiry then Read no words')
def c10(pg):
    r={}; advance(pg,60500); r['none']=btn(pg,'Read no words'); r['res']=finish_to_result(pg,2); r['rec']=save(pg); return r
@case('expiry: mark at 52 (end) in awaiting then Score it, comprehension 1/5')
def c11(pg):
    r={}; advance(pg,61000); wclick(pg,51); r['score']=btn(pg,'Score it'); r['res']=finish_to_result(pg,1); return r
@case('exactly at 15.0s finish with mark at last word (cap check)')
def c12(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,51); advance(pg,15000); btn(pg,'Child finished'); r['res']=finish_to_result(pg,5); r['rec']=save(pg); return r
@case('click Finish at 59.9s with mark, then timer expiry fires')
def c13(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,30); advance(pg,59900); btn(pg,'Child finished'); advance(pg,1000); r['res']=finish_to_result(pg,5); r['rec']=save(pg); r['n']=pg.evaluate("async()=>{const {db}=await import('/src/db.js');return (await db.all('assessments')).length}"); return r
@case('mark word, finish at 60s expiry+comprehension skipped')
def c14(pg):
    r={}; btn(pg,'Mark last word reached'); wclick(pg,51); advance(pg,61000); r['res']=finish_to_result(pg,None); r['rec']=save(pg); return r
@case('no click at all for 120 s (timer expiry) then nothing: is state sane')
def c15(pg):
    r={}; advance(pg,120000); r['note']=note(pg)[:120]; r['h2']=pg.inner_text('#eg h2')[:40]; r['timer']=pg.evaluate("document.querySelector('#eg .timer')?.textContent"); return r
if __name__=='__main__':
    out={}
    with sync_playwright() as p:
        for name,f in CASES.items():
            b,pg=start(p)
            try: out[name]=f(pg)
            except Exception as e: out[name]={'EXC':str(e)[:200]}
            out[name]['errors']=h.real_errors(pg); b.close()
            print(name, '->', json.dumps(out[name],ensure_ascii=False)[:900], flush=True)
    h.save('t5_egra.json', out)
