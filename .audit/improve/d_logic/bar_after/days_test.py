import json,os
from playwright.sync_api import sync_playwright
EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_page(); pg.goto('http://localhost:5188/?skiponb'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""async()=>{const S=await import('/src/session.js');const {db}=await import('/src/db.js');const pid='days-1';
      const D=(y,m,d,h,mi)=>new Date(y,m,d,h,mi).getTime(); const ts=[D(2026,9,1,23,59),D(2026,9,2,0,1),D(2026,9,2,12,0),D(2026,9,2,12,5),D(2026,9,10,9,0)];
      for(const t of ts) await db.put('attempts',{id:'d'+t,profileId:pid,unit:1,drill:'x',item:'a',correct:true,ms:1,ts:t});
      const out={days:await S.streak(pid),expected:3}; 
      // attempts that are wrong still count as a practised day; lessons with no attempts (rules / listen-only) do not
      return out}""")
    print(r); json.dump(r,open('days_test.json','w')); b.close()
