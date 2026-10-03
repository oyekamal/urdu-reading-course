import os, json, sys
from playwright.sync_api import sync_playwright
PORT = os.environ.get('PORT', '5431')
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
URL = f'http://localhost:{PORT}/?skiponb'
HERE = os.path.dirname(os.path.abspath(__file__))
def bare(p, w=390, h=800):
    b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': w, 'height': h}); pg = ctx.new_page()
    pg.errors = []; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept())
    pg.goto(URL); pg.wait_for_timeout(1500); return b, pg
def real_errors(pg): return [e for e in pg.errors if 'srLine' not in e]
def fresh(p, name='Vee', w=390, h=800):
    b, pg = bare(p, w, h)
    pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', name); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2300)
    return b, pg
def save(name, obj): json.dump(obj, open(os.path.join(HERE, name), 'w'), ensure_ascii=False, indent=1)
INIT = "const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__plays=(window.__plays||[]);if(!this.src.includes('/ui/')){window.__plays.push(this.src)}return _p.call(this)}"
def fresh2(p, name='Vee', w=390, h=800):
    b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': w, 'height': h}); pg = ctx.new_page()
    pg.errors = []; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept()); pg.add_init_script(INIT)
    pg.goto(URL); pg.wait_for_timeout(1500)
    pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', name); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2300)
    return b, pg
def tamper(pg, passed_upto=-1, lessons_done=None, cur_unit=None):
    """mark units 0..passed_upto passed; lessons_done = {unitN: [lesson ids]}"""
    pg.evaluate("""async ([upto, ld]) => { const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0};
      for (let n=0;n<=upto;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}};
      for (const [n,ids] of Object.entries(ld||{})) { pr.units[n]={...(pr.units[n]||{}),lessons:Object.fromEntries(ids.map(i=>[i,Date.now()]))}; }
      await db.put('progress',pr); }""", [passed_upto, lessons_done or {}])
    pg.reload(); pg.wait_for_timeout(2500)
def click(pg, sel): pg.evaluate('s=>document.querySelector(s).click()', sel)
