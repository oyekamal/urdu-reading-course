import json, re, h
from playwright.sync_api import sync_playwright
truth = json.load(open('t1_truth.json'))
JS = '''async () => {
 const Cn = await import('/src/content.js'); await Cn.loadContent(); const C = Cn.C;
 document.querySelectorAll('.lesson').forEach(x=>x.remove());
 const les = document.createElement('div'); les.className='lesson'; les.innerHTML='<div class="row"><div><h1>x</h1></div></div><div class="pg-wrap"><div class="progress"><i></i></div></div><div class="choices"></div>'; document.body.append(les);
 await new Promise(r=>setTimeout(r,50));
 const ch = les.querySelector('.choices'); const tick=()=>new Promise(r=>setTimeout(r,0));
 const glyphs=[]; for(const l of C.letters.letters) for(const [f,g] of Cn.forms(l)) if(g) glyphs.push({ch:l.ch,form:f,g});
 const res=[];
 for(const G of glyphs){
   const wr = glyphs.filter(x=>x!==G && (x.form===G.form || x.ch===G.ch));
   for(const W of wr){
     ch.innerHTML=''; const a=document.createElement('button'); a.className='tile ur'; a.textContent=G.g; a.dataset.right='names/'+C.by[G.ch].id; const b=document.createElement('button'); b.className='tile ur'; b.textContent=W.g; ch.append(a,b);
     await tick(); b.classList.add('no'); await tick(); await tick();
     const s=document.querySelector('.feel-say'); res.push({good:G.ch,gform:G.form,gg:G.g,wrong:W.ch,wform:W.form,wg:W.g,hint:s?s.textContent:null});
     document.querySelectorAll('.feel-say').forEach(x=>x.remove());
   } }
 return res; }'''
with sync_playwright() as p:
    b, pg = h.bare(p); r = pg.evaluate(JS); print(len(r), 'cases'); print('errors', set(h.real_errors(pg))); b.close()
h.save('t1_hints_raw.json', r)
NUM={'one':1,'two':2,'three':3}
bad={}; kinds={}
names=None
for c in r:
    t = truth[f"{c['good']}|{c['gform']}"]; hint=c['hint']; key=(c['good'],c['gform'])
    mark = 'tah' if c['good'] in 'ٹڈڑ' else 'hamza' if c['good']=='ئ' else None
    n = 0 if mark=='hamza' else t['n']
    why=None
    if hint is None: why='no hint shown'
    else:
        m=re.search(r'has (one|two|three)( above| below)?$',hint)
        if hint.startswith('Count the dots') or hint.startswith('Look where'):
            kinds['dots']=kinds.get('dots',0)+1
            if not m: why='unparsed '+hint
            else:
                k=NUM[m.group(1)]; pos=(m.group(2) or '').strip()
                if k!=n: why=f'claims {k} dots, glyph has {n}'
                elif pos and pos!=t['pos']: why=f'claims {pos}, glyph {t["pos"]}'
                if mark and not why: why='dot claim on mark glyph'
        elif 'no dots' in hint:
            kinds['nodots']=kinds.get('nodots',0)+1
            if n!=0 or mark: why='claims no dots but glyph has dots/mark'
        elif 'little ط' in hint:
            kinds['tah']=kinds.get('tah',0)+1
            if mark!='tah': why='tah claim on non-tah'
        elif 'little ء' in hint:
            kinds['hamza']=kinds.get('hamza',0)+1
            if mark!='hamza': why='hamza claim on non-hamza'
        elif hint.startswith('Listen again') or hint.startswith('Almost'): kinds['generic']=kinds.get('generic',0)+1
        else: why='unknown hint '+hint
        if 'wrong' in hint.lower() or 'no!' in hint.lower().replace('no dots!',''): why=(why or '')+' unkind'
    if why: bad.setdefault((why.split(',')[0] if False else why, c['good'],c['gform']),[]).append((c['wrong'],c['wform'],hint))
print(kinds)
print('bad glyph-keys', len(bad))
for k,v in list(bad.items())[:60]: print(k, len(v), v[0])
json.dump([[list(k),v[:3]] for k,v in bad.items()], open('t1_hints_bad.json','w'), ensure_ascii=False, indent=1)
