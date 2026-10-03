from lib import *
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for style in ('nastaliq','naskh'):
        for ch in 'ڈڑ':
            pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(500)
            pg.locator('.trace-wrap').screenshot(path=f'dal_{style}_{ch}.png')
    b.close()
