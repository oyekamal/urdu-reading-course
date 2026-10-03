import json
from lib import *
BOOT = '''async () => { const E = await import('/src/egra.js'); const {db} = await import('/src/db.js'); const Cn = await import('/src/content.js'); await Cn.loadContent();
  document.body.innerHTML = '<div id="eg"></div>'; window.__done = null; await db.put('profiles',{id:'pE',kind:'learner',name:'Kid',track:'child'});
  E.runEgra(document.getElementById('eg'), null, {id:'pE', name:'Kid'}, r => { window.__done = r; }); }'''
def btn(pg,t,exact=True):
    return pg.evaluate("""([t,ex])=>{const b=[...document.querySelectorAll('#eg button')].find(b=>ex?b.textContent.trim()===t:b.textContent.includes(t)); if(!b) return 'missing'; if(b.disabled) return 'disabled'; b.click(); return 'ok'}""",[t,exact])
def item(pg,i): pg.evaluate("i=>document.querySelector('#eg .item[data-i=\"'+i+'\"]').click()",i)
def adv(pg,ms): pg.clock.run_for(ms); pg.wait_for_timeout(30)
def h2(pg): return pg.inner_text('#eg h2')
def rows(pg): return dict(pg.evaluate("[...document.querySelectorAll('#eg tr')].map(r=>[...r.children].map(c=>c.textContent))") or [])
def note(pg): return pg.evaluate("[...document.querySelectorAll('#eg .muted, #eg .row span')].map(e=>e.textContent).join(' | ')")[:200]
R={}
def new(p):
    b,pg=browser(p,390,900); pg.clock.install(time=1_700_000_000_000); pg.goto(URL); pg.wait_for_timeout(1500); pg.clock.pause_at(1_700_000_100_000); pg.evaluate(BOOT); pg.wait_for_timeout(200); return b,pg
def to_passage(pg):
    for _ in range(3): btn(pg,'Skip'); pg.wait_for_timeout(40)
with sync_playwright() as p:
    # flash: ask path
    b,pg=new(p); r={}
    adv(pg,60500); r['ask_text']=note(pg); r['empty']=btn(pg,'Score it'); r['toast']=pg.evaluate("document.getElementById('toast')?.textContent||''"); r['still']=h2(pg)
    pg.fill('#eg input[type=number]','500'); btn(pg,'Score it'); pg.wait_for_timeout(50); r['after500_h2']=h2(pg); R['flash_ask_500']=r
    # subtask 2: nothing tapped, type 0
    adv(pg,60500); pg.fill('#eg input[type=number]','0'); btn(pg,'Score it'); r['sub2_zero_h2']=h2(pg)
    # subtask 3: tap Next once, timeout
    btn(pg,'Next ›'); adv(pg,60500); r['sub3_touch_next_h2']=h2(pg)
    # passage: timeout untouched
    adv(pg,60500); r['passage_ask']=note(pg); r['finish_btn']=btn(pg,'Score it'); r['none']='shown' if pg.evaluate("[...document.querySelectorAll('#eg button')].some(b=>b.textContent==='Read no words'&&b.style.display!=='none')") else 'hidden'
    btn(pg,'Read no words'); pg.wait_for_timeout(100); r['after_none_h2']=h2(pg)
    for i in range(5): btn(pg,'Correct' if i<4 else 'Incorrect'); pg.wait_for_timeout(30)
    r['res']=rows(pg); btn(pg,'Save assessment'); pg.wait_for_timeout(300); r['rec']=pg.evaluate('window.__done'); R['seq1']=r; b.close()
    # passage variants
    def pv(name, fn):
        b,pg=new(p); to_passage(pg); out=fn(pg); out['h2']=h2(pg)[:40]; R[name]=out; 
        pg.errors and out.setdefault('errors',pg.errors); b.close()
    def fin_res(pg,comp=5):
        o={}
        if 'Comprehension' in h2(pg):
            for i in range(5): btn(pg,'Correct' if i<comp else 'Incorrect'); pg.wait_for_timeout(20)
        o['res']={k:v for k,v in rows(pg).items() if 'Passage' in k or 'Overall' in k or 'band' in k or 'Comp' in k}; return o
    def a(pg):
        adv(pg,14900); o={'f149':btn(pg,'Child finished')}; o['still']= 'Passage' in h2(pg); o['note']=note(pg)[:100]; return o
    pv('finish_14.9s',a)
    def a2(pg):
        btn(pg,'Mark last word reached'); item(pg,51); adv(pg,15000); btn(pg,'Child finished'); o=fin_res(pg); return o
    pv('all52_at15s_cap',a2)
    def a3(pg):
        adv(pg,30000); btn(pg,'Child finished'); o={'ask':note(pg)[:150]}; btn(pg,'Read to the end'); o.update(fin_res(pg)); return o
    pv('finish30_readToEnd',a3)
    def a4(pg):
        adv(pg,30000); btn(pg,'Child finished'); btn(pg,'Stopped early',False); item(pg,9); o={'note':note(pg)[:120]}; btn(pg,'Child finished'); o.update(fin_res(pg)); return o
    pv('finish30_stoppedEarly_w9',a4)
    def a5(pg):
        adv(pg,60500); o={'note':note(pg)[:140]}; item(pg,19); o['after_tap']=note(pg)[:100]; o['score']=btn(pg,'Score it'); o.update(fin_res(pg)); return o
    pv('timeout_then_tap_w19',a5)
    def a6(pg):
        adv(pg,60500); btn(pg,'Mark last word reached'); o={'toggled_off':True}; item(pg,19); o['note']=note(pg)[:100]; o['score']=btn(pg,'Score it'); o['wrong_count']=pg.evaluate("document.querySelectorAll('#eg .item.wrong').length"); return o
    pv('timeout_press_markBtn_then_tap',a6)
    def a7(pg):
        # mark w=-? mark word 0 then 20s: cwpm
        item(pg,0); btn(pg,'Mark last word reached'); item(pg,0); adv(pg,20000); btn(pg,'Child finished'); o=fin_res(pg,0); return o
    pv('last_word0_wrong0',a7)
    def a8(pg):
        # teacher taps Skip when awaiting
        adv(pg,60500); btn(pg,'Skip'); o={'h2':h2(pg)}; o.update(fin_res(pg,None) if False else {}); return o
    pv('timeout_skip',a8)
json.dump(R,open('egra_t.json','w'),ensure_ascii=False,indent=1); print(json.dumps(R,ensure_ascii=False,indent=1))
