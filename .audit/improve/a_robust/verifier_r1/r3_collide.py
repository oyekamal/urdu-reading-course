from common import *
from d1_helpers import *
from r2_import import run_import, base
import json, time
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); base(pg)
    now=int(time.time()*1000)
    # A: collide with the ACTIVE learner p1 using updatedAt = now+1h (passes the clamp): rename, change track, replace progress, overwrite card
    f={'format':'urdu-qaida-backup','version':1,
       'profiles':[{'id':'p1','name':'Hacked','kind':'teacher','track':'adult','updatedAt':now+3600000}],
       'progress':[{'id':'p1','units':{str(i):{'passed':True,'score':10,'total':10} for i in range(0,13)},'updatedAt':now+3600000}],
       'cards':[{'id':'p1:ا','profileId':'p1','item':'ا','kind':'letter','box':0,'due':0,'seen':0,'updatedAt':now+3600000}],
       'attempts':[{'id':'inj1','profileId':'p2','ts':now,'drill':'tell','item':'ا','correct':False,'unit':1}]}
    t=run_import(pg,json.dumps(f)); d=pg.evaluate('__dump()')
    print('toast', t)
    print('p1 now:', [ (x['name'],x.get('kind'),x['track']) for x in d['profiles'] if x['id']=='p1'])
    print('p1 progress units passed:', sorted(k for k,v in d['progress'][0]['units'].items() if v.get('passed')), 'lessons kept?', d['progress'][0]['units'].get('0',{}).get('lessons'))
    print('p1 card ا box:', [c['box'] for c in d['cards'] if c['id']=='p1:ا'])
    print('attempt injected into other learner p2:', [a['id'] for a in d['attempts']])
    pg.reload(); pg.wait_for_timeout(2000); print('after reload (active p1):', pg.inner_text('#app')[:80].replace('\n',' | '))
    ctx.close()
    # B: far-future updatedAt then re-import twice
    ctx,pg=newpage(b); base(pg)
    f={'format':'urdu-qaida-backup','version':1,'profiles':[{'id':'p2','name':'Future','kind':'learner','track':'adult','updatedAt':9e15}]}
    t=run_import(pg,json.dumps(f)); print('far-future updatedAt toast:', t, [x['name'] for x in pg.evaluate('__dump()')['profiles']])
    f['profiles'][0]['updatedAt']=now+80000000; f['profiles'][0]['name']='Future2'
    t=run_import(pg,json.dumps(f)); print('now+22h:', t); 
    f['profiles'][0]['name']='Future3'; t=run_import(pg,json.dumps(f)); print('same again:', t, [ (x['name'],x['updatedAt']-now) for x in pg.evaluate('__dump()')['profiles'] if x['id']=='p2'])
    # legit later edit by user then older backup can't override: edit p2 name via DB put with updatedAt now (simulate)
    ctx.close()
    # C: legacy v0.10-style backup (no marker, includes all settings)
    ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
    legacy={'exportedAt':'2026-09-01T00:00:00.000Z','device':'dev1',
     'settings':[{'key':'deviceId','value':'dev1','updatedAt':1},{'key':'mode','value':'school','updatedAt':1},{'key':'teacherPin','value':'0000','updatedAt':1},{'key':'activeProfile','value':'L1','updatedAt':1},{'key':'onb','value':None,'updatedAt':1},{'key':'ui','value':{'style':'nastaliq','marks':False},'updatedAt':5},{'key':'teacherName','value':'Mr X','updatedAt':1}],
     'profiles':[{'id':'L1','kind':'learner','name':'Legacy','track':'child','grade':'2','avatar':'🦁','createdAt':100,'updatedAt':200},{'id':'L2','name':'Old','track':'adult','createdAt':100,'updatedAt':200}],
     'attempts':[{'id':'la','profileId':'L1','unit':1,'drill':'tell','item':'ا','correct':True,'ms':900,'ts':300,'updatedAt':300}],
     'cards':[{'id':'L1:ا','profileId':'L1','item':'ا','kind':'letter','box':2,'due':9,'seen':2,'updatedAt':300}],
     'sessions':[{'id':'ls','profileId':'L1','startedAt':1,'bites':[1,2,3],'correct':0,'total':0,'updatedAt':1}],
     'progress':[{'id':'L1','units':{'0':{'passed':True,'score':10,'total':10,'at':3}},'wpm':[{'ts':1,'wpm':30,'unit':1}],'sessions':1,'updatedAt':3}],
     'assessments':[{'id':'as','profileId':'L1','ts':3,'letters':10,'nonwords':5,'words':5,'orf':{'cwpm':20,'acc':80},'comp':1,'band':'words','by':'teacher','updatedAt':3}]}
    p_=tempfile.mktemp(suffix='.json'); open(p_,'w').write(json.dumps(legacy))
    with pg.expect_file_chooser(timeout=6000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(p_); pg.wait_for_timeout(2500)
    st=settings(pg); print('legacy restore toast:', toast(pg), '| screen:', pg.inner_text('#app')[:80].replace('\n',' | '))
    print('settings after legacy:', {k:v for k,v in st.items() if k!='deviceId'}, 'deviceId kept?', st.get('deviceId')!='dev1')
    print('profiles', [(x['name'],x['track'],x.get('avatar')) for x in pg.evaluate('__dump()')['profiles']], pg._errs)
    # second restore of same file
    nav(pg,'me') if pg.query_selector('.bottom') else None
    ctx.close(); b.close()
