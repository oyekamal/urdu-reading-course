#!/usr/bin/env python3
"""Screens in .audit/wordimg/final3 -> design/words/gallery.html (one self-contained page, screenshots embedded as WebP)."""
import base64, io, os, json
from PIL import Image
R = os.path.expanduser('~/Documents/free_work/urdu-reading-course/.audit/wordimg/final3'); OUT = os.path.expanduser('~/Documents/free_work/urdu-reading-course/design/words/gallery.html')
def img(p, w=420):
    im = Image.open(f'{R}/{p}').convert('RGB'); im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS); b = io.BytesIO(); im.save(b, 'WEBP', quality=84)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
S = [
 ('First lesson', 'The very first word. The child reads بابا, then the picture shows what it means.', [('onb/25_demo_word.png', 'Read it'), ('onb/26_demo_word_read.png', 'Picture appears'), ('onb/27_demo_check.png', 'Which one says baba?'), ('onb/29_value.png', 'Share card preview')]),
 ('Lessons', 'Letter lesson with an example word, and the word cards.', [('letter_nun.png', 'Letter lesson'), ('words_light.png', 'Word cards'), ('words_light_scrolled.png', 'More cards'), ('words_2.png', 'Build the word')]),
 ('Dark mode and small phones', 'The picture tile stays light in dark mode so outlines stay readable. Cards hold up at 360 px wide.', [('words_dark.png', 'Dark'), ('words_dark_scrolled.png', 'Dark, scrolled'), ('words_small.png', 'Small phone'), ('words_small_scrolled.png', 'Small, scrolled')]),
 ('Share card', 'The image a family member receives when a child shares their first word.', [('share_card.png', '1080 × 1350')]),
]
sec = ''
for t, d, items in S:
    figs = ''.join(f'<figure><img src="{img(p, 600 if "share" in p else 420)}" alt="{c}" loading="lazy"><figcaption>{c}</figcaption></figure>' for p, c in items)
    sec += f'<section><h2>{t}</h2><p>{d}</p><div class="row">{figs}</div></section>'
html = '''<title>Urdu Qaida With Pictures</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&display=swap">
<style>
/* Layout: one band per area of the app, phone screenshots in a wrapping row. Palette from the app itself. */
:root{--bg:#FBF6EC;--ink:#1E2F55;--muted:#5C6985;--line:#E6DDCB;--teal:#00756B;--card:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121C33;--ink:#EAF0FF;--muted:#9DAACB;--line:#2C3C60;--teal:#2FB8A9;--card:#1B2946;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121C33;--ink:#EAF0FF;--muted:#9DAACB;--line:#2C3C60;--teal:#2FB8A9;--card:#1B2946;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:16px/1.5 "Fredoka",system-ui,sans-serif;padding-inline:max(16px,env(safe-area-inset-left,0px)) max(16px,env(safe-area-inset-right,0px));padding-block:24px 56px}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:30px;font-weight:600;margin:0 0 6px;text-wrap:balance}
.lede{color:var(--muted);margin:0 0 8px;max-width:62ch}
.stats{display:flex;gap:10px 22px;flex-wrap:wrap;margin:14px 0 6px;font-variant-numeric:tabular-nums}.stats b{color:var(--teal);font-size:22px;font-weight:600}.stats span{color:var(--muted);font-size:14px}
section{margin-top:34px}h2{font-size:20px;font-weight:600;margin:0}section p{color:var(--muted);margin:2px 0 14px;max-width:62ch}
.row{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start}
figure{margin:0;width:min(100%,260px)}figure img{display:block;width:100%;height:auto;border-radius:22px;border:1.5px solid var(--line);background:var(--card)}
section:last-of-type figure{width:min(100%,380px)}
figcaption{font-size:13px;color:var(--muted);margin-top:6px;text-align:center}
</style>
<body><div class="wrap">
<h1>Urdu Qaida With Pictures</h1>
<p class="lede">Version 0.12.0. Words now carry a picture so a child sees what they are reading. These are real screenshots of the updated app.</p>
<div class="stats"><div><b>760</b> <span>of 1,030 words have a picture</span></div><div><b>38</b> <span>hand-drawn in the app style</span></div><div><b>3</b> <span>critic rounds on the real screens</span></div></div>
''' + sec + '</div></body>'
open(OUT, 'w').write(html); print(len(html) // 1024, 'KB')
