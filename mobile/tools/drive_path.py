import json, re, sys
from playwright.sync_api import sync_playwright
L=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/data/letters.json',encoding='utf8'))['letters']
byid={l['id']:l for l in L}; byname={l['name']:l for l in L}; bych={l['ch']:l for l in L}
U=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/data/units.json',encoding='utf8'))['units']
TAT='ـ'
def formof(l,pos): return {'isolated':l['ch'],'initial':l['ch']+TAT if l['joiner'] else None,'medial':TAT+l['ch']+TAT if l['joiner'] else None,'final':TAT+l['ch']}[pos]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":800}); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e.stack)[:400])); pg.on("dialog", lambda d: d.accept())
    pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__last=this.src;return _p.call(this)}")
    js=lambda h: pg.evaluate("e=>e.click()", h)
    def last(): return (pg.evaluate("window.__last||''")).split('/audio/')[-1].replace('.mp3','')
    pg.goto("http://localhost:5179/"); pg.wait_for_timeout(1800); pg.click("text=Just me"); pg.wait_for_timeout(400); pg.click("text=+ Add a learner"); pg.wait_for_timeout(300); pg.fill("input[placeholder=Name]","Zee"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
    def answer_once():
        tiles=pg.query_selector_all(".choices .tile:not([disabled])")
        if not tiles: return False
        texts=[t.inner_text().strip() for t in tiles]
        q=(pg.query_selector(".card p.muted") or pg.query_selector(".card div:not(.choices)"))
        qt=pg.evaluate("()=>{const c=document.querySelector('.choices');return c?c.parentElement.innerText:''}")
        key=last(); kind,_,id_=key.partition('/')
        target=None
        m=re.search(r"Which is (.+?) at the (\w+) position", qt)
        if m and m.group(1) in byname: target=formof(byname[m.group(1)], m.group(2))
        elif re.search(r"Tap (\S+)\s*$", qt.split('\n')[-1] if qt else '') and not 'hear' in qt:
            n=re.search(r"Tap (.+?)\s*$", [x for x in qt.split('\n') if x.startswith('Tap ')][-1]).group(1).strip(); target=byname[n]['ch'] if n in byname else None
        if target is None:
            if kind=='names' and id_ in byid: target=byid[id_]['ch']
            elif kind=='syllables': lid,_,v=id_.rpartition('_'); target=byid[lid]['ch']+{'a':'ا','i':'ی','u':'و'}[v]
            elif kind=='sight': target=L and json.load(open('/home/oye/Documents/free_work/urdu-reading-course/data/letters.json',encoding='utf8'))['sight_words'][int(id_)]
            elif kind=='units':
                un,_,wi=id_.partition('_'); w=U[int(un[1:])]['words'][int(wi)]; target=w[0]
                # quiz asks by roman: choices show vowelled or bare
                for t,tx in zip(tiles,texts):
                    if tx in (w[0], w[3] if len(w)>3 else w[0]): js(t); return True
        # word-builder: 'Make: <rom>' -> find the word by romanisation
        mk=re.search(r"Make:\s*(\S+)", qt)
        if mk:
            rom=mk.group(1)
            for u in U:
                for w in u['words']:
                    if w[1]==rom and sorted(list(w[0]))==sorted(texts): target=w[0]
        if target and len(target)>=3 and all(len(tx)==1 for tx in texts) and sorted(texts)==sorted(list(target)):
            for ch in target:
                for t in pg.query_selector_all(".choices .tile:not([disabled])"):
                    if t.inner_text().strip()==ch: js(t); pg.wait_for_timeout(80); break
            return True
        for t,tx in zip(tiles,texts):
            if tx==target: js(t); return True
        js(tiles[0]); return True
    def answer_quiz():
        for li in pg.query_selector_all("ol li"):
            m=re.search(r"Which one says (\S+)", li.inner_text())
            if not m: continue
            rom=m.group(1)
            for u in U:
                for w in u['words']:
                    if w[1]==rom:
                        for t in li.query_selector_all(".tile"):
                            if t.inner_text().strip() in (w[0], w[3] if len(w)>3 else w[0]): js(t); break
        sub=pg.query_selector("button:has-text('Submit')")
        if sub: js(sub); pg.wait_for_timeout(800)
    def run_lesson(maxsteps=14):
        out=[]
        for step in range(maxsteps):
            h2=pg.query_selector("#app h2"); title=h2.inner_text() if h2 else "?"
            for r in range(40):
                if pg.query_selector(".btn-primary.btn-wide"): break
                if pg.query_selector("ol li .tile"): answer_quiz(); continue
                if pg.query_selector("h2:has-text('Dictation')") and pg.query_selector("button:has-text('Skip')"):
                    # dictation: type the word using keys
                    key=last(); un,_,wi=key.split('/')[-1].partition('_'); w=U[int(un[1:])]['words'][int(wi)][0]
                    for ch in w:
                        for k in pg.query_selector_all(".keys .tile"):
                            if k.inner_text().strip()==ch: js(k); break
                    js(pg.query_selector("button:has-text('Check')")); pg.wait_for_timeout(1000); continue
                if not answer_once():
                    sub=pg.query_selector("button:has-text('Submit')") or pg.query_selector("button:has-text('Next word')")
                    if sub: js(sub); pg.wait_for_timeout(400); continue
                    break
                pg.wait_for_timeout(560)
            c=pg.query_selector(".btn-primary.btn-wide")
            if c and c.inner_text().strip()=='Submit': answer_quiz(); pg.wait_for_timeout(600); c=[x for x in pg.query_selector_all('.btn-primary.btn-wide') if x.inner_text().strip()!='Submit']; c=c[0] if c else None
            if not c: out.append(title+" (stuck)"); break
            label=c.inner_text(); out.append(f"{title} -> {label}"); js(c); pg.wait_for_timeout(600)
            if label.startswith("Back to path") or label.startswith("Next:"): break
        return out
    js(pg.query_selector("button:has-text('Start:')")); pg.wait_for_timeout(600)
    for k in range(3): run_lesson()
    js(pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1000); js(pg.query_selector("button:has-text('Start:')")); pg.wait_for_timeout(900)
    for n in ["alif","be","kaf","lam","mim","nun","join","blend","words1","words2","read","check"]:
        if pg.query_selector("button:has-text('Continue:')") and not pg.query_selector("#app h2"): js(pg.query_selector("button:has-text('Continue:')")); pg.wait_for_timeout(800)
        r=run_lesson(16); print(f"{n}:", r[-2:])
        if r and "stuck" in r[-1]: pg.screenshot(path=f"stuck_{n}.png", full_page=True); print(pg.inner_text("#app")[:300]); break
    js(pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1200); pg.screenshot(path="p4_path_after.png", full_page=True); print("path:", pg.inner_text("#app")[:400].replace("\n"," | "))
    print("errors:", errs[:3]); b.close()
