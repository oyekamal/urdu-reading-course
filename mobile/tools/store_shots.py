# Raw phone screenshots for the store listing (1080-wide). Usage: python3 tools/store_shots.py [port]
import sys, re; from playwright.sync_api import sync_playwright
port=sys.argv[1] if len(sys.argv)>1 else '5188'; out='../store/raw'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":412,"height":880}, device_scale_factor=2.62); pg=ctx.new_page(); pg.on("dialog", lambda d: d.accept())
    pg.goto(f"http://localhost:{port}/"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/08_mode.png")
    pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]","Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
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
    pg.wait_for_selector(".nastaliq", timeout=8000); pg.evaluate("""()=>{const card=document.querySelector('.nastaliq').closest('.card');const main=card.parentElement;[...main.children].forEach(c=>{if(c!==card&&!c.matches('.row,.bottom'))c.style.display='none'});card.querySelector('.words')?.remove();[...card.querySelectorAll('h2,p')].forEach(x=>x.remove());const h=document.createElement('h2');h.textContent='Naskh for learning, Nastaliq for print';card.prepend(h);window.scrollTo(0,0)}"""); pg.wait_for_timeout(400); pg.screenshot(path=f"{out}/05_nastaliq.png")
    # teacher assess
    ctx2=b.new_context(viewport={"width":412,"height":880}, device_scale_factor=2.62); pg2=ctx2.new_page(); pg2.on("dialog", lambda d: d.accept()); pg2.goto(f"http://localhost:{port}/"); pg2.wait_for_timeout(1500)
    pg2.click("text=My class"); pg2.wait_for_timeout(400); pg2.fill("input[placeholder='Your name']","Ms Sana"); pg2.fill("input[placeholder='4-digit PIN']","1234"); pg2.click("button:has-text('Save')"); pg2.wait_for_timeout(600)
    pg2.click("button:has-text('Teacher')"); pg2.wait_for_timeout(300); pg2.fill("input[type=password]","1234"); pg2.click("button:has-text('Unlock')"); pg2.wait_for_timeout(1200)
    for n,g in [("Ayesha","1"),("Bilal","2"),("Hira","1")]:
        pg2.fill("input[placeholder=Name]",n); pg2.click("button:has-text('Add child')"); pg2.wait_for_timeout(400)
    pg2.evaluate("""async()=>{const {db,uid}=await import('/src/db.js');const {bandFor}=await import('/src/content.js');const ps=(await db.all('profiles')).filter(p=>p.kind!=='teacher');const DAY=86400000;const data=[[38,6,14,31,3],[52,9,22,64,5],[45,8,19,48,4]];
      ps.forEach(async(p,i)=>{for(let k=0;k<2;k++){const d=data[i];const cw=d[3]-(k?12:0);await db.put('assessments',{id:uid(),profileId:p.id,ts:Date.now()-(k?35:2)*DAY,by:'Ms Sana',letters:d[0]-(k?8:0),nonwords:d[1]-(k?2:0),words:d[2]-(k?5:0),orf:{cwpm:cw,seconds:60,errors:3},comp:d[4]-(k?1:0),band:bandFor(cw)});}})}"""); pg2.wait_for_timeout(800)
    pg2.click(".tab:has-text('Class')"); pg2.wait_for_timeout(600); pg2.click(".tab:has-text('Assess')"); pg2.wait_for_timeout(900); pg2.screenshot(path=f"{out}/06_teacher.png")
    print("raw shots done"); b.close()
