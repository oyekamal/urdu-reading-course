from common import *
from t1_teacher import setup, unlock, tab
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); setup(pg)
    pg.evaluate("""async()=>{ await __put('attempts',{id:'a1',profileId:'t2',unit:1,drill:'tell',item:'ا',correct:true,ms:1,ts:Date.now()}); await __put('cards',{id:'t2:ا',profileId:'t2',item:'ا',kind:'letter',box:1,due:1,seen:0}); await __put('progress',{id:'t2',units:{0:{passed:true}}}); await __put('sessions',{id:'s1',profileId:'t2',startedAt:1}); await __put('settings',{key:'stickersSeen:t2',value:['ا']}) }""")
    pg.reload(); pg.wait_for_timeout(1500); unlock(pg)
    pg.on('dialog', lambda d: d.accept())
    pg.evaluate("[...document.querySelectorAll('tr')].find(r=>r.innerText.includes('Bilal')).querySelectorAll('button')[4].click()"); pg.wait_for_timeout(1200)
    d=pg.evaluate('__dump()')
    print('after teacher Delete Bilal: profiles', [x['name'] for x in d['profiles']], '| orphans: attempts',len([a for a in d['attempts'] if a['profileId']=='t2']),'cards',len([a for a in d['cards'] if a['profileId']=='t2']),'progress',len([a for a in d['progress'] if a['id']=='t2']),'sessions',len(d['sessions']),'assessments',len([a for a in d['assessments'] if a['profileId']=='t2']), 'stickersSeen', [s['key'] for s in d['settings'] if 'stickersSeen' in s['key']])
    ctx.close()
    # learner Reset keeps profile + name
    ctx,pg=newpage(b); quick_profile(pg,'ResetMe'); pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    pg.evaluate("p=>__put('settings',{key:'stickersSeen:'+p,value:['ا']})",pid)
    nav(pg,'me'); pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Reset this profile/.test(b.innerText)).click()"); gate_pass(pg); pg.wait_for_timeout(1200)
    d=pg.evaluate('__dump()'); print('after Reset: profiles', [x['name'] for x in d['profiles']], 'settings keys', [s['key'] for s in d['settings']])
    b.close()
