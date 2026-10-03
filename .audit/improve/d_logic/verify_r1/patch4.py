s=open('t4_ui.py').read()
a=s.index("        tiles = pg.query_selector_all('.choices .tile')"); b_=s.index("    pg.wait_for_timeout(500)\n    heading")
new='''        r = pg.evaluate("""([known, rv, dbl]) => { const tiles=[...document.querySelectorAll('.choices .tile')]; if(tiles.length<2) return null; const right=tiles.find(t=>t.dataset.right); if(!right) return null;
          if(tiles.some(t=>t.classList.contains('ok')||t.classList.contains('no'))) return {busy:1};
          const rt=right.textContent.trim().replace(/\\u0640/g,''); const K=new Set([...known]); const knows=[...rt].every(c=>K.has(c)||/[\\u064B-\\u0652\\u0670]/.test(c));
          const pick = knows? right : tiles[Math.floor(rv*tiles.length)]; const status=(document.querySelector('.score')||{}).textContent||'';
          pick.click(); if(dbl){ for(const t of tiles) t.click(); }
          return {rt, knows, correct: pick===right, status}; }""", [''.join(known), rnd.random(), dbl])
        if not r: stuck += 1; pg.wait_for_timeout(150)
        elif r.get('busy'): pg.wait_for_timeout(100)
        else:
            stuck = 0; nq += 1; log.append(r); pg.wait_for_timeout(560 if r['correct'] else 900)
        if stuck > 60: break
'''
s=s[:a]+new+s[b_:]
open('t4_ui.py','w').write(s)
