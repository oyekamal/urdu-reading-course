import json, re, h, sys
from playwright.sync_api import sync_playwright
truth = json.load(open('t1_truth.json')); TAT='ـ'
def gf(t):
    t=t.strip(); lead=t.startswith(TAT); trail=len(t)>1 and t.endswith(TAT); ch=t.replace(TAT,'')
    return ch, ('medial' if lead and trail else 'final' if lead else 'initial' if trail else 'isolated')
NUM={'one':1,'two':2,'three':3}
def verdict(good_txt, hint):
    ch,f=gf(good_txt); t=truth.get(f'{ch}|{f}'); 
    if t is None: return 'no truth'
    mark='tah' if ch in 'ٹڈڑ' else 'hamza' if ch=='ئ' else None; n=0 if mark=='hamza' else t['n']
    m=re.search(r'has (one|two|three)( above| below)?$',hint)
    if hint.startswith(('Count the dots','Look where')):
        if not m: return 'unparsed'
        if NUM[m.group(1)]!=n or mark: return f'FALSE dots claim ({hint}) truth n={n} {t["pos"]}'
        if m.group(2) and m.group(2).strip()!=t['pos']: return f'FALSE pos ({hint}) truth {t["pos"]}'
    elif 'no dots' in hint:
        if n or mark: return f'FALSE no-dots ({hint})'
    elif 'little ط' in hint:
        if mark!='tah': return 'FALSE tah'
    elif 'little ء' in hint:
        if mark!='hamza': return 'FALSE hamza'
    elif not hint.startswith(('Listen again','Almost')): return 'unknown '+hint
    return None
ONE=False
BUDGET=10**9
def step_once(pg, letter, log):
    tiles = pg.query_selector_all('.lesson .choices .tile')
    right = [t for t in tiles if t.get_attribute('data-right')]
    if len(tiles) > 1 and right and not any('ok' in (t.get_attribute('class') or '').split() for t in tiles):
        good = right[0]; gt = good.inner_text()
        for t in tiles:
            if t is good: continue
            if 'no' in (t.get_attribute('class') or '').split(): continue
            global BUDGET
            if BUDGET<=0: break
            BUDGET-=1
            t.click(); pg.wait_for_timeout(180)
            s = pg.query_selector('.feel-say'); hint = s.inner_text() if s else None
            log.append({'letter': letter, 'good': gt, 'tapped': t.inner_text(), 'hint': hint, 'verdict': verdict(gt, hint) if hint else 'NO HINT SHOWN'})
            if ONE: break
        good.click(); pg.wait_for_timeout(700); return
    if len(tiles) > 1 and not right and not pg.evaluate("(document.querySelector('.lesson .score')?.textContent||'').trim()") and pg.evaluate("!!document.querySelector('.lesson .say-row')"):
        tiles[0].click(); pg.wait_for_timeout(500); return
    if pg.query_selector('.celebrate'): raise StopIteration
    prim = pg.evaluate_handle("[...document.querySelectorAll('.lesson button.btn-primary')].filter(b=>b.offsetParent&&!b.disabled).slice(-1)[0]||null").as_element()
    if prim: prim.click()
    pg.wait_for_timeout(300)
def run_letter(p, letter, log):
    b, pg = h.fresh2(p, 'T'+str(abs(hash(letter))%99))
    info = pg.evaluate("""async(c)=>{const {C,loadContent}=await import('/src/content.js');await loadContent();const u=C.units.find(x=>x.letters.includes(c));return {n:u.n,before:u.letters.slice(0,u.letters.indexOf(c)).map(x=>'L'+C.by[x].id)}}""", letter)
    h.tamper(pg, info['n']-1, {str(info['n']): info['before']} if info['before'] else {})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(900)
    title = pg.inner_text('h1')
    for k in range(70):
        try: step_once(pg, letter, log)
        except StopIteration: break
        except Exception as ex: pg.wait_for_timeout(300)
    errs = h.real_errors(pg); b.close(); return title, errs
if __name__ == '__main__':
    letters = sys.argv[1:] or ['ٹ','ڈ','ڑ','ئ','ی','ں','ب','ث','ج','گ','ہ','ھ','ن','ت']
    log = []; E={}
    with sync_playwright() as p:
        for l in letters:
            try: t, e = run_letter(p, l, log); E[l]=(t,e)
            except Exception as ex: E[l]=('EXC '+str(ex)[:150],[])
    h.save('t1_real.json', {'log': log, 'letters': E})
    bad = [x for x in log if x['verdict']]
    print('hints seen', len(log), 'bad', len(bad)); 
    for x in bad[:30]: print(x)
    print({k:v for k,v in E.items()})
    from collections import Counter; print(Counter((x['hint'] or '')[:12] for x in log))
