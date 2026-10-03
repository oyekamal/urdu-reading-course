import sys, json, os, random
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5460/?skiponb'
from playwright.sync_api import sync_playwright
R={'hints':[], 'steps':[]}
DB="async(a)=>{const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; return await (async()=>{%s})()}"
def cards(pg): return pg.evaluate(DB%"return (await db.by('cards','profileId',prof.id)).map(c=>({item:c.item,box:c.box,due:c.due,seen:c.seen,lastOk:c.lastOk,lastMiss:c.lastMiss,kind:c.kind}))")
def attempts(pg): return pg.evaluate(DB%"return (await db.by('attempts','profileId',prof.id)).map(c=>({drill:c.drill,item:c.item,correct:c.correct}))")
with sync_playwright() as p:
    b,pg=h.fresh2(p,'Flow'); h.tamper(pg,0,{})
    now=pg.evaluate("Date.now()")
    pg.evaluate("""async()=>{const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const d=86400000;
      for (const [it,box,days] of [['ب',4,8],['ک',3,4],['ل',5,16],['ا',2,2]]) await db.put('cards',{id:prof.id+':'+it,profileId:prof.id,item:it,kind:'letter',box,due:Date.now()+days*d,seen:3}); }""")
    before={c['item']:c for c in cards(pg)}; R['before']=before
    pg.reload(); pg.wait_for_timeout(2500)
    wrong_taps=[]; right_taps=0
    pg.keyboard.press('Escape'); pg.evaluate("document.querySelectorAll('.stk-ov').forEach(e=>{const b=e.querySelector('button'); b?b.click():e.remove()})"); pg.wait_for_timeout(600); pg.evaluate("document.querySelector('.tc-go').click()"); pg.wait_for_timeout(800)
    for step in range(220):
        pg.wait_for_timeout(120)
        if pg.evaluate("!!document.querySelector('.celebrate')"):
            R['steps'].append('celebrate'); pg.evaluate("document.querySelector('.cel-go')?.click()"); pg.wait_for_timeout(500); 
            if len(R['steps'])>=4: break
            continue
        info=pg.evaluate("""()=>{const l=document.querySelector('.lesson'); if(!l) return {gone:true}; const t=[...document.querySelectorAll('.lesson .tile')]; const right=t.filter(x=>x.dataset.right&&!x.classList.contains('ok')&&!x.classList.contains('no')); 
          const prim=[...document.querySelectorAll('.lesson button.btn-primary')].filter(b=>!b.disabled&&b.offsetParent); return {h:document.querySelector('.lesson h1')?.textContent, nright:right.length, ntile:t.length, prim:prim.map(b=>b.textContent.trim()), q:document.querySelector('.lesson .q')?.textContent||''}}""")
        if info.get('gone'): break
        if info['nright'] and info['ntile']:
            # first tile question in the flow: tap a wrong tile for the first 2 questions, then the right one
            if len(wrong_taps)<2:
                res=pg.evaluate("""()=>{const t=[...document.querySelectorAll('.lesson .tile')]; const w=t.find(x=>!x.dataset.right&&!x.classList.contains('no')&&!x.classList.contains('ok')); if(!w) return null; const r=t.find(x=>x.dataset.right); w.click(); return {tapped:w.textContent, answer:r.textContent, key:r.dataset.right}}""")
                if res:
                    pg.wait_for_timeout(400); say=pg.evaluate("document.querySelector('.feel-say')?.textContent||''"); res['hint']=say; wrong_taps.append(res); R['hints'].append(res); continue
            pg.evaluate("document.querySelector('.lesson .tile[data-right]:not(.ok)')?.click()"); right_taps+=1; pg.wait_for_timeout(300); continue
        if info['prim']:
            pg.evaluate("[...document.querySelectorAll('.lesson button.btn-primary')].find(b=>!b.disabled&&b.offsetParent).click()"); continue
        # else something else: try Skip or any enabled button
        pg.wait_for_timeout(300)
    R['wrong_taps']=wrong_taps; R['right_taps']=right_taps
    after={c['item']:c for c in cards(pg)}; R['after']=after; R['attempts']=attempts(pg)
    R['errors']=h.real_errors(pg); R['url_h1']=pg.evaluate("document.querySelector('h1')?.textContent")
    b.close()
json.dump(R,open('flow.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:R[k] for k in ('hints','wrong_taps','right_taps','errors','steps','url_h1')},ensure_ascii=False,indent=1))
print('before',{k:(v['box'],round((v['due']-now)/86400000,2)) for k,v in R['before'].items()})
print('after',{k:(v['box'],round((v['due']-now)/86400000,2),v.get('lastOk')) for k,v in R['after'].items()})
print(R['attempts'][:40])
