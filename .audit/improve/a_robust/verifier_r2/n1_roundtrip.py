from common import *
import json, tempfile, sys
sys.path.insert(0, '../verifier_r1')
def strip(r): return {k: v for k, v in r.items()}
SEED = """async()=>{
 const now=Date.now(); const __p=window.__put; const __put=(s,v)=>__p(s,{updatedAt:Date.now(),...v});
 await __put('settings',{key:'mode',value:'family'}); await __put('settings',{key:'teacherPin',value:'4321'}); await __put('settings',{key:'activeProfile',value:'p1'}); await __put('settings',{key:'teacherName',value:'Ms Secret'});
 await __put('settings',{key:'ui',value:{style:'nastaliq',marks:false,scale:'1.25',rom:false,audioOnly:true,spacing:'0.12'}});
 await __put('settings',{key:'stickersSeen:p1',value:['ا','ب']});
 await __put('profiles',{id:'p1',kind:'learner',name:'Amal',track:'child',grade:'3',avatar:'#1E9C8F',createdAt:now-1e6});
 await __put('profiles',{id:'p2',kind:'learner',name:'Bina',track:'heritage',grade:'',avatar:'#F2A93B',createdAt:now-5e5,goal:'family',speaks:'fluent',pains:['dots','check'],minutes:15,days:5,unit:0});
 await __put('profiles',{id:'p3',kind:'learner',name:'Tahir',track:'adult',grade:4,createdAt:now-4e5});
 for(let i=0;i<30;i++) await __put('attempts',{id:'a'+i,profileId:'p1',unit:1,drill:'tell',item:'ا',correct:i%3==0,ms:500+i,ts:now-i*1000});
 await __put('cards',{id:'p1:ا',profileId:'p1',item:'ا',kind:'letter',box:3,due:now+86400000,seen:4,last:now-1000,lastOk:true});
 await __put('cards',{id:'p1:بابا',profileId:'p1',item:'بابا',kind:'word',v:'بابا',rom:'bābā',en:'dad',unit:1,idx:3,box:1,due:now,seen:0,lastOk:false,lastMiss:now-500});
 await __put('cards',{id:'p1:sight',profileId:'p1',item:'اور',kind:'sight',idx:2,box:2,due:now,seen:1});
 await __put('sessions',{id:'s1',profileId:'p1',startedAt:now-9e5,endedAt:now-8e5,bites:7,correct:0,total:0});
 await __put('sessions',{id:'s2',profileId:'p1',startedAt:now-5e5,bites:[],correct:0,total:0});
 await __put('progress',{id:'p1',units:{0:{passed:true,score:10,total:10,at:now-1e5,lessons:{rules:now-2e5,done:now-1e5},steps:{hear:true,tell:false}},1:{lessons:{Lalif:now-5e4}}},wpm:[{ts:now-1e4,wpm:42,unit:1}],sessions:3,lastSession:now-8e5});
 await __put('assessments',{id:'as1',profileId:'p1',ts:now-3e5,letters:30,nonwords:10,words:12,orf:{cwpm:65,acc:92,seconds:60,errors:4,attempted:70,capped:false},orfDone:true,comp:2,compDone:false,band:'sentences',level:'fluent, comprehension not tested: not yet a standard result',by:'teacher'});
 await __put('assessments',{id:'as2',profileId:'p3',ts:now-2e5,letters:20,nonwords:5,words:3,orf:{cwpm:0,acc:0,seconds:0,errors:0},orfDone:false,comp:0,compDone:false,band:'not tested',level:'passage not tested: no standard result',by:'teacher'});
 await __put('assessments',{id:'as3',profileId:'p3',ts:now-1e5,letters:40,nonwords:20,words:20,orf:{cwpm:95.5,acc:99,seconds:60,errors:1,attempted:96,capped:true},orfDone:true,comp:5,compDone:true,band:'fluent',level:'exceeds grade-2 standard',by:'teacher'});
}"""
def dump(pg): return pg.evaluate('__dump()')
def export_me(pg):
    nav(pg, 'me'); pg.wait_for_timeout(500)
    with pg.expect_download(timeout=10000) as dl:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()"); gate_pass(pg)
    return open(dl.value.path()).read()
def restore_welcome(pg, raw):
    f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(raw)
    with pg.expect_file_chooser(timeout=6000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(f); pg.wait_for_timeout(3000)
def restore_me(pg, raw, gate=True):
    f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(raw)
    nav(pg, 'me'); pg.wait_for_timeout(500)
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup/.test(b.innerText)).click()")
    with pg.expect_file_chooser(timeout=8000) as fc:
        gate_pass(pg)
    fc.value.set_files(f); pg.wait_for_timeout(2500)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(2000)
    A = dump(pg)
    raw = export_me(pg); exp = json.loads(raw)
    print('export keys', list(exp.keys()), 'settings keys', [s['key'] for s in exp['settings']], 'PIN in file:', '4321' in raw, 'teacherName in file', 'Ms Secret' in raw, 'device', exp.get('device'))
    ctx2, pg2 = newpage(b); pg2.goto(BASE); pg2.wait_for_timeout(2200)
    restore_welcome(pg2, raw); print('welcome restore toast:', toast(pg2), '| screen:', pg2.inner_text('#app')[:50].replace('\n', ' | '))
    B = dump(pg2)
    for s in ['profiles', 'attempts', 'cards', 'sessions', 'progress', 'assessments']:
        a = {r['id']: r for r in A[s]}; bb = {r['id']: r for r in B[s]}
        diffs = []
        for k in a:
            if k not in bb: diffs.append(('MISSING', k)); continue
            if a[k] != bb[k]: diffs.append((k, {f: (a[k].get(f), bb[k].get(f)) for f in set(a[k]) | set(bb[k]) if a[k].get(f) != bb[k].get(f)}))
        extra = [k for k in bb if k not in a and not (s == 'cards' and True)]
        print(s, len(a), len(bb), 'LOSSLESS' if not diffs else diffs[:4], 'extra' if extra else '', extra[:3])
    sa = {s['key']: s['value'] for s in A['settings']}; sb = {s['key']: s['value'] for s in B['settings']}
    print('settings B keys:', sorted(sb), '| ui', sb.get('ui'), '| seen', sb.get('stickersSeen:p1'), '| mode', sb.get('mode'), 'pin', sb.get('teacherPin'), 'active', sb.get('activeProfile'), 'dev same?', sa.get('deviceId') == sb.get('deviceId'))
    pg2.evaluate("[...document.querySelectorAll('#app .card.btn')].find(b=>/Amal/.test(b.innerText))?.click()"); pg2.wait_for_timeout(1500)
    # double import on the same device (Me tab, gated) -> nothing new, no confirm
    restore_me(pg2, raw); print('second import toast:', toast(pg2), '| confirm', bool(pg2.query_selector('.a11y-sheet')))
    # device edits Amal's profile name later than backup -> importing the OLD backup must not overwrite
    pg2.evaluate("async()=>{const d=await __dump(); const p=d.profiles.find(x=>x.id==='p1'); p.name='Edited'; p.updatedAt=Date.now()+5; await __put('profiles',p)}")
    restore_me(pg2, raw); print('old backup over newer edit toast:', toast(pg2), '| name now', [x['name'] for x in dump(pg2)['profiles'] if x['id']=='p1'])
    # backup newer than device -> asks first
    raw2 = json.loads(raw); 
    for pr in raw2['profiles']:
        if pr['id'] == 'p1': pr['name'] = 'FromBackup'; pr['updatedAt'] = int(__import__('time').time() * 1000) + 10000000
    restore_me(pg2, json.dumps(raw2), True)
    print('newer backup: confirm sheet shown?', bool(pg2.query_selector('.a11y-sheet')), '|', (pg2.inner_text('.a11y-sheet-card')[:200].replace('\n', ' | ') if pg2.query_selector('.a11y-sheet') else ''))
    if pg2.query_selector('.a11y-sheet'):
        pg2.evaluate("document.querySelector('.a11y-stay').click()"); pg2.wait_for_timeout(600)
        print(' after Cancel: toast', toast(pg2), 'name', [x['name'] for x in dump(pg2)['profiles'] if x['id']=='p1'])
    print('errs', pg._errs, pg2._errs)
    b.close()
