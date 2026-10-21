#!/usr/bin/env python3
"""UI defect finder for the gauntlet loop: clipped/truncated text, sideways overflow, small tap targets, low contrast, at several widths.
  python3 tools/ui_defects.py <port> [outdir]      (dev server: npx vite --port 5189)
Writes <outdir>/defects.json and prints a summary. Exit 0 always; the loop reads the numbers."""
import sys, os, json
from playwright.sync_api import sync_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '5189'; OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/ur/ui'; os.makedirs(OUT, exist_ok=True)
SEED = """async n => { const db = await new Promise((r,j)=>{const q=indexedDB.open('urdu-reader'); q.onsuccess=()=>r(q.result); q.onerror=()=>j(q.error)});
 const all = (s)=>new Promise(r=>{const q=db.transaction(s).objectStore(s).getAll(); q.onsuccess=()=>r(q.result)});
 const p=(await all('profiles'))[0]; const units={}; for(let k=0;k<n;k++) units[k]={passed:true,score:10,total:10,at:Date.now()};
 await new Promise(r=>{const tx=db.transaction('progress','readwrite'); tx.objectStore('progress').put({id:p.id,units,wpm:[],sessions:0}); tx.oncomplete=r}); }"""
CHECK = r"""() => {
  const vw = innerWidth, out = [];
  const lum = c => { const f = v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4) }; return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]) };
  const rgba = s => { const m = s.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p = m[1].split(',').map(Number); return [p[0],p[1],p[2], p.length>3?p[3]:1] };
  const bgOf = el => { let n = el; let acc = null; while (n && n.nodeType===1) { const cs = getComputedStyle(n); if (cs.backgroundImage && cs.backgroundImage!=='none') return null; const c = rgba(cs.backgroundColor); if (c && c[3] > 0.95) return c; n = n.parentElement } return [255,255,255,1] };
  const desc = e => (e.tagName.toLowerCase() + (e.className && typeof e.className==='string' ? '.' + e.className.trim().split(/\s+/).slice(0,2).join('.') : '') + ' "' + (e.innerText||'').trim().replace(/\s+/g,' ').slice(0,28) + '"');
  const seen = new Set();
  const add = (kind, e, extra='') => { const k = kind + desc(e); if (seen.has(k)) return; seen.add(k); out.push(kind + ': ' + desc(e) + (extra? ' ('+extra+')':'')) };
  if (document.scrollingElement.scrollWidth > vw + 1) out.push('overflow-x: page scrolls sideways (' + document.scrollingElement.scrollWidth + ' > ' + vw + ')');
  document.querySelectorAll('body *').forEach(e => {
    const cs = getComputedStyle(e); if (cs.display==='none' || cs.visibility==='hidden' || +cs.opacity===0) return; const r = e.getBoundingClientRect(); if (r.width===0 || r.height===0) return;
    const hasText = [...e.childNodes].some(n => n.nodeType===3 && n.textContent.trim().length>1);
    if (hasText) {
      if (cs.textOverflow==='ellipsis' && e.scrollWidth > e.clientWidth + 1) add('truncated', e, 'ellipsis ' + e.scrollWidth + '>' + e.clientWidth);
      else if ((cs.overflowX==='hidden'||cs.overflowX==='clip') && e.scrollWidth > e.clientWidth + 2) add('clipped-x', e, e.scrollWidth + '>' + e.clientWidth);
      if ((cs.overflowY==='hidden'||cs.overflowY==='clip') && e.scrollHeight > e.clientHeight + 3 && e.clientHeight>0) add('clipped-y', e, e.scrollHeight + '>' + e.clientHeight);
      if (r.right > vw + 1 || r.left < -1) add('off-screen', e, Math.round(r.left) + '..' + Math.round(r.right));
      let a = e.parentElement; while (a && a!==document.body) { const ac = getComputedStyle(a); if (['hidden','clip'].includes(ac.overflowX) || ['hidden','clip'].includes(ac.overflowY)) { const ar = a.getBoundingClientRect(); if (r.left < ar.left - 1 || r.right > ar.right + 1) { add('outside-parent', e, 'text '+Math.round(r.left)+'..'+Math.round(r.right)+' vs box '+Math.round(ar.left)+'..'+Math.round(ar.right)); break } } a = a.parentElement }
      const fg = rgba(cs.color), bg = bgOf(e);
      if (fg && bg) { const comp = fg[3]<1 ? [0,1,2].map(i => fg[i]*fg[3]+bg[i]*(1-fg[3])) : fg; const L1 = lum(comp), L2 = lum(bg); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05); const big = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.66 && +cs.fontWeight >= 700); const need = big ? 3 : 4.5; if (ratio < need && r.bottom>0 && r.top<innerHeight) add('low-contrast', e, ratio.toFixed(1) + ':1 need ' + need) }
    }
    if (['BUTTON','A','INPUT','SELECT'].includes(e.tagName) && r.bottom>0 && r.top<innerHeight && (r.width < 40 || r.height < 40)) add('small-tap', e, Math.round(r.width) + 'x' + Math.round(r.height));
  });
  return out;
}"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ('light', 'dark'):
        for W in (360, 390, 412, 820, 1280):
            H = 844 if W < 500 else 1000
            ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme=scheme); pg = ctx.new_page(); pg.on("dialog", lambda d: d.accept()); screens = {}
            try:
                pg.goto(f"http://localhost:{PORT}/?skiponb"); pg.wait_for_timeout(2000)
                pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.wait_for_timeout(300)
                pg.fill("input[placeholder=Name]", "Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(2200)
                pg.evaluate(SEED, 3); pg.reload(); pg.wait_for_timeout(3000)
                def grab(name): pg.wait_for_timeout(1800); screens[name] = pg.evaluate(CHECK)
                grab('learn'); pg.mouse.wheel(0, 700); pg.wait_for_timeout(500); grab('learn-units')
                for t in ('Review', 'Read', 'Me'):
                    pg.click(f".bottom button:has-text('{t}')"); grab(t.lower())
                pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(700); pg.evaluate("window.scrollTo(0,0)")
                pg.click(".btn-primary.btn-wide"); grab('lesson-1')
                for i in range(3):
                    c = pg.query_selector("button:has-text('Continue')")
                    if not c: break
                    c.click(); pg.wait_for_timeout(600)
                grab('lesson-steps')
            except Exception as e: screens['ERROR'] = [str(e)[:120]]
            res[f"{scheme}-{W}"] = screens; ctx.close()
    b.close()
json.dump(res, open(f"{OUT}/defects.json", "w"), indent=1, ensure_ascii=False)
tot = {}
for k, sc in res.items():
    for n, items in sc.items():
        for it in items: tot[it.split(':')[0]] = tot.get(it.split(':')[0], 0) + 1
print('defect counts (summed over widths/screens/schemes):', tot)
