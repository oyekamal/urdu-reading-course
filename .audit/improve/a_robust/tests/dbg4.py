from common import *
with sync_playwright() as p:
    b = p.chromium.launch(); ctx, pg = newpage(b); quick_profile(pg, 'Zed')
    d = pg.evaluate('__dump()'); print([(x['name'], x['updatedAt']) for x in d['profiles']], pg.evaluate('Date.now()'))
