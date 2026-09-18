#!/usr/bin/env python3
"""For every flagged clip key (one per line in a file) synthesize alternative renderings so a listener can pick:
  A  main voice, text alone            B  main voice, carrier "یہ لفظ X" cut with duration predictor
  C  Meta baseline voice, text alone   D  Meta baseline, carrier cut
  E  Meta Roman-script model from the romanised form (words only)
Writes assets/audio/_repair/<kind>__<id>/<A..E>.mp3 and app/repair_pick.html (audio inline, picks saved to the
artifact db doc picks/current when opened on claude.ai, and to localStorage). Sentences get A, C and F (main voice,
second random seed) instead of carrier variants."""
import json, os, sys, base64, subprocess, numpy as np, soundfile as sf, torch
from transformers import VitsModel, AutoTokenizer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/assets/audio/_repair"; SR = 16000
MAIN = "sharjeel103/mms-tts-urdu-finetune"; BASE = "facebook/mms-tts-urd-script_arabic"; LATIN = "facebook/mms-tts-urd-script_latin"
M = {f"{j['kind']}/{j['id']}": j for j in json.load(open(f"{ROOT}/assets/audio/manifest.json", encoding="utf8"))}
L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8")); U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
ROMAN = {}
for u in U:
    for w in u["words"] + u["sentences"]: ROMAN[w[0]] = w[1]
for l in L["letters"]: ROMAN[l["example"][0]] = l["example"][1]; ROMAN[l["name_ur"]] = l["name"]
ROMAN.update({a[2]: a[3] for a in L["aspirates"]})
for i, w in enumerate(L["sight_words"]): ROMAN.setdefault(w, None)
cap = {}; _ceil = torch.ceil
def rec(x):
    y = _ceil(x); cap["dur"] = y.detach(); return y
torch.ceil = rec
def norm(a): return (a / max(1e-6, abs(a).max()) * 0.9).astype(np.float32)
def pad(a): return np.concatenate([np.zeros(int(0.15 * SR)), a, np.zeros(int(0.25 * SR))]).astype(np.float32)
def load(name): return VitsModel.from_pretrained(name).eval(), AutoTokenizer.from_pretrained(name)
def alone(m, tok, text, seed=0):
    torch.manual_seed(seed)
    with torch.no_grad(): return pad(norm(m(**tok(text, return_tensors="pt")).waveform[0].numpy()))
def carrier(m, tok, text):
    torch.manual_seed(0); enc = tok(f"یہ لفظ {text}", return_tensors="pt")
    with torch.no_grad(): a = norm(m(**enc).waveform[0].numpy())
    dur = cap["dur"][0, 0] if cap["dur"].dim() == 3 else cap["dur"][0]
    chars = tok.convert_ids_to_tokens(enc.input_ids[0].tolist()); sp = [i for i, c in enumerate(chars) if c == " "]
    hop = int(np.prod(m.config.upsample_rates)); t0 = int(dur[: sp[-1] + 1].sum().item()) * hop if sp else 0
    return pad(a[max(0, t0 - 480):])
def romanize(r):
    for a, b in [("ā","aa"),("ī","ee"),("ū","oo"),("ṭ","t"),("ḍ","d"),("ṛ","r"),("ṉ","n"),("ḥ","h"),("ṣ","s"),("ẕ","z"),("z̤","z"),("t̤","t"),("k͟h","kh"),("g͟h","gh"),("s̱","s"),("ʻ",""),("ʾ",""),("’",""),("'","")]: r = r.replace(a, b)
    return r
def mp3(path_wav):
    subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-i", path_wav, "-q:a", "4", path_wav[:-4] + ".mp3"], check=True)
    return "data:audio/mpeg;base64," + base64.b64encode(open(path_wav[:-4] + ".mp3", "rb").read()).decode()

def main():
    keys = [k.strip() for k in open(sys.argv[1], encoding="utf8") if k.strip()]
    mm, mt = load(MAIN); bm, bt = load(BASE); lm, lt = load(LATIN)
    rows = []
    for k in keys:
        j = M[k]; text = j["text"]; d = f"{OUT}/{k.replace('/', '__')}"; os.makedirs(d, exist_ok=True)
        var = {}
        if j["kind"] == "sentences":
            var["A"] = alone(mm, mt, text); var["C"] = alone(bm, bt, text); var["F"] = alone(mm, mt, text, seed=7)
        else:
            var["A"] = alone(mm, mt, text); var["B"] = carrier(mm, mt, text); var["C"] = alone(bm, bt, text); var["D"] = carrier(bm, bt, text)
            r = ROMAN.get(text)
            if r: var["E"] = alone(lm, lt, romanize(r))
        srcs = {}
        for v, a in var.items():
            w = f"{d}/{v}.wav"; sf.write(w, a, SR); srcs[v] = mp3(w)
        rows.append((k, text, ROMAN.get(text) or "", srcs)); print(k, text, "".join(var), flush=True)
    labels = {"A": "main voice, alone", "B": "main voice, from phrase", "C": "Meta voice, alone", "D": "Meta voice, from phrase", "E": "Roman-script model", "F": "main voice, retake"}
    body = "".join(f'<tr data-k="{k}"><td>{k}</td><td class="ur">{t}</td><td>{r}</td>' + "".join(f'<td><button onclick="p(this)" data-s="{s}">▶ {v}</button></td>' if v in srcs else "<td></td>" for v, s in [(v, srcs.get(v)) for v in "ABCDEF"]) + f'<td><select id="pick-{k}"><option value="">pick</option>' + "".join(f"<option>{v}</option>" for v in srcs) + '<option value="none">none</option></select></td></tr>' for k, t, r, srcs in rows)
    html = f'''<meta charset="utf-8"><title>Urdu Audio Repair Picks</title>
<style>body{{font:14px system-ui;margin:0;padding:16px;background:#f4f6f8;color:#14213d}}table{{border-collapse:collapse;width:100%}}td,th{{padding:6px;border-bottom:1px solid #d9dee6;text-align:left;vertical-align:middle}}.ur{{font-family:"Noto Naskh Arabic",serif;font-size:24px;direction:rtl}}button{{font:inherit;padding:4px 8px;border-radius:6px;border:1px solid #0f7b6c;background:#fff;color:#0f7b6c;cursor:pointer}}select{{font:inherit}}th{{position:sticky;top:0;background:#f4f6f8}}.tablewrap{{overflow-x:auto}}</style>
<h1>Pick the correct rendering for each flagged clip</h1>
<p>{len(rows)} clips. {" · ".join(f"<b>{v}</b> {lab}" for v, lab in labels.items())}. Choose <b>none</b> if no version is right. Picks save automatically. <span id="sync">connecting…</span></p>
<div class="tablewrap"><table><tr><th>clip</th><th>text</th><th>say</th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th><th>F</th><th>best</th></tr>{body}</table></div>
<script>
const a=new Audio();function p(b){{a.src=b.dataset.s;a.play()}}
const picks=JSON.parse(localStorage.getItem('urc.repairPicks')||'{{}}');const st=document.getElementById('sync');let ref=null,pending=null;
function paint(){{for(const s of document.querySelectorAll('select')){{const k=s.id.slice(5);if(picks[k])s.value=picks[k];}}}}
paint();
document.querySelectorAll('select').forEach(s=>s.onchange=()=>{{const k=s.id.slice(5);if(s.value)picks[k]=s.value;else delete picks[k];localStorage.setItem('urc.repairPicks',JSON.stringify(picks));save();}});
function save(){{clearTimeout(pending);pending=setTimeout(async()=>{{if(!ref)return;try{{await ref.set({{picks,count:Object.keys(picks).length,updatedAt:new Date().toISOString()}});st.textContent='saved to Kamil ('+Object.keys(picks).length+' picks)';}}catch(e){{st.textContent='(save failed: '+(e.code||e.message)+')';}}}},500);}}
(async()=>{{try{{const db=await (window.claude?.use?.('db'));if(!db){{st.textContent='(picks kept in this browser only — use Export)';return;}}ref=db.doc('picks/current');const snap=await ref.get();if(snap.exists)Object.assign(picks,snap.data().picks||{{}});paint();st.textContent='saved to Kamil ('+Object.keys(picks).length+' picks)';if(Object.keys(picks).length)save();}}catch(e){{st.textContent='(db error: '+(e.code||e.message)+')';}}}})();
</script>'''
    open(f"{ROOT}/app/repair_pick.html", "w", encoding="utf8").write(html)
    print("wrote app/repair_pick.html", os.path.getsize(f"{ROOT}/app/repair_pick.html") // 1024, "KB")

if __name__ == "__main__":
    main()
