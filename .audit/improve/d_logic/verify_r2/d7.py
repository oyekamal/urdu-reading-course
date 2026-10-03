import json
from lib import *
JS='''async()=>{const Cn=await import('/src/content.js'); await Cn.loadContent();
 const les=document.createElement('div'); les.className='lesson'; les.innerHTML='<div class="choices"></div>'; document.body.append(les); await new Promise(r=>setTimeout(r,50));
 const ch=les.querySelector('.choices'); const tick=()=>new Promise(r=>setTimeout(r,0)); const out=[];
 for(const [A,B,right] of [['ب','پ',false],['ب','پ',true],['ا','1',false],['۱','۲',false],['ب','ـبـ',false]]){
   ch.innerHTML=''; const a=document.createElement('button'); a.className='tile ur'; a.textContent=A; if(right) a.dataset.right='names/be'; const b=document.createElement('button'); b.className='tile ur'; b.textContent=B; ch.append(a,b);
   await tick(); b.classList.add('no'); await tick(); await tick(); const s=document.querySelector('.feel-say'); out.push([A,B,right,s?s.textContent:null]); document.querySelectorAll('.feel-say').forEach(x=>x.remove()); }
 return out}'''
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500); print(json.dumps(pg.evaluate(JS),ensure_ascii=False)); print(pg.errors); b.close()
