import json, os, time
from playwright.sync_api import sync_playwright
OUT = '/home/oye/Documents/free_work/urdu-reading-course/.audit/validation/perf_robust/evidence'
VP = {'width': 390, 'height': 844}
EXE = '/home/oye/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'

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
