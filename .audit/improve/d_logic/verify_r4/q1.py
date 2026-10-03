import json
from lib import *
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    print(pg.evaluate("""async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();return Cn.C.units.map(u=>u?[u.n,u.letters.length,u.words.length]:null)}"""))
    b.close()
