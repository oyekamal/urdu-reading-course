# Backup import: corrupt / hostile / forged files, PIN + mode overwrite, atomicity, restore on the first screen. Expect PASS on every line.
from common import *
import tempfile, json
RES = []
def chk(name, ok, extra=''):
    RES.append(ok); print(('PASS ' if ok else 'FAIL ') + name, extra)
def settings(pg): return {s['key']: s['value'] for s in pg.evaluate('__dump()')['settings']}
def import_text(pg, text, name='b.json'):
    """drive the real file input through the UI of the current screen"""
    p = tempfile.mktemp(suffix='.json'); open(p, 'w').write(text)
    with pg.expect_file_chooser(timeout=6000) as fc:
        pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>/Restore from a backup|Import a backup/.test(b.innerText)); b.click()}")
    fc.value.set_files(p); pg.wait_for_timeout(1500)
    return pg.evaluate("document.getElementById('toast')?.textContent")
def gate_pass(pg):
    """solve the grown-up gate from the digits shown in the English words"""
    pg.wait_for_selector('.gate-sheet', timeout=4000)
    words = pg.inner_text('.gate-en').strip()
    ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']; TEENS = ['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']; TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    n = None
    for i in range(10, 100):
        w = TEENS[i-10] if i < 20 else TENS[i//10] + ('-' + ONES[i%10] if i % 10 else '')
        if w == words: n = i
    pg.fill('#gate-input', str(n)); pg.evaluate("()=>document.querySelector('.gate-ok').click()"); pg.wait_for_timeout(500)
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ---- fresh device: first screen offers restore (welcome) and the mode picker offers it too
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
        chk('welcome screen has Restore from a backup', pg.evaluate("[...document.querySelectorAll('button')].some(b=>/Restore from a backup/.test(b.innerText))"))
        good = {'format': 'urdu-qaida-backup', 'version': 1, 'exportedAt': '2026-10-03T00:00:00Z', 'profiles': [{'id': 'p1', 'name': 'Amal', 'kind': 'learner', 'track': 'child', 'avatar': '#1E9C8F', 'createdAt': 1, 'updatedAt': 5}],
                'attempts': [{'id': 'a1', 'profileId': 'p1', 'unit': 1, 'drill': 'tell', 'item': 'ا', 'correct': True, 'ms': 100, 'ts': 10, 'updatedAt': 5}],
                'cards': [{'id': 'p1:ا', 'profileId': 'p1', 'item': 'ا', 'kind': 'letter', 'box': 2, 'due': 5, 'seen': 1, 'updatedAt': 5}], 'sessions': [], 'assessments': [],
                'progress': [{'id': 'p1', 'units': {'0': {'passed': True, 'score': 10, 'total': 10, 'at': 3, 'lessons': {'rules': 3}}}, 'wpm': [], 'sessions': 1, 'updatedAt': 5}],
                'settings': [{'key': 'mode', 'value': 'school', 'updatedAt': 99999999999999}, {'key': 'teacherPin', 'value': '0000', 'updatedAt': 99999999999999}, {'key': 'ui', 'value': {'style': 'nastaliq'}, 'updatedAt': 7}]}
        t = import_text(pg, json.dumps(good)); print('toast:', t)
        c, d = counts(pg); st = settings(pg)
        chk('good backup restored on a fresh phone', c['profiles'] == 1 and c['attempts'] == 1 and c['cards'] == 1 and c['progress'] == 1, c)
        chk('forged mode/teacherPin in settings NOT imported', st.get('teacherPin') is None and st.get('mode') != 'school', {k: v for k, v in st.items() if k in ('mode', 'teacherPin')})
        chk('ui preference imported', (st.get('ui') or {}).get('style') == 'nastaliq')
        pg.wait_for_timeout(1500); print('screen after restore:', pg.inner_text('#app')[:60].replace('\n', ' | '))
        chk('app opens the restored learner (not a hang)', 'Amal' in pg.inner_text('#app'))
        ctx.close()
        # ---- populated device (Me tab): hostile files, each must be rejected with a message and change NOTHING
        ctx, pg = newpage(b); quick_profile(pg, 'Zed'); nav(pg, 'me')
        pg.evaluate("__put('settings',{key:'teacherPin',value:'4321'})"); pg.evaluate("__put('settings',{key:'mode',value:'family'})")
        before = counts(pg)[0]
        # file chooser opens from the input click after the gate; drive it by intercepting
        def run(label, text):
            nav(pg, 'me')
            pg.evaluate("()=>{const t=document.getElementById('toast'); if(t) t.textContent=''}")
            pth = tempfile.mktemp(suffix='.json'); open(pth, 'w').write(text)
            with pg.expect_file_chooser(timeout=8000) as fc:
                pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup|Restore from a backup/.test(b.innerText)).click()"); gate_pass(pg)
            fc.value.set_files(pth); pg.wait_for_timeout(1500)
            return pg.evaluate("document.getElementById('toast')?.textContent")
        T = lambda s: json.dumps(s)
        cases = [
            ('corrupt json', '{not json'),
            ('array root', '[1,2,3]'),
            ('null profile entry', T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [None]})),
            ('wrong format', T({'format': 'evil', 'version': 1, 'profiles': []})),
            ('future version', T({'format': 'urdu-qaida-backup', 'version': 99, 'profiles': []})),
            ('profiles not a list', T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': 'x'})),
            ('profile bad id type', T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [{'id': {'a': 1}, 'name': 'x'}]})),
            ('attempt missing profileId', T({'format': 'urdu-qaida-backup', 'version': 1, 'attempts': [{'id': 'z', 'ts': 1}]})),
            ('too many profiles', T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [{'id': 'p%d' % i, 'name': 'n'} for i in range(500)]})),
            ('not a backup at all', T({'hello': 'world'})),
        ]
        for label, text in cases:
            t = run(label, text); after = counts(pg)[0]; st = settings(pg)
            chk(f'rejected: {label}', after == before and st.get('teacherPin') == '4321' and st.get('mode') == 'family' and bool(t), f'toast={t!r}')
        # huge file
        big = '{"format":"urdu-qaida-backup","version":1,"profiles":[],"pad":"' + 'x' * (9 * 1024 * 1024) + '"}'
        t = run('huge', big); chk('rejected: 9 MB file', counts(pg)[0] == before and bool(t), f'toast={t!r}')
        # atomic: second record invalid -> first must not be written
        atom = T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [{'id': 'ok1', 'name': 'Good'}, {'id': 'bad1', 'name': 5}]})
        t = run('atomic', atom); chk('atomic: valid + invalid record -> nothing written', counts(pg)[0] == before, f'toast={t!r}')
        # PIN overwrite attempt hidden in a settings-only file + valid profile
        forged = T({'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [{'id': 'p9', 'name': '<img src=x onerror=alert(1)>', 'avatar': '#fff" onmouseover="x', 'track': 'child'}], 'settings': [{'key': 'teacherPin', 'value': '0000', 'updatedAt': 99999999999999}, {'key': 'mode', 'value': 'school', 'updatedAt': 99999999999999}, {'key': 'activeProfile', 'value': 'p9', 'updatedAt': 99999999999999}, {'key': 'deviceId', 'value': 'x', 'updatedAt': 99999999999999}, {'key': 'ui', 'value': {'scale': '1.5', 'evil': '<script>'}, 'updatedAt': 99999999999999}]})
        t = run('forged', forged); st = settings(pg); d = pg.evaluate('__dump()')
        chk('forged PIN/mode/activeProfile/deviceId untouched', st.get('teacherPin') == '4321' and st.get('mode') == 'family' and st.get('activeProfile') != 'p9', {k: st.get(k) for k in ('teacherPin', 'mode', 'activeProfile')})
        prof = [x for x in d['profiles'] if x['id'] == 'p9']
        chk('hostile name sanitised, bad avatar dropped', prof and '<' not in prof[0]['name'] and not prof[0].get('avatar'), prof)
        ui = st.get('ui') or {}
        chk('ui keys whitelisted', 'evil' not in ui, ui)
        chk('future updatedAt clamped', all(x['updatedAt'] < 4e12 for x in d['profiles'] if x['id'] == 'p9'))
        print('page errors:', pg._errs)
        ctx.close(); b.close()
    print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
main()
