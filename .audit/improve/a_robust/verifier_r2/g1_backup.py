from common import *
import sys, json, tempfile, os
NOW = 1760000000000
def good(**kw):
    d = {'format': 'urdu-qaida-backup', 'version': 1, 'exportedAt': '2026-10-03T00:00:00Z', 'profiles': [], 'attempts': [], 'cards': [], 'sessions': [], 'progress': [], 'assessments': [], 'settings': []}
    d.update(kw); return d
P = lambda i='p1', name='Amal', **k: dict({'id': i, 'name': name, 'kind': 'learner', 'track': 'child', 'grade': 2, 'createdAt': 5, 'updatedAt': 100}, **k)
CASES = {}
CASES['ok_min'] = good(profiles=[P()])
CASES['legacy_noformat'] = {'exportedAt': '2026-01-01', 'profiles': [P()]}
CASES['legacy_noexported'] = {'profiles': [P()]}
CASES['wrong_format'] = good(format='other')
CASES['future_version'] = good(version=2)
CASES['version_str'] = good(version='1')
CASES['array_top'] = [1, 2]
CASES['null_top'] = None
CASES['proto_top'] = json.loads('{"format":"urdu-qaida-backup","version":1,"__proto__":{"polluted":1},"profiles":[{"id":"p1","name":"A","__proto__":{"polluted2":1},"constructor":{"prototype":{"polluted3":1}}}]}')
CASES['proto_ids'] = good(profiles=[P('__proto__', 'Proto'), P('constructor', 'Ctor'), P('toString', 'TS')], progress=[{'id': '__proto__', 'units': {'0': {'passed': True}}}, {'id': 'constructor', 'units': {'__proto__': {'passed': True}, 'constructor': {'passed': True}}}],
                         cards=[{'id': 'p1:__proto__', 'profileId': '__proto__', 'item': '__proto__'}], attempts=[{'id': 'a1', 'profileId': 'p1', 'ts': 5, 'item': 'constructor', 'correct': False, 'drill': 'tell', 'unit': 1}])
CASES['hostile_strings'] = good(profiles=[P('p1', '<img src=x onerror=window.__xss=1>', goal='<svg onload=window.__xss=1>', speaks='"><b>', pains=['<b>x</b>', 5, None], grade='<i>')],
                                 cards=[{'id': 'p1:x', 'profileId': 'p1', 'item': '<b>', 'v': '<script>', 'rom': '<i>', 'en': '"><svg>', 'kind': 'word'}],
                                 assessments=[{'id': 'as1', 'profileId': 'p1', 'ts': 5, 'band': '<b>', 'level': '<i>', 'by': '<img src=x onerror=1>', 'orf': {'cwpm': 5, 'acc': '<b>'}}],
                                 settings=[{'key': 'ui', 'value': {'style': '<b>', 'scale': '9999', 'marks': 'yes'}}, {'key': 'stickersSeen:p1', 'value': ['<b>', 'abcdefghijklmnopq', 5]}])
CASES['settings_attack'] = good(settings=[{'key': 'mode', 'value': 'school'}, {'key': 'teacherPin', 'value': '0000'}, {'key': 'activeProfile', 'value': 'p9'}, {'key': 'deviceId', 'value': 'evil'}, {'key': 'onb', 'value': {'i': 5}}, {'key': 'teacherName', 'value': 'X'}, {'key': 'stickersSeen:../../x', 'value': []}], profiles=[P()])
CASES['profile_kind_teacher'] = good(profiles=[P('t1', 'Teach', kind='teacher', pin='1234', track='adult')])
CASES['dup_ids'] = good(profiles=[P('p1', 'First'), P('p1', 'Second')])
CASES['bad_rec_type'] = good(profiles=[P(), 'str'])
CASES['missing_name'] = good(profiles=[{'id': 'p1'}])
CASES['name_number'] = good(profiles=[P('p1', 5)])
CASES['store_not_list'] = good(profiles={'a': 1})
CASES['id_bad_chars'] = good(profiles=[P('a b', 'x')])
CASES['id_huge'] = good(profiles=[P('a' * 121, 'x')])
CASES['too_many_profiles'] = good(profiles=[P('p%d' % i, 'n') for i in range(201)])
CASES['too_many_attempts'] = good(profiles=[P()], attempts=[{'id': 'a%d' % i, 'profileId': 'p1', 'ts': 1} for i in range(60001)])
CASES['name_300'] = good(profiles=[P('p1', 'N' * 300)])
CASES['future_updatedAt'] = good(profiles=[P('p1', 'Future', updatedAt=9e15)])
CASES['unit_passed_all'] = good(profiles=[P()], progress=[{'id': 'p1', 'units': {str(i): {'passed': True, 'score': 10, 'total': 10} for i in range(13)}}])
CASES['cards_locked_unit'] = good(profiles=[P()], cards=[{'id': 'p1:' + 'ب', 'profileId': 'p1', 'item': 'ب', 'kind': 'letter', 'box': 1, 'due': 1, 'seen': 0, 'unit': 12}])
CASES['numbers_hostile'] = good(profiles=[P('p1', 'N', unit=99, minutes=1e300, days=-4)], attempts=[{'id': 'a1', 'profileId': 'p1', 'ts': 1e300}, {'id': 'a2', 'profileId': 'p1', 'ts': 5, 'ms': 'x', 'correct': 'yes'}])
CASES['deep_json'] = '[' * 100000 + ']' * 100000
CASES['empty_obj'] = {}
CASES['not_json'] = '<<<not json'
CASES['bom_json'] = '﻿' + json.dumps(good(profiles=[P()]))
CASES['huge_string'] = good(profiles=[P('p1', 'x' * (9 * 1024 * 1024))])

def write(c):
    f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(c if isinstance(c, str) else json.dumps(c)); return f
def restore_on(pg, f, screen='welcome'):
    with pg.expect_file_chooser(timeout=6000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(f); pg.wait_for_timeout(2500)
def settings_of(d): return {s['key']: s['value'] for s in d['settings']}
if __name__ == '__main__':
    names = sys.argv[1:] or list(CASES)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for n in names:
            ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2000)
            pg.evaluate("window.__polluted=()=>({a:({}).polluted,b:({}).polluted2,c:({}).polluted3})")
            f = write(CASES[n])
            try:
                restore_on(pg, f)
            except Exception as e:
                print(n, 'NO CHOOSER', str(e)[:80]); ctx.close(); continue
            tt = toast(pg); c, d = counts(pg); st = settings_of(d)
            print(f'{n:22} toast={tt!r:.110} counts={ {k:v for k,v in c.items() if v} } mode={st.get("mode")} pin={st.get("teacherPin")} active={st.get("activeProfile")} dev={str(st.get("deviceId"))[:6]} onb={"onb" in st}', 'poll', pg.evaluate('__polluted()'), 'xss', pg.evaluate('window.__xss'), 'errs', pg._errs[:2], 'screen:', pg.inner_text('#app')[:40].replace('\n', ' | '), flush=True)
            for pr in d['profiles']: print('      profile', {k: (str(v)[:40]) for k, v in pr.items() if k in ('id', 'name', 'kind', 'updatedAt', 'pin')})
            ctx.close()
        b.close()
