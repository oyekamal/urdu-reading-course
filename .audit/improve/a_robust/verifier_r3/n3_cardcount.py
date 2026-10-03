import sys; sys.path.insert(0,'.')
from common import *
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); quick_profile(pg,'Zara'); pid=pg.evaluate('__dump()')['profiles'][0]['id']
    for n in (6,12,13):
        pg.evaluate("([pid,n])=>__put('progress',{id:pid,units:Object.fromEntries([...Array(n)].map((_,i)=>[i,{passed:true}]))})",[pid,n]); pg.reload(); pg.wait_for_timeout(3500)
        print('units passed',n,'-> cards per learner',len(pg.evaluate('__dump()')['cards']))
