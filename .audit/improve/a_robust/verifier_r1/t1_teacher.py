from common import *
PAY='<img src=x onerror=window.__xss=1>'
def setup(pg, extra=''):
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1200)
    pg.evaluate("""async(PAY)=>{
     await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'teacherPin',value:'1234'});
     await __put('profiles',{id:'t1',kind:'learner',name:PAY,track:'child',grade:PAY,createdAt:1});
     await __put('profiles',{id:'t2',kind:'learner',name:'Bilal',track:'child',grade:2,createdAt:2});
     await __put('profiles',{id:'t3',kind:'learner',name:'=cmd|calc',track:'child',grade:2,createdAt:2});
     await __put('assessments',{id:'e1',profileId:'t1',ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:PAY});
     await __put('assessments',{id:'e2',profileId:'t2',ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:70},comp:5,band:'fluent',by:'T'});
     await __put('assessments',{id:'e3',profileId:'t3',ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:70},comp:5,band:PAY,by:'T'});
    }""",PAY)
    pg.evaluate(extra) if extra else None
    pg.reload(); pg.wait_for_timeout(1500)
def unlock(pg):
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(500)
    pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
def tab(pg,t):
    pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t).click()",t); pg.wait_for_timeout(900)
def main():
  with sync_playwright() as p:
      b=p.chromium.launch()
      ctx,pg=newpage(b); setup(pg); unlock(pg)
      print('class screen:', pg.inner_text('#app')[:80].replace('\n',' | '))
      for t in ['Class','Lesson','Groups','Assess','Reports','Device']:
          tab(pg,t); print(t, 'inert', inert(pg)[:3], 'errs', pg._errs[-1:] , 'text', pg.inner_text('#app')[:50].replace('\n',' '))
      tab(pg,'Class')
      # Detail of t1
      pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Detail').click()"); pg.wait_for_timeout(1200); print('detail inert', inert(pg)[:3])
      # Open (per-child) for Bilal
      tab(pg,'Class')
      pg.evaluate("[...document.querySelectorAll('tr')].find(r=>r.innerText.includes('Bilal')).querySelector('button').click()"); pg.wait_for_timeout(1500)
      print('Open ->', pg.inner_text('#app')[:80].replace('\n',' | '), pg._errs[-1:])
      # CSV export capture
      ctx2,pg2=newpage(b); setup(pg2); unlock(pg2); tab(pg2,'Reports')
      with pg2.expect_download(timeout=8000) as dl:
          pg2.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Export CSV').click()"); gate_pass(pg2)
      path=dl.value.path(); print(open(path).read())
      # malformed assessment w/o orf
      ctx3,pg3=newpage(b); setup(pg3,"__put('assessments',{id:'e9',profileId:'t2',ts:Date.now()+5,band:'words',by:'x'})"); unlock(pg3)
      print('malformed assessment (no orf) class:', pg3.inner_text('#app')[:100].replace('\n',' | '), pg3._errs[-2:])
      tab(pg3,'Reports'); print('reports:', pg3.inner_text('#app')[:80].replace('\n',' | '), pg3._errs[-2:])
      b.close()

if __name__=='__main__': main()
