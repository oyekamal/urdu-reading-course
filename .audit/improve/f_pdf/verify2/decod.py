import json,re,subprocess,glob,os,unicodedata
D=os.path.expanduser('~/Documents/free_work/urdu-reading-course/')
U=json.load(open(D+'data/units.json'))['units']
L=json.load(open(D+'data/letters.json'))['letters']
taught=lambda n:set(c for x in U if x['n']<=n for c in x['letters'])
allow=set('ءآؤۃۓ')
for n in range(0,13):
  for kind in ['trace','lookalike','join','match','reading','dictation','check','guide','pack']:
    f=D+f'mobile/public/pdf/u{n:02d}_{kind}.pdf'
    if not os.path.exists(f): continue
    pages=subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout.split('\f')
    for pi,pg in enumerate(pages):
        lines=pg.split('\n')
        first=True;out=set()
        for l in lines:
            ar=[c for c in l if unicodedata.category(c)=='Lo' and '؀'<=c<='ۿ']
            if not ar: continue
            if first: first=False;continue   # header
            out|=set(ar)
        extra=out-taught(n)-allow-set('ٱ')
        if n>=10: extra-=set('ٰ')
        if extra: print(n,kind,'page',pi+1,''.join(sorted(extra)))
