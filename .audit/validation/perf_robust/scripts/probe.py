from h import *
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='block'); pg = ctx.new_page()
    quick_profile(pg, 'http://localhost:5301/')
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(1000)
    print(pg.evaluate("()=>[...document.querySelectorAll('button')].map(b=>(b.getAttribute('aria-label')||b.innerText).trim().slice(0,20)+'|'+b.className).join('\\n')"))
    print(pg.evaluate("()=>!!document.querySelector('.bottom')"))
    b.close()
