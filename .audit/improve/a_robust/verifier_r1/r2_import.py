from common import *
from d1_helpers import *
import json, time
RES=[]
def chk(n, ok, extra=''): RES.append(ok); print(('PASS ' if ok else 'FAIL ')+n, extra)
def deep(n): return '{"format":"urdu-qaida-backup","version":1,"profiles":' + '['*n + ']'*n + '}'
def run_import(pg, text, how='me'):
    p_=tempfile.mktemp(suffix='.json'); open(p_,'w').write(text)
    pg.evaluate("()=>{const t=document.getElementById('toast'); if(t) t.textContent=''}")
    with pg.expect_file_chooser(timeout=8000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup/.test(b.innerText)).click()"); gate_pass(pg)
    fc.value.set_files(p_); pg.wait_for_timeout(2000)
    return toast(pg)
def base(pg):
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
    pg.evaluate("""async()=>{const now=Date.now();
      await __put('settings',{key:'mode',value:'family'}); await __put('settings',{key:'teacherPin',value:'4321'}); await __put('settings',{key:'activeProfile',value:'p1'});
      await __put('profiles',{id:'p1',kind:'learner',name:'Amal',track:'child',grade:'3',avatar:'#1E9C8F',createdAt:now-1e6});
      await __put('profiles',{id:'p2',kind:'learner',name:'Bina',track:'adult',grade:'',createdAt:now-1e6});
      await __put('progress',{id:'p1',units:{0:{passed:true,lessons:{rules:1,done:1}},1:{lessons:{Lalif:1}}},wpm:[],sessions:2});
      await __put('cards',{id:'p1:ا',profileId:'p1',item:'ا',kind:'letter',box:4,due:now+86400000,seen:9});
    }"""); pg.reload(); pg.wait_for_timeout(1500); nav(pg,'me')
H='"format":"urdu-qaida-backup","version":1'
def main():
  with sync_playwright() as p:
      b=p.chromium.launch()
      ctx,pg=newpage(b); base(pg)
      before=counts(pg)[0]
      cases=[
       ('truncated json', '{"format":"urdu-qaida-backup","version":1,"profiles":[{"id":"x","na'),
       ('deeply nested 50000', deep(50000)),
       ('wrong types everywhere', json.dumps({'format':'urdu-qaida-backup','version':'1','profiles':{}})),
       ('version 0', '{"format":"urdu-qaida-backup","version":0,"profiles":[]}'),
       ('version float', '{"format":"urdu-qaida-backup","version":1.5,"profiles":[]}'),
       ('empty object w/ format', '{"format":"urdu-qaida-backup","version":1}'),
       ('100k attempts', json.dumps({'format':'urdu-qaida-backup','version':1,'attempts':[{'id':'a%d'%i,'profileId':'p1','ts':1} for i in range(100000)]})),
       ('59999 attempts + 59999 cards', json.dumps({'format':'urdu-qaida-backup','version':1,'attempts':[{'id':'a%d'%i,'profileId':'p1','ts':1} for i in range(60000)],'cards':[{'id':'c%d'%i,'profileId':'p1','item':'x'} for i in range(20000)],'sessions':[{'id':'s%d'%i,'profileId':'p1'} for i in range(20000)],'assessments':[{'id':'q%d'%i,'profileId':'p1','ts':1} for i in range(5000)]})),
       ('null / NaN-ish numbers', json.dumps({'format':'urdu-qaida-backup','version':1,'attempts':[{'id':'z','profileId':'p1','ts':None}]})),
       ('negative ts', json.dumps({'format':'urdu-qaida-backup','version':1,'attempts':[{'id':'z','profileId':'p1','ts':-5}]})),
       ('1e308 ts', '{"format":"urdu-qaida-backup","version":1,"attempts":[{"id":"z","profileId":"p1","ts":1e308}]}'),
       ('settings only forged', json.dumps({'format':'urdu-qaida-backup','version':1,'settings':[{'key':'teacherPin','value':'0000'},{'key':'mode','value':'school'},{'key':'onb','value':{'i':3}}]})),
      ]
      for label,text in cases:
          t0=time.time(); t=run_import(pg,text); after=counts(pg)[0]; st=settings(pg)
          same = after==before or label.startswith('59999')
          print(('OK  ' if bool(t) else 'SILENT '), label, f'{time.time()-t0:.1f}s', repr(t), 'unchanged' if after==before else f'CHANGED {after}', 'pin',st.get('teacherPin'),'mode',st.get('mode'), 'errs', pg._errs[-1:])
          if after!=before:
              # restore base state for next case
              ctx.close(); ctx,pg=newpage(b); base(pg); before=counts(pg)[0]
      ctx.close()
      # prototype pollution + payloads in every field
      ctx,pg=newpage(b); base(pg)
      PAY='<img src=x onerror=window.__xss=1>'
      evil={'format':'urdu-qaida-backup','version':1,'__proto__':{'polluted':1},'constructor':{'prototype':{'polluted2':1}},
        'profiles':[{'id':'e1','name':PAY,'kind':'learner','track':'child','grade':PAY,'avatar':'#fff" onmouseover="x','goal':PAY,'speaks':PAY,'pains':[PAY],'minutes':PAY,'__proto__':{'polluted3':1},'updatedAt':5}],
        'attempts':[{'id':'e1','profileId':'e1','ts':1,'drill':PAY,'item':PAY,'correct':'yes','unit':PAY}],
        'cards':[{'id':'e1:q','profileId':'e1','item':PAY,'kind':'letter','v':PAY,'rom':PAY,'en':PAY}],
        'sessions':[{'id':'e1','profileId':'e1','bites':PAY}],
        'progress':[{'id':'e1','units':{'__proto__':{'passed':True},'constructor':{'passed':True},'7':{'passed':True,'lessons':{'__proto__':1,PAY:1}},'abc':{}},'wpm':[PAY]}],
        'assessments':[{'id':'e1','profileId':'e1','ts':1,'band':PAY,'by':PAY,'orf':{'cwpm':PAY}}],
        'settings':[{'key':'ui','value':{'style':PAY,'scale':PAY}},{'key':'stickersSeen:'+PAY,'value':[PAY]}]}
      raw=json.dumps(evil).replace('"__proto__": {"polluted": 1}','"__proto__": {"polluted": 1}')
      t=run_import(pg,raw); print('evil import toast:', repr(t))
      d=pg.evaluate('__dump()')
      print('polluted?', pg.evaluate("({}).polluted||({}).polluted2||({}).polluted3||Object.prototype.passed||null"))
      for s in ['profiles','attempts','cards','sessions','progress','assessments']:
          rows=[r for r in d[s] if str(r.get('id','')).startswith('e1')]
          if rows: print(s, json.dumps(rows[0], ensure_ascii=False)[:300])
      nav(pg,'me'); nav(pg,'review'); print('inert after evil import:', inert(pg)[:3], pg._errs[-1:])
      ctx.close()
      b.close()

if __name__=='__main__': main()
