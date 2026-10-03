import json,re,os
ROOT=os.path.expanduser('~/Documents/free_work/urdu-reading-course')
L=json.load(open(ROOT+'/data/letters.json',encoding='utf8'))['letters']; BY={l['ch'] for l in L}
U=json.load(open(ROOT+'/data/units.json',encoding='utf8'))['units']
MARKS=re.compile('[ً-ْٰـ]'); EXTRA=set('ءئؤآۃ')
bad=[];n=0;homo=[]
HOM={'س':'s','ث':'s','ص':'s','ز':'z','ذ':'z','ض':'z','ظ':'z','ت':'t','ط':'t','ہ':'h','ح':'h','ع':'a','ا':'a'}
for u in U:
    keys={c for x in U if x['n']<u['n'] for c in x['letters'] if c in BY}|{c for c in u['letters'] if c in BY}
    if u['n']>=10: keys|=EXTRA
    for w in u['words']:
        known=keys|{'ـ'}
        sp=all(c in known or MARKS.match(c) for c in w[0])
        if not sp: continue
        n+=1; b=MARKS.sub('',w[0])
        if not all(c in keys for c in b): bad.append((u['n'],w[0],[c for c in b if c not in keys]))
        # two taught homophone-class letters in the word => ear alone cannot give the spelling
        amb=[c for c in b if HOM.get(c,'a')!='a' and sum(1 for k in keys if HOM.get(k)==HOM[c])>1]
        if amb: homo.append((u['n'],w[0],w[1],''.join(amb)))
print('spellable words checked',n,'| not typeable with the dictation keyboard:',bad)
print('dictation words containing a homophone-class letter (ear cannot pick the spelling):',len(homo),homo[:12])
