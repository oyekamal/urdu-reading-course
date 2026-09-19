# Raw phone screenshots for the store listing (1080-wide). Usage: python3 tools/store_shots.py [port]
import sys, re; from playwright.sync_api import sync_playwright
port=sys.argv[1] if len(sys.argv)>1 else '5188'; out='../store/raw'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":412,"height":880}, device_scale_factor=2.62); pg=ctx.new_page(); pg.on("dialog", lambda d: d.accept())
    pg.goto(f"http://localhost:{port}/"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/08_mode.png")
    pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]","Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
    # seed realistic demo progress so the Progress screenshot doesn't show zeros
    pid = pg.evaluate("(async()=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];return p.id})()")
    pg.evaluate("""async (pid)=>{const {db,uid}=await import('/src/db.js');const S=await import('/src/session.js');const now=Date.now(),DAY=86400000;
      const p={id:pid,units:{},wpm:[],sessions:14,lastSession:now};for(let n=0;n<=6;n++)p.units[n]={passed:true,score:9,total:10,at:now-(7-n)*3*DAY};p.units[7]={lessons:{L1:now,L2:now}};
      p.wpm=[22,28,31,37,44,49,58].map((w,i)=>({ts:now-(7-i)*4*DAY,wpm:w,unit:i+1}));await db.put('progress',p);
      await S.ensureCards(pid,7);const cards=await db.by('cards','profileId',pid);let i=0;for(const c of cards){i++;const box=i%5===0?1:i%3===0?3:4+(i%2);await db.put('cards',{...c,box,seen:box+2,due:now+(i%4)*DAY-DAY,last:now-DAY});}
      const drills=['tell','join','read','trace','dictation','quiz'];for(let k=0;k<90;k++){await db.put('attempts',{id:uid(),profileId:pid,unit:1+(k%6),drill:drills[k%6],item:cards[k%cards.length].item,correct:k%7!==0,ms:0,ts:now-(k%13)*DAY});}
      for(let d=0;d<20;d++){await db.put('sessions',{id:uid(),profileId:pid,startedAt:now-(27-d-(d%3))*DAY,endedAt:now-(27-d-(d%3))*DAY+600000,bites:5,correct:9,total:10});}}""", pid)
    pg.reload(); pg.wait_for_timeout(3500); pg.click(".bottom button:has-text('Progress')"); pg.wait_for_timeout(2000); pg.screenshot(path=f"{out}/07_progress.png")
    pg.evaluate("""async()=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];const pr=await db.get('progress',p.id);pr.units={};pr.wpm=[];pr.sessions=0;await db.put('progress',pr);for(const c of await db.by('cards','profileId',p.id))await db.del('cards',c.id);}"""); pg.reload(); pg.wait_for_timeout(1500)
    # finish unit 0 quickly, then open alif
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(600)
    for _ in range(3): pg.click("button:has-text('Continue')"); pg.wait_for_timeout(350)
    pg.click("button:has-text('Next')"); pg.wait_for_timeout(500); pg.click("button:has-text('Unlock')"); pg.wait_for_timeout(700); pg.click("button:has-text('Back to path')"); pg.wait_for_timeout(1200); pg.screenshot(path=f"{out}/02_path.png")
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1500); pg.screenshot(path=f"{out}/01_letter.png")
    pg.click("button:has-text('I heard it')"); pg.wait_for_timeout(800); pg.click("button:has-text('I see it')"); pg.wait_for_timeout(900)
    pg.evaluate("document.querySelector('canvas.trace')?.scrollIntoView({block:'center'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/03_trace.png")
    # words: unit 1 lesson view via Units tab (locked confirm auto-accepted)
    pg.click(".bottom button:has-text('Units')"); pg.wait_for_timeout(700); pg.click(".ucard:nth-child(2)"); pg.wait_for_timeout(1200)
    pg.wait_for_selector(".words", timeout=8000); pg.evaluate("""()=>{const h=[...document.querySelectorAll('h3')].find(h=>h.textContent.includes('Read it'));const main=h.parentElement;[...main.children].forEach(c=>{if(c!==h&&c!==h.nextElementSibling&&!c.matches('.row,.bottom'))c.style.display='none'});h.style.marginTop='24px';window.scrollTo(0,0)}"""); pg.wait_for_timeout(400); pg.screenshot(path=f"{out}/04_words.png")
    pg.click(".bottom button:has-text('Units')"); pg.wait_for_timeout(700); pg.click(".ucard:nth-child(12)"); pg.wait_for_timeout(1200)
    pg.wait_for_selector(".nastaliq", timeout=8000); pg.evaluate("""()=>{const h=[...document.querySelectorAll('.card h3')].find(x=>x.textContent.includes('Nastaliq'));const card=h.closest('.card');const main=card.parentElement;[...main.children].forEach(c=>{if(c!==card&&!c.matches('.row,.bottom'))c.style.display='none'});const keep=new Set([h,h.nextElementSibling]);[...card.children].forEach(c=>{if(!keep.has(c))c.remove()});const t=document.createElement('h2');t.textContent='Same word, two typefaces';card.prepend(t);const pp=document.createElement('p');pp.className='muted';pp.textContent='Learn in Naskh. Read newspapers and books in Nastaliq.';t.after(pp);[...card.querySelectorAll('.row .card')].forEach(x=>{x.style.width='100%';x.style.fontSize='34px'});window.scrollTo(0,0)}"""); pg.wait_for_timeout(400); pg.screenshot(path=f"{out}/05_nastaliq.png")
    # teacher assess
    ctx2=b.new_context(viewport={"width":412,"height":880}, device_scale_factor=2.62); pg2=ctx2.new_page(); pg2.on("dialog", lambda d: d.accept()); pg2.goto(f"http://localhost:{port}/"); pg2.wait_for_timeout(1500)
    pg2.click("text=My class"); pg2.wait_for_timeout(400); pg2.fill("input[placeholder='Your name']","Ms Sana"); pg2.fill("input[placeholder='4-digit PIN']","1234"); pg2.click("button:has-text('Save')"); pg2.wait_for_timeout(600)
    pg2.click("button:has-text('Teacher')"); pg2.wait_for_timeout(300); pg2.fill("input[type=password]","1234"); pg2.click("button:has-text('Unlock')"); pg2.wait_for_timeout(1200)
    for n,g in [("Ayesha","1"),("Bilal","2"),("Hira","1")]:
        pg2.fill("input[placeholder=Name]",n); pg2.click("button:has-text('Add child')"); pg2.wait_for_timeout(400)
    pg2.evaluate("""async()=>{const {db,uid}=await import('/src/db.js');const {bandFor}=await import('/src/content.js');const ps=(await db.all('profiles')).filter(p=>p.kind!=='teacher');const DAY=86400000;const data=[[38,6,14,31,3],[52,9,22,64,5],[45,8,19,48,4]];
      ps.forEach(async(p,i)=>{for(let k=0;k<2;k++){const d=data[i];const cw=d[3]-(k?12:0);await db.put('assessments',{id:uid(),profileId:p.id,ts:Date.now()-(k?35+i*3:1+i*4)*DAY,by:'Ms Sana',letters:d[0]-(k?8:0),nonwords:d[1]-(k?2:0),words:d[2]-(k?5:0),orf:{cwpm:cw,seconds:60,errors:3},comp:d[4]-(k?1:0),band:bandFor(cw)});}})}"""); pg2.wait_for_timeout(800)
    pg2.click(".tab:has-text('Class')"); pg2.wait_for_timeout(600); pg2.click(".tab:has-text('Assess')"); pg2.wait_for_timeout(900); pg2.screenshot(path=f"{out}/06_teacher.png")
    print("raw shots done"); b.close()
