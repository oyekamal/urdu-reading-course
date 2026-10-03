import json,re,subprocess,sys,unicodedata
D='/home/oye/Documents/free_work/urdu-reading-course/'
U=json.load(open(D+'data/units.json'))['units']
def base(s): return ''.join(c for c in s if 'ء'<=c<='ي' or c in 'ٹپچڈڑژکگںھہیےۓ' ) # base letters, drop marks
def base2(s): return ''.join(c for c in s if unicodedata.category(c)=='Lo')
def txt(f): return subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout
bad=0
for n in range(1,12):
    f=D+f'mobile/public/pdf/u{n:02d}_match.pdf'
    t=txt(f)
    pages=t.split('\f')
    rows=[]
    for pg in pages:
        lines=pg.split('\n')
        for i,l in enumerate(lines):
            m=re.match(r'^\s*(\d+)\s*$',l.strip()) 
            # number on its own line at the right, urdu above
    # simpler: collect urdu tokens in order & glosses
    words=[];gl={}
    for pg in pages:
        lines=[l for l in pg.split('\n')]
        k=0
        for i,l in enumerate(lines):
            s=l.strip()
            if re.fullmatch(r'\d+',s):
                # urdu word on previous nonblank line OR same line prior
                j=i-1
                while j>=0 and not lines[j].strip(): j-=1
                words.append((int(s),lines[j].strip()))
            m=re.match(r'^([a-j])\s+(.+)$',s)
            if m: gl[m.group(1)]=m.group(2).strip()
            m=re.search(r'(\d+)\s*$',s)
    print(n,len(words),len(gl))
    # find key
    kt=[p for p in pages if 'answers' in p.lower() or 'Answers' in p]
    print('   keypages in match pdf:',len(kt))
