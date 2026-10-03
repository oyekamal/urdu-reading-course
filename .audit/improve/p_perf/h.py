import json, os, time
from playwright.sync_api import sync_playwright
OUT = '/tmp/claude-1000/p_perf/out'
VP = {'width': 390, 'height': 844}
EXE = '/home/oye/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'

def click(pg, sel, t=8000):
    pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=t))

def quick_profile(pg, base, name='Zara', track='child'):
    """skiponb -> Just me -> add learner (fast path to the learner home)."""
    pg.goto(base + '?skiponb'); pg.wait_for_timeout(1500)
    click(pg, 'text=Just me'); pg.wait_for_timeout(300)
    click(pg, 'text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', name)
    if track != 'child': pg.select_option('select >> nth=0', track)
    click(pg, "button:has-text('Start')"); pg.wait_for_timeout(1500)

def onboard_child(pg, base, name='Zara', fast=True):
    pg.goto(base); pg.wait_for_timeout(2200)
    click(pg, "text=Let's begin"); pg.wait_for_timeout(500)
    click(pg, '.ob-sleeper'); pg.wait_for_timeout(2600)
    click(pg, '.ob-sw >> nth=0'); click(pg, '.ob-cta')
    click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', name)
    click(pg, '.ob-cta'); click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500)
    click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500); click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
    click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); click(pg, '.ob-cta')
    pg.wait_for_timeout(900); click(pg, '.ob-cta')
    click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500); pg.wait_for_timeout(3500)
    click(pg, '.ob-cta'); click(pg, '.ob-cta')
    for t in ['ب', 'ا', 'ب']:
        click(pg, f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
    click(pg, '.ob-cta'); click(pg, 'text=Join them'); pg.wait_for_timeout(1500); click(pg, '.ob-cta')
    click(pg, '.ob-word'); pg.wait_for_timeout(1400); click(pg, '.ob-cta')
    click(pg, ".ob-choices .tile:text-is('بابا')"); pg.wait_for_timeout(1300); click(pg, '.ob-cta')
    pg.wait_for_timeout(1000); click(pg, '.ob-foot .btn-primary'); pg.wait_for_timeout(900); click(pg, '.ob-cta')
    click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500); click(pg, '.ob-cta'); pg.wait_for_timeout(2000)

def walk_onboarding(pg, name='Zara', max_steps=70):
    """Generic onboarding walker (the old onboard_child helper is stale): clicks whatever the current screen offers until the Today tab bar appears. Returns steps taken."""
    for i in range(max_steps):
        if pg.query_selector('.bottom'): return i
        did = pg.evaluate("""([name, idx])=>{
          const vis=e=>e&&e.getClientRects().length>0&&!e.disabled;
          const q=(s)=>[...document.querySelectorAll(s)].filter(vis);
          const nm=document.querySelector('#ob-name'); if(vis(nm)&&!nm.value){nm.value=name;nm.dispatchEvent(new Event('input',{bubbles:true}));return 'name'}
          let e=q('.ob-sleeper')[0]; if(e){e.click();return 'sleeper'}
          e=q('.ob-sw')[0]; if(e&&!document.querySelector('.ob-sw.on,.ob-sw.sel,.ob-sw[aria-pressed=true]')){e.click();return 'swatch'}
          e=q('.ob-opt').find(o=>/my child/i.test(o.textContent)); if(e){e.click();return 'child'}
          const opts=q('.ob-opt'); if(opts.length&&!document.querySelector('.ob-opt.on,.ob-opt.sel,.ob-opt[aria-pressed=true],.ob-opt[aria-checked=true]')){opts[0].click();return 'opt'}
          const tiles=q('.ob-choices .tile'); if(tiles.length){const t=tiles[idx%tiles.length];if(t){t.click();return 'tile'}}
          e=q('.ob-word')[0]; if(e&&!e.dataset.cl){e.dataset.cl=1;e.click();return 'word'}
          e=q('button').find(b=>/join them/i.test(b.textContent)); if(e){e.click();return 'join'}
          e=q('.ob-cta, .ob-foot .btn-primary')[0]; if(e){e.click();return 'cta'}
          e=q('button.btn-primary, .btn-primary')[0]||q('button').find(b=>/check|continue|next|start|done|finish|go/i.test(b.textContent)); if(e){e.click();return 'btn'}
          return null}""", [name, i])
        pg.wait_for_timeout(900 if did in ('tile', 'word', 'sleeper', 'cta') else 500)
    return -1
