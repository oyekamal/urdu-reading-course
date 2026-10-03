import os, json, re
from playwright.sync_api import sync_playwright
PORT = os.environ.get('PORT', '5391')
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
HERE = os.path.dirname(os.path.abspath(__file__))
INIT = "const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__plays=(window.__plays||[]);if(!this.src.includes('/ui/')){window.__last=this.src;window.__plays.push(this.src)}return _p.call(this)}"
js = lambda pg, h: pg.evaluate('e=>e.click()', h)
def fresh(p, name='Zee', track=None):
    b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': 390, 'height': 800}); pg = ctx.new_page()
    pg.errors = []; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept()); pg.add_init_script(INIT)
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2000); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', name); pg.click('button:has-text("Start")'); pg.wait_for_selector('.bottom button',timeout=30000); pg.wait_for_timeout(1500)
    return b, pg
def bare(p):
    b = p.chromium.launch(executable_path=EXE); pg = b.new_context(viewport={'width': 390, 'height': 800}).new_page(); pg.errors = []; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:200]))
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2000); return b, pg
