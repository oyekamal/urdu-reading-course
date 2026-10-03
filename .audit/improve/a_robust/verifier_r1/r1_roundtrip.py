from common import *
from d1_helpers import *
import json
def strip(r): return {k:v for k,v in r.items() if k!='updatedAt'}
def seed(pg):
    pg.evaluate("""async()=>{
     const now=Date.now();
     await __put('settings',{key:'mode',value:'family'}); await __put('settings',{key:'teacherPin',value:'4321'}); await __put('settings',{key:'activeProfile',value:'p1'});
     await __put('settings',{key:'ui',value:{style:'nastaliq',marks:false,scale:'1.25',rom:false,audioOnly:true,spacing:'0.12'}});
     await __put('settings',{key:'stickersSeen:p1',value:['ا','ب']});
     await __put('profiles',{id:'p1',kind:'learner',name:'Amal',track:'child',grade:'3',avatar:'#1E9C8F',createdAt:now-1e6});
     await __put('profiles',{id:'p2',kind:'learner',name:'Bina',track:'heritage',grade:'',avatar:'#F2A93B',createdAt:now-5e5,goal:'read the Quran',speaks:'fluent',pains:['dots','joining'],minutes:15,days:5});
     for(let i=0;i<30;i++) await __put('attempts',{id:'a'+i,profileId:'p1',unit:1,drill:'tell',item:'ا',correct:i%3==0,ms:500+i,ts:now-i*1000});
     await __put('cards',{id:'p1:ا',profileId:'p1',item:'ا',kind:'letter',box:3,due:now+86400000,seen:4,last:now-1000,lastOk:true});
     await __put('cards',{id:'p1:بابا',profileId:'p1',item:'بابا',kind:'word',v:'بابا',rom:'bābā',en:'dad',unit:1,idx:3,box:1,due:now,seen:0,lastOk:false,lastMiss:now-500});
     await __put('sessions',{id:'s1',profileId:'p1',startedAt:now-9e5,endedAt:now-8e5,bites:7,correct:0,total:0});
     await __put('progress',{id:'p1',units:{0:{passed:true,score:10,total:10,at:now-1e5,lessons:{rules:now-2e5,done:now-1e5},steps:{hear:true,tell:false}},1:{lessons:{Lalif:now-5e4}}},wpm:[{ts:now-1e4,wpm:42,unit:1}],sessions:3,lastSession:now-8e5});
     await __put('assessments',{id:'as1',profileId:'p1',ts:now-3e5,letters:30,nonwords:10,words:12,orf:{cwpm:65,acc:92,seconds:60,errors:4,capped:false},orfDone:true,comp:2,compDone:false,band:'sentences',level:'fluent, comprehension not tested: not yet a standard result',by:'teacher'});
    }""")
def dump(pg): return pg.evaluate('__dump()')
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b,accept_downloads=True) if False else newpage(b)
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500); seed(pg); pg.reload(); pg.wait_for_timeout(1500)
    A=dump(pg)
    # export via Me/More of active profile p1 (child -> Me tab)
    nav(pg,'me'); pg.wait_for_timeout(500)
    with pg.expect_download(timeout=10000) as dl:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()"); gate_pass(pg)
    path=dl.value.path(); raw=open(path).read(); exp=json.loads(raw)
    print('export keys:', list(exp.keys()))
    print('export settings keys:', [s['key'] for s in exp['settings']], '| contains PIN 4321?', '4321' in raw)
    # fresh device restore through welcome screen
    ctx2,pg2=newpage(b); pg2.goto(BASE); pg2.wait_for_timeout(2200)
    p_=tempfile.mktemp(suffix='.json'); open(p_,'w').write(raw)
    with pg2.expect_file_chooser(timeout=6000) as fc:
        pg2.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(p_); pg2.wait_for_timeout(2500)
    print('toast:', toast(pg2), '| screen:', pg2.inner_text('#app')[:60].replace('\n',' | '))
    B=dump(pg2)
    for s in ['profiles','attempts','cards','sessions','progress','assessments']:
        a={r['id']:strip(r) for r in A[s]}; bb={r['id']:strip(r) for r in B[s]}
        diffs=[]
        for k in a:
            if k not in bb: diffs.append(('MISSING',k)); continue
            if a[k]!=bb[k]: diffs.append((k,{f:(a[k].get(f),bb[k].get(f)) for f in set(a[k])|set(bb[k]) if a[k].get(f)!=bb[k].get(f)}))
        print(s, len(a), len(bb), 'LOSSLESS' if not diffs else diffs[:3])
    print('settings B:', {s['key']:s['value'] for s in B['settings'] if s['key']!='deviceId'})
    print('pg2 errs', pg2._errs)
    b.close()
