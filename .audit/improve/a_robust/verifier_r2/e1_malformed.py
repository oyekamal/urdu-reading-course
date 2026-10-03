from common import *
import sys, json
PID = 'pp1'
BASEREC = """async()=>{
 const now=Date.now();
 await __put('settings',{key:'mode',value:'family'}); await __put('settings',{key:'activeProfile',value:'pp1'}); await __put('settings',{key:'teacherPin',value:'1234'});
 await __put('profiles',{id:'pp1',kind:'learner',name:'Zara',track:'child',grade:2,avatar:'#1E9C8F',createdAt:now-1e6});
 await __put('profiles',{id:'pp2',kind:'learner',name:'Bilal',track:'adult',grade:'',createdAt:now-9e5});
 await __put('progress',{id:'pp1',units:{0:{passed:true,score:10,total:10,at:now-1e5,lessons:{rules:now-2e5,done:now-1e5}},1:{lessons:{Lalif:now-5e4}}},wpm:[{ts:now-1e4,wpm:42,unit:1}],sessions:3,lastSession:now-8e5});
 await __put('cards',{id:'pp1:ا',profileId:'pp1',item:'ا',kind:'letter',box:3,due:now-1000,seen:4,last:now-1000,lastOk:true});
 await __put('attempts',{id:'a1',profileId:'pp1',unit:1,drill:'tell',item:'ا',correct:false,ms:500,ts:now-1000});
 await __put('sessions',{id:'s1',profileId:'pp1',startedAt:now-9e5,endedAt:now-8e5,bites:7,correct:0,total:0});
 await __put('assessments',{id:'as1',profileId:'pp1',ts:now-3e5,letters:30,nonwords:10,words:12,orf:{cwpm:65,acc:92},orfDone:true,comp:2,compDone:false,band:'sentences',level:'x',by:'teacher'});
}"""
SC = {}
def add(name, store, rec): SC[name] = [(store, rec)]
# progress
for n, units in {'units_null': None, 'units_str': 'abc', 'units_arr': [1, 2], 'units_n0null': {'0': None}, 'units_n1num': {'1': 5}, 'units_lessonsnull': {'0': {'lessons': None, 'passed': True}},
                 'units_lessonsstr': {'1': {'lessons': 'x'}}, 'units_passed_str': {'0': {'passed': 'yes'}}, 'units_steps_arr': {'1': {'steps': [1]}}, 'units_deep': {'0': {'lessons': {'a': {'b': {'c': {'d': {'e': {'f': '<img src=x onerror=1>'}}}}}}}}}.items():
    add('progress_' + n, 'progress', {'id': PID, 'units': units, 'wpm': [], 'sessions': 1})
add('progress_wpm_str', 'progress', {'id': PID, 'units': {}, 'wpm': 'x', 'sessions': 'x'})
add('progress_wpm_bad', 'progress', {'id': PID, 'units': {}, 'wpm': [None, {'wpm': '<b>'}, {'wpm': 1e308}, {'wpm': -5}, 7], 'sessions': -1})
add('progress_wpm_inf', 'progress', {'id': PID, 'units': {'0': {'passed': True}}, 'wpm': [{'ts': 1, 'wpm': 99999999}], 'sessions': 1e308})
# cards
for n, rec in {'box_str': {'box': 'a'}, 'box_big': {'box': 99}, 'due_str': {'due': 'x'}, 'seen_missing': {'seen': None}, 'item_obj': {'item': {'a': 1}}, 'kind_weird': {'kind': 'word', 'unit': 'x', 'idx': 'y', 'v': None, 'rom': None, 'en': {'x': 1}},
               'letter_unknown': {'kind': 'letter', 'item': 'ZZZ'}, 'word_unit99': {'kind': 'word', 'unit': 99, 'idx': 5, 'item': 'x', 'v': 'x', 'rom': 'x', 'en': 'x'}, 'noprofile': {'profileId': None}}.items():
    base = {'id': 'pp1:zz', 'profileId': PID, 'item': 'ب', 'kind': 'letter', 'box': 1, 'due': 1, 'seen': 0}; base.update(rec)
    add('cards_' + n, 'cards', base)
# attempts
for n, rec in {'ts_str': {'ts': 'x'}, 'item_obj': {'item': {'a': 1}, 'correct': False}, 'drill_obj': {'drill': {'a': 1}}, 'correct_str': {'correct': 'no'}, 'unit_str': {'unit': 'x'}, 'item_proto': {'item': '__proto__', 'correct': False}, 'item_ctor': {'item': 'constructor', 'correct': False},
               'ms_neg': {'ms': -1e9}}.items():
    base = {'id': 'att2', 'profileId': PID, 'unit': 1, 'drill': 'tell', 'item': 'ا', 'correct': False, 'ms': 5, 'ts': 'NOW'}; base.update(rec)
    add('attempts_' + n, 'attempts', base)
# sessions
for n, rec in {'started_str': {'startedAt': 'x'}, 'started_null': {'startedAt': None}, 'bites_obj': {'bites': {'a': 1}}}.items():
    base = {'id': 's2', 'profileId': PID}; base.update(rec); add('sessions_' + n, 'sessions', base)
# assessments
for n, rec in {'orf_str': {'orf': 'x'}, 'orf_null': {'orf': None}, 'ts_str': {'ts': 'x'}, 'ts_none': {'ts': None}, 'letters_obj': {'letters': {'a': 1}}, 'band_obj': {'band': {'a': 1}}, 'by_obj': {'by': {'a': 1}}, 'orf_cwpm_str': {'orf': {'cwpm': 'zz'}}, 'comp_str': {'comp': 'x'},
               'orf_neg': {'orf': {'cwpm': -5, 'acc': 1e9}}, 'noorfDone': {'orfDone': 'x', 'compDone': 'y'}}.items():
    base = {'id': 'as2', 'profileId': PID, 'ts': 'NOW', 'letters': 5, 'nonwords': 5, 'words': 5, 'orf': {'cwpm': 40}, 'comp': 2, 'band': 'words', 'by': 'T'}; base.update(rec); add('assess_' + n, 'assessments', base)
# profiles
for n, rec in {'name_obj': {'name': {'a': 1}}, 'name_none': {'name': None}, 'track_obj': {'track': {'a': 1}}, 'grade_obj': {'grade': {'a': 1}}, 'kind_none': {'kind': None}, 'avatar_obj': {'avatar': {'a': 1}}, 'goal_obj': {'goal': {'a': 1}, 'pains': 'x', 'speaks': {'a': 1}}, 'name_emptyish': {'name': '   '},
               'name_longlong': {'name': 'ä' * 200000}, 'id_num': {'id': 5}, 'id_proto': {'id': '__proto__'}, 'id_ctor': {'id': 'constructor'}, 'id_arr': {'id': [1, 2]}, 'name_rtl': {'name': '‮‮‮cba'}, 'name_zalgo': {'name': 'a' + '̀' * 5000}, 'unit_str': {'unit': 'x'}}.items():
    base = {'id': 'pp3', 'kind': 'learner', 'name': 'Third', 'track': 'child', 'grade': 1, 'createdAt': 5}; base.update(rec); add('profile_' + n, 'profiles', base)
# settings
for n, (k, v) in {'ui_arr': ('ui', [1]), 'ui_str': ('ui', 'x'), 'ui_num': ('ui', 7), 'ui_scale': ('ui', {'scale': 'calc(1px+1px)', 'spacing': '9999', 'style': 'x;y'}), 'mode_num': ('mode', 7), 'active_obj': ('activeProfile', {'a': 1}), 'active_missing': ('activeProfile', 'nobody'),
                  'onb_str': ('onb', 'x'), 'onb_arr': ('onb', [1]), 'seen_str': ('stickersSeen:pp1', 'x'), 'seen_obj': ('stickersSeen:pp1', {'a': 1}), 'seen_arrobj': ('stickersSeen:pp1', [{'a': 1}, None, 5]), 'pin_num': ('teacherPin', 1234), 'name_obj': ('teacherName', {'a': 1})}.items():
    add('settings_' + n, 'settings', {'key': k, 'value': v})
SC['baseline'] = []
WALK = r"""async()=>{
 const out={}; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const txt=()=>document.getElementById('app').innerText.replace(/\s+/g,' ').trim();
 out.boot=txt().slice(0,60);
 const keys=[...document.querySelectorAll('.bottom button')].map(b=>b.dataset.k);
 for(const k of keys){ document.querySelector(`.bottom button[data-k='${k}']`)?.click(); await sleep(900); out['tab_'+k]=txt().length; }
 return {out,keys}}"""
def run(b, name, label, teacher=False):
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1000)
    pg.evaluate(BASEREC)
    for store, rec in SC[name]:
        pg.evaluate("async([s,r])=>{ if(r.ts==='NOW') r.ts=Date.now(); try{ await __put(s,r) }catch(e){ window.__putfail=String(e) } }", [store, rec])
    pf = pg.evaluate("window.__putfail||null")
    pg.reload(); pg.wait_for_timeout(2500)
    res = {}
    try:
        r = pg.evaluate(WALK); res.update(r['out'])
    except Exception as e: res['walk'] = 'EXC ' + str(e)[:60]
    res['rec'] = pg.evaluate("!!document.querySelector('.recovery')")
    res['errs'] = pg._errs[:3]
    bad = [k for k, v in res.items() if k.startswith('tab_') and v < 60]
    bad_flag = bool(res['errs']) or res['rec'] or bad or 'Loading' in str(res.get('boot')) or 'walk' in res
    return pf, res, bad_flag
def run_teacher(b, name):
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1000)
    pg.evaluate(BASEREC)
    pg.evaluate("async()=>{await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'activeProfile',value:null});}")
    for store, rec in SC[name]:
        pg.evaluate("async([s,r])=>{ if(r.ts==='NOW') r.ts=Date.now(); try{ await __put(s,r) }catch(e){} }", [store, rec])
    pg.reload(); pg.wait_for_timeout(2000)
    out = {}
    try:
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(500)
        pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
        for t in ['Class', 'Lesson', 'Groups', 'Assess', 'Reports', 'Device']:
            pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()", t); pg.wait_for_timeout(900)
            out[t] = pg.evaluate("document.getElementById('app').innerText.length")
        pg.evaluate("[...document.querySelectorAll('.tab')].find(x=>x.innerText==='Class').click()"); pg.wait_for_timeout(700)
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Detail')?.click()"); pg.wait_for_timeout(1200)
        out['detail'] = pg.evaluate("document.getElementById('app').innerText.length")
    except Exception as e: out['EXC'] = str(e)[:80]
    out['errs'] = pg._errs[:3]
    bad = [k for k, v in out.items() if k in ('Class', 'Lesson', 'Groups', 'Assess', 'Reports', 'Device', 'detail') and v < 60]
    ctx.close()
    return out, bool(out['errs']) or bool(bad) or 'EXC' in out
if __name__ == '__main__':
    names = [n for n in SC if (not sys.argv[1:] or any(n.startswith(a) for a in sys.argv[1:]))]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for n in names:
            try:
                pf, res, flag = run(b, n, n)
                tout, tflag = run_teacher(b, n)
            except Exception as e:
                print('SCEN', n, 'HARNESS EXC', str(e)[:100], flush=True); continue
            print(('FLAG ' if (flag or tflag) else 'ok   ') + n, '| putfail', (pf or '')[:40], '| learner', {k: v for k, v in res.items() if k != 'tab_today' or True}, '| teacher', tout, flush=True)
        b.close()
