#!/usr/bin/env python3
"""Hints: every letter x 4 forms. Truth = the glyph rendered in the browser (Noto Naskh AND Nastaliq) and counted as ink blobs:
body = biggest blob, the rest are marks (dots are small round blobs, tah/hamza are marks flagged in the data). Compares dotInfo() from content.js
and runs lineFor-equivalent claims through the real feel.js? (lineFor is private: tested by driving wrong taps in t1b)."""
import json, sys
from common import *
R = {}
with sync_playwright() as p:
    b, pg = bare(p)
    res = pg.evaluate("""async () => {
      const {loadContent, C, dotInfo, forms} = await import('/src/content.js'); await loadContent(); await document.fonts.load('60px "Noto Naskh Arabic"'); await document.fonts.load('60px "Noto Nastaliq Urdu"');
      const out = [];
      const cv = document.createElement('canvas'); cv.width = 260; cv.height = 260; const g = cv.getContext('2d', {willReadFrequently: true});
      function blobs(fam, text) { g.clearRect(0,0,260,260); g.fillStyle='#000'; g.font = '110px ' + fam; g.direction='rtl'; g.textAlign='center'; g.textBaseline='middle'; g.fillText(text,130,130);
        const d = g.getImageData(0,0,260,260).data, W=260, lab=new Int32Array(W*W); const sizes=[]; let id=0; const st=[];
        for (let i=0;i<W*W;i++){ if (d[i*4+3]<60||lab[i]) continue; id++; let n=0; st.push(i); lab[i]=id; while(st.length){ const q=st.pop(); n++; const x=q%W,y=(q/W)|0; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy; if(nx<0||ny<0||nx>=W||ny>=W)continue; const k=ny*W+nx; if(!lab[k]&&d[k*4+3]>=60){lab[k]=id;st.push(k);}}} sizes.push(n);} return sizes.sort((a,b)=>b-a); }
      for (const l of C.letters.letters) for (const [form, glyph] of forms(l)) { if (!glyph) continue; const info = dotInfo(l.ch, form);
        for (const fam of ['"Noto Naskh Arabic"', '"Noto Nastaliq Urdu"']) { const bl = blobs(fam, glyph); out.push({ch: l.ch, form, fam, info, blobs: bl}); } }
      return out; }""")
    # claims. Naskh draws every dot as its own blob, so blobs-1 must equal the claimed dot count (tah/hamza: exactly one separate mark).
    # Nastaliq fuses neighbouring dots into one stroke, so there only "has marks / has none" and ink growth with n can be checked.
    bad = []; checked = 0; WL = {('ہ', 'initial'), ('ہ', 'medial')}   # ہ initial/medial: the shaped glyph is two ink blobs, no dots
    byfam = {}
    for r in res: byfam[(r['fam'], r['ch'], r['form'])] = r
    for r in res:
        info = r['info']; checked += 1; extra = len(r['blobs']) - 1; want = info['n'] + (1 if info['mark'] else 0)
        if r['ch'] == 'گ' or (r['ch'], r['form']) in WL: continue          # گ: second bar of the gaf, not a dot
        if 'Naskh' in r['fam']:
            if extra != want: bad.append((r['ch'], r['form'], 'Naskh', info, r['blobs']))
        else:
            if (extra >= 1) != (want >= 1): bad.append((r['ch'], r['form'], 'Nastaliq', info, r['blobs']))
    R['checked_glyphs'] = checked; R['mismatches'] = bad
    R['letters'] = len({r['ch'] for r in res})
    b.close()
json.dump(R, open(HERE + '/t1_dots.json', 'w'), ensure_ascii=False, indent=1)
print('glyphs checked', R['checked_glyphs'], 'letters', R['letters'], 'mismatches', len(R['mismatches']))
for m in R['mismatches']: print(' ', m)
