#!/usr/bin/env python3
"""Real feel.js hint path: for every letter x every position x several tapped (wrong) tiles, build a tile row, flag a wrong tap and read the
bubble the child sees. Each claim is checked against the rendered glyph (Naskh): dots counted as ink blobs, position from blob centroid vs body."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = fresh(p)
    out = pg.evaluate("""async () => {
      const {C, forms, loadContent} = await import('/src/content.js'); await loadContent(); await document.fonts.load('60px "Noto Naskh Arabic"');
      const cv = document.createElement('canvas'); cv.width = 260; cv.height = 260; const g = cv.getContext('2d', {willReadFrequently: true});
      function parts(text) { g.clearRect(0,0,260,260); g.fillStyle='#000'; g.font='110px "Noto Naskh Arabic"'; g.direction='rtl'; g.textAlign='center'; g.textBaseline='middle'; g.fillText(text,130,130);
        const d=g.getImageData(0,0,260,260).data,W=260,lab=new Int32Array(W*W),bl=[],st=[]; let id=0;
        for(let i=0;i<W*W;i++){ if(d[i*4+3]<60||lab[i])continue; id++; let n=0,sy=0; st.push(i); lab[i]=id; while(st.length){const q=st.pop(); n++; const x=q%W,y=(q/W)|0; sy+=y; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy; if(nx<0||ny<0||nx>=W||ny>=W)continue; const k=ny*W+nx; if(!lab[k]&&d[k*4+3]>=60){lab[k]=id;st.push(k);}}} bl.push({n, cy: sy/n}); }
        bl.sort((a,b)=>b.n-a.n); return bl; }
      const letters = C.letters.letters; const rows = [];
      const host = document.createElement('div'); document.body.append(host);
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      for (const t of letters) for (const [form, glyph] of forms(t)) { if (!glyph) continue;
        const others = [...new Set([...(t.confusable || []), ...letters.filter(() => rnd() < 0.12).map(l => l.ch)])].filter(c => c !== t.ch && C.by[c]).slice(0, 5);
        for (const o of others) { const pf = forms(C.by[o]).find(x => x[0] === form && x[1]); if (!pf) continue;   // same position for both tiles, as in the lesson quick check
          host.innerHTML = ''; const row = document.createElement('div'); row.className = 'choices'; const a = document.createElement('button'), bt = document.createElement('button'); a.className = 'tile ur'; bt.className = 'tile ur'; a.textContent = glyph; bt.textContent = pf[1]; a.dataset.right = 'names/' + t.id; row.append(a, bt); host.append(row);
          bt.classList.add('no'); await sleep(30); const say = document.querySelector('.feel-say'); const txt = say ? say.textContent : null; document.querySelectorAll('.feel-say').forEach(x => x.remove());
          const bl = parts(glyph); rows.push({ch: t.ch, form, tapped: o, glyph, txt, blobs: bl.length, bodyCy: bl[0].cy, smallCy: bl.slice(1).map(x => x.cy)}); } }
      return rows; }""")
    bad = []; kinds = {}
    NUM = {'one': 1, 'two': 2, 'three': 3}
    for r in out:
        t = r['txt'] or ''; extra = r['blobs'] - 1
        if r['ch'] == 'گ' or (r['ch'] == 'ہ' and r['form'] in ('initial', 'medial')): continue
        m = re.match(r'Count the dots: (\S+) has (one|two|three)$', t)
        if m: kinds['count'] = kinds.get('count', 0) + 1; ok = extra == NUM[m.group(2)] and m.group(1) == r['glyph']
        elif t.startswith('Look for the little ط on'): kinds['tah'] = kinds.get('tah', 0) + 1; ok = r['ch'] in 'ٹڈڑ' and extra == 1 and t.endswith(r['glyph'])
        elif t.startswith('Look for the little ء on'): kinds['hamza'] = kinds.get('hamza', 0) + 1; ok = r['ch'] == 'ئ' and extra == 1
        elif t.endswith('no dots!'): kinds['nodots'] = kinds.get('nodots', 0) + 1; ok = extra == 0
        else:
            m2 = re.match(r'Look where the dot sits: (\S+) has (one|two|three) (above|below)$', t)
            if m2: kinds['where'] = kinds.get('where', 0) + 1; ab = 'above' if sum(r['smallCy']) / len(r['smallCy']) < r['bodyCy'] else 'below'; ok = extra == NUM[m2.group(2)] and ab == m2.group(3)
            elif t.startswith('Listen again: this is'): kinds['listen'] = kinds.get('listen', 0) + 1; ok = True
            else: kinds['other:' + t[:30]] = kinds.get('other:' + t[:30], 0) + 1; ok = t.startswith('Almost') is False and False
        if not ok: bad.append((r['ch'], r['form'], r['tapped'], t, r['blobs']))
    R = {'cases': len(out), 'kinds': kinds, 'false_or_odd_claims': bad[:40], 'n_bad': len(bad), 'page_errors': pg.errors}
    b.close()
json.dump(R, open(HERE + '/t1b_hints.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1)[:3000])
