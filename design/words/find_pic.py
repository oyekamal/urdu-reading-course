#!/usr/bin/env python3
"""Search the free picture sets by English keyword. Sets (cloned in ~/.cache/urdu-word-src):
  om = OpenMoji colour (CC BY-SA 4.0, thick outline, closest to Marko)   tw = Twemoji (CC BY 4.0, same emoji, softer)
  mb = Mulberry Symbols (CC BY-SA 2.0 UK, AAC pictograms, best for actions/feelings/abstract words)
  python3 find_pic.py "dog" [-n 12] [--set om,tw,mb]     -> id | set | name | tags
  python3 find_pic.py --build                              -> rebuilds the index (design/words/index.json)
ids look like om:1F415, tw:1f415, mb:dog.  File path: pic_path(id)."""
import json, os, re, sys
SRC = os.path.expanduser('~/.cache/urdu-word-src'); HERE = os.path.dirname(os.path.abspath(__file__)); IDX = f'{HERE}/index.json'
def pic_path(i):
    s, k = i.split(':', 1)
    return {'om': f'{SRC}/openmoji/color/svg/{k}.svg', 'tw': f'{SRC}/twemoji/assets/svg/{k}.svg', 'mb': f'{SRC}/mulberry-symbols/EN/{k}.svg'}[s]
def build():
    out = []
    for e in json.load(open(f'{SRC}/openmoji/data/openmoji.json')):
        if e.get('skintone') or e['group'] in ('flags', 'component', 'extras-unicode'): continue
        hx = e['hexcode']; name = e['annotation']; tags = ' '.join(filter(None, [e.get('tags', ''), e.get('openmoji_tags', '')])).replace(',', '')
        if os.path.exists(pic_path('om:' + hx)): out.append({'id': 'om:' + hx, 'name': name, 'tags': tags, 'group': e['group']})
        tw = '-'.join(p.lower() for p in hx.split('-') if p != 'FE0F')
        if os.path.exists(pic_path('tw:' + tw)): out.append({'id': 'tw:' + tw, 'name': name, 'tags': tags, 'group': e['group']})
    for f in sorted(os.listdir(f'{SRC}/mulberry-symbols/EN')):
        if f.endswith('.svg'): k = f[:-4]; out.append({'id': 'mb:' + k, 'name': k.replace('_', ' '), 'tags': '', 'group': 'mulberry'})
    json.dump(out, open(IDX, 'w'), ensure_ascii=False); print(len(out), 'pictures indexed')
def search(q, n=12, sets=('om', 'tw', 'mb')):
    idx = json.load(open(IDX)); ws = re.findall(r'\w+', q.lower()); res = []
    for p in idx:
        if p['id'][:2] not in sets: continue
        name = p['name'].lower(); tags = p['tags'].lower(); sc = 0
        for w in ws:
            if re.search(rf'\b{w}\b', name): sc += 10 if name == q.lower() else 6
            elif w in name: sc += 3
            if re.search(rf'\b{w}\b', tags): sc += 2
        if sc: res.append((sc - len(name) * 0.01, p))
    return [p for _, p in sorted(res, key=lambda x: -x[0])[:n]]
if __name__ == '__main__':
    a = sys.argv[1:]
    if '--build' in a: build(); sys.exit()
    n = int(a[a.index('-n') + 1]) if '-n' in a else 12; sets = tuple(a[a.index('--set') + 1].split(',')) if '--set' in a else ('om', 'tw', 'mb')
    for p in search(a[0], n, sets): print(f"{p['id']} | {p['name']} | {p['tags'][:60]}")
