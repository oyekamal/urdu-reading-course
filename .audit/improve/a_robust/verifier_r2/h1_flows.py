from common import *
import sys, json
U = json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
L1 = ['Lalif', 'Lbe', 'Lkaf', 'Llam', 'Lmim', 'Lnun']
def mk(pg, done, passed0=True, extra_units=None):
    pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    units = {'0': {'passed': True, 'score': 10, 'total': 10, 'at': 1, 'lessons': {'rules': 1, 'done': 1}}, '1': {'lessons': {k: 1 for k in done}}}
    if extra_units: units.update(extra_units)
    pg.evaluate("p=>__put('progress',p)", {'id': pid, 'units': units}); pg.reload(); pg.wait_for_timeout(1800); return pid
def cur_btn(pg): click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(1000)
def prog(pg):
    c, d = counts(pg); return c, d
TIMES = [(0, 0, 0), (0, 100, 200), (0, 100, 200, 300), (0, 60, 150)]
def quiz_test(b, times):
    ctx, pg = newpage(b); quick_profile(pg, 'Q'); pid = mk(pg, L1 + ['marks', 'join', 'blend', 'W1', 'W2', 'W3', 'W4', 'read'])
    cur_btn(pg)
    n = pg.evaluate("""()=>{const lis=[...document.querySelectorAll('.lesson ol > li')]; lis.forEach(li=>{const rom=li.querySelector('b').innerText; [...li.querySelectorAll('.tile')].find(t=>t.getAttribute('aria-label')===rom).click()}); return lis.length}""")
    burst_sel(pg, ".lesson button.act", times); pg.wait_for_timeout(1500)
    c, d = counts(pg)
    q = len([a for a in d['attempts'] if a['drill'] == 'quiz'])
    out = {'questions': n, 'quiz attempts': q, 'cards': c['cards'], 'passed': [(u, v.get('passed')) for x in d['progress'] for u, v in x['units'].items()]}
    # Finish burst
    if pg.query_selector(".lesson button:has-text('Finish')"):
        burst_sel(pg, ".lesson button:has-text('Finish')", times); pg.wait_for_timeout(2500)
        c, d = counts(pg)
        out['finish pearls(unit1)'] = [sorted(v.get('lessons', {}).keys())[-2:] for x in d['progress'] for u, v in x['units'].items() if u == '1']
        out['celebrations'] = pg.evaluate("document.querySelectorAll('.celebrate').length")
        out['cel text'] = pg.evaluate("document.querySelector('.celebrate h1')?.innerText")
        # celebration button burst: expect return to path (Back to path) exactly once
        if pg.query_selector('.cel-go'):
            log = burst_sel(pg, '.cel-go', times); pg.wait_for_timeout(2000)
            out['after cel-go'] = pg.inner_text('#app')[:50].replace('\n', ' | '); out['active tab'] = pg.evaluate("document.querySelector('.bottom .active')?.dataset.k")
            out['cel-go taps landed on'] = [x[1] for x in log]
    out['errs'] = pg._errs[:2]; ctx.close(); return out
def dict_test(b, times, right):
    ctx, pg = newpage(b); quick_profile(pg, 'D'); pid = mk(pg, L1 + ['marks', 'join', 'blend'])
    cur_btn(pg)
    # words lesson 1: has dictation? find via text
    txt = pg.inner_text('#app')[:60].replace('\n', ' | ')
    return ctx, pg, txt
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        for t in TIMES:
            print('QUIZ', t, quiz_test(b, t), flush=True)
        b.close()
