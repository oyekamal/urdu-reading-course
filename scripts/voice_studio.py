#!/usr/bin/env python3
"""Local voice-recording studio: record Kamal's own voice for every audio clip in the course,
one line at a time, in the browser, saved straight into the app in the exact format
scripts/import_recordings.py already produces (16kHz mono wav+mp3, silence-trimmed, peak-
normalised, lead/tail padded) — so a normal recording session needs no separate import step.

  python3 scripts/voice_studio.py [port]        # default port 8420
  then open http://localhost:8420/ in Chrome or Firefox (mic access needs http://localhost)

There are 490 clips total across 10 kinds: names 39, words 39, syllables 90, aspirates 11,
diacritics 12, units 220, sentences 33, sight 20, numerals 10, ui 16.

Every clip already recorded (by this tool or by scripts/import_recordings.py) shows a check
in the list and can be replayed or re-recorded. Progress is the source of truth already used
everywhere else: data/audio_overrides.json — nothing new to track. After a session, run
`python3 scripts/build_app.py` to bake the new audio into the app.
"""
import json
import os
import sys
import tempfile
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_recordings import SR, ffmpeg_decode_to_wav, load_overrides, process_array, save_overrides, write_clip  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = f"{ROOT}/assets/audio/manifest.json"
OVERRIDES = f"{ROOT}/data/audio_overrides.json"
ASSETS = f"{ROOT}/assets/audio"
FONTS = {
    "NotoNaskhArabic.ttf": f"{ROOT}/assets/fonts/NotoNaskhArabic.ttf",
    "NotoNastaliqUrdu-Regular.ttf": f"{ROOT}/assets/fonts/NotoNastaliqUrdu-Regular.ttf",
}
MIN_CLIP_S = 0.2

UI_GLOSS = {
    "listen": "Listen", "tap_heard": "Tap what you heard", "tap_word": "Tap the word you heard",
    "look": "Look how this letter changes in a word", "trace": "Trace it with your finger",
    "blend": "Blend the letter and the sound", "build": "Build the word from the letters",
    "read": "Read it aloud", "write": "Write the word you heard", "check": "A quick check now",
    "correct": "Correct!", "wrong": "Try again", "next": "Next", "done": "Well done, lesson finished",
    "unit_done": "Great! Unit finished, the next one is open", "welcome": "Come, let's learn to read Urdu",
}


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s)[:40]


def build_items():
    manifest = json.load(open(MANIFEST, encoding="utf8"))
    L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
    U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
    by_id = {l["id"]: l for l in L["letters"]}
    diacritics = {d["id"]: d for d in L["diacritics"]}
    aspirates = {slug(row[1]): row for row in L["aspirates"]}
    units_by_n = {u["n"]: u for u in U}
    items = []
    for m in manifest:
        kind, id_, text = m["kind"], m["id"], m["text"]
        big, roman, en, note = text, None, None, None
        if kind == "names":
            l = by_id.get(id_)
            if l:
                roman, note = l["name"], l.get("hint")
        elif kind == "words":
            l = by_id.get(id_)
            if l and len(l.get("example", [])) >= 3:
                roman, en = l["example"][1], l["example"][2]
        elif kind == "syllables":
            lid, _, tag = id_.rpartition("_")
            l = by_id.get(lid)
            if l:
                roman = l["name"] + " + " + {"a": "ā (long a)", "i": "ī (long i)", "u": "ū (long u)"}.get(tag, tag)
        elif kind == "aspirates":
            row = aspirates.get(id_)
            if row and len(row) >= 5:
                roman, en = row[3], row[4]
                note = "Say the word naturally — the extra breath after the letter is what this teaches, don't force it."
        elif kind == "diacritics":
            if id_.endswith("_ex"):
                d = diacritics.get(id_[:-3])
                if d and len(d.get("example", [])) >= 3:
                    roman, en = d["example"][1], d["example"][2]
                    note = "Read exactly as the mark shows — this is the one place your voice fixes what the machine voice guessed."
            else:
                d = diacritics.get(id_)
                if d:
                    note = "Just the mark's name, clearly: " + d.get("sound", "")
        elif kind == "numerals":
            note = "Say it as a spoken number word — the way you'd say 'two' out loud, not a digit name."
        elif kind in ("units", "sentences"):
            n, _, idx = id_.partition("_")
            u = units_by_n.get(int(n[1:])) if n[1:].isdigit() else None
            if u:
                rows = u["words"] if kind == "units" else u["sentences"]
                i = int(idx)
                if i < len(rows):
                    row = rows[i]
                    if len(row) >= 4 and row[3] and row[3] != row[0]:
                        big = row[3]
                        note = "Read the marked form shown big — the short vowel is the point, even though the screen may hide it later."
                    if len(row) > 1:
                        roman = row[1]
                    if len(row) > 2:
                        en = row[2]
        elif kind == "sight":
            note = "Read naturally, calm and clear — a third of any Urdu text is these twenty words."
        elif kind == "ui":
            en = UI_GLOSS.get(id_)
            note = "Say this like a warm hint to a child using the app, not a robot's command."
        items.append({"kind": kind, "id": id_, "text": text, "big": big, "roman": roman, "en": en, "note": note})
    return items


ITEMS = build_items()
KIND_ORDER = ["names", "words", "syllables", "aspirates", "diacritics", "units", "sentences", "sight", "numerals", "ui"]


def state_payload():
    ovr = load_overrides(OVERRIDES)
    out = []
    for it in ITEMS:
        key = f"{it['kind']}/{it['id']}"
        o = ovr.get(key)
        row = dict(it)
        row["recorded"] = bool(o and o.get("method") == "human")
        row["recordedBy"] = o.get("recordedBy") if o else None
        row["date"] = o.get("date") if o else None
        out.append(row)
    return out


HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voice Studio · Urdu Reading Course</title>
<style>
@font-face{font-family:"Naskh";src:url("/fonts/NotoNaskhArabic.ttf")}
:root{--paper:#F2F7F6;--card:#fff;--ink:#1E2F55;--muted:#5A6B84;--line:#D5E3E1;--accent:#1E9C8F;--accent-deep:#157A70;--gold:#F2A93B;--bad:#C74A3B;--good:#3E9A5E}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif;display:flex;height:100vh;overflow:hidden}
.side{width:270px;flex:none;background:var(--card);border-right:1px solid var(--line);display:flex;flex-direction:column}
.side h1{font-size:16px;margin:14px 14px 4px}
.side .top{padding:0 14px 10px;border-bottom:1px solid var(--line)}
.side input[type=text]{width:100%;padding:8px;border:1px solid var(--line);border-radius:8px;font:inherit;margin-top:6px}
.overall{padding:10px 14px;font-size:13px;color:var(--muted)}
.bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin-top:4px}.bar i{display:block;height:100%;background:var(--accent)}
.kinds{overflow-y:auto;flex:1}
.kind{display:flex;justify-content:space-between;padding:9px 14px;cursor:pointer;border-left:3px solid transparent}
.kind:hover{background:var(--paper)}.kind.active{background:var(--paper);border-left-color:var(--accent);font-weight:700}
.kind small{color:var(--muted);font-weight:400}
.list{overflow-y:auto;flex:1;border-top:1px solid var(--line)}
.row{display:flex;gap:8px;align-items:center;padding:6px 14px;cursor:pointer;font-size:13px}
.row:hover{background:var(--paper)}.row.cur{background:#DCF1EE}
.row .dot{width:9px;height:9px;border-radius:50%;background:var(--line);flex:none}.row.done .dot{background:var(--good)}
.row .t{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;direction:rtl;font-family:Naskh,serif}
main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;gap:18px;position:relative}
.count{position:absolute;top:16px;right:20px;color:var(--muted);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:0 6px 24px rgba(30,47,85,.08);padding:36px 48px;text-align:center;max-width:640px;width:100%}
.kindtag{display:inline-block;background:#DCF1EE;color:var(--accent-deep);border-radius:99px;padding:3px 12px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.big{font-family:Naskh,serif;direction:rtl;font-size:64px;line-height:1.5;margin:14px 0;color:var(--ink)}
.sub{color:var(--muted);font-size:15px}
.note{margin-top:10px;font-size:13px;color:var(--accent-deep);background:#DCF1EE;border-radius:10px;padding:8px 12px}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:center}
button{font:inherit;font-weight:700;border:2px solid var(--line);border-bottom-width:4px;background:var(--card);color:var(--ink);border-radius:14px;padding:10px 18px;cursor:pointer}
button:active{transform:translateY(2px);border-bottom-width:2px}
button:disabled{opacity:.4;cursor:default}
.rec{background:var(--bad);color:#fff;border-color:#a53a2e}
.rec.on{background:#8f2418;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.7}}
.go{background:var(--accent);color:#fff;border-color:var(--accent-deep)}
.gold{background:var(--gold);color:#1E2F55;border-color:#C9862A}
.timer{font-variant-numeric:tabular-nums;font-size:14px;color:var(--muted);min-width:48px}
.byrow{display:flex;gap:8px;align-items:center;font-size:13px;color:var(--muted)}
.byrow input{font:inherit;border:1px solid var(--line);border-radius:8px;padding:4px 8px}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--ink);color:#fff;padding:10px 18px;border-radius:12px;font-size:14px;opacity:0;transition:.25s;pointer-events:none}
.toast.show{opacity:1}
.hint{color:var(--muted);font-size:12px}
kbd{background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:1px 5px;font-size:11px}
</style></head>
<body>
<div class="side">
  <h1>Voice Studio</h1>
  <div class="top">
    <div class="byrow">Recorded by <input id="by" type="text" placeholder="your name" style="flex:1"></div>
    <input id="search" type="text" placeholder="search text or id…">
  </div>
  <div class="overall"><span id="overallLabel">0 / 490 recorded</span><div class="bar"><i id="overallBar" style="width:0%"></i></div></div>
  <div class="kinds" id="kinds"></div>
  <div class="list" id="list"></div>
</div>
<main>
  <div class="count" id="count"></div>
  <div class="card">
    <span class="kindtag" id="kindtag"></span>
    <div class="big" id="big"></div>
    <div class="sub" id="sub"></div>
    <div class="note" id="note" style="display:none"></div>
  </div>
  <div class="controls">
    <button id="prev">◀ Prev <kbd>←</kbd></button>
    <button class="rec" id="recBtn">● Record <kbd>space</kbd></button>
    <span class="timer" id="timer">0.0s</span>
    <button id="playBtn" disabled>▶ Play</button>
    <button class="go" id="saveBtn" disabled>Save &amp; next <kbd>enter</kbd></button>
    <button id="nextBtn">Next ▶ <kbd>→</kbd></button>
  </div>
  <div class="hint">Skip already-recorded items: <input type="checkbox" id="skipDone" checked> · <kbd>backspace</kbd> discards the take</div>
</main>
<div class="toast" id="toast"></div>
<audio id="player" style="display:none"></audio>
<script>
let ITEMS = [], cur = 0, curKind = 'all', mediaRecorder, chunks = [], recordedBlob = null, recordedMime = '';
const $ = s => document.querySelector(s);
const KIND_LABEL = {names:'Letter names',words:'Letter examples',syllables:'Syllables',aspirates:'Aspirates',diacritics:'Vowel marks',units:'Unit words',sentences:'Sentences',sight:'Sight words',numerals:'Numerals',ui:'App voice'};
const toast = m => { const t=$('#toast'); t.textContent=m; t.classList.add('show'); clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'),2000); };
const byName = () => localStorage.getItem('vs_by') || '';
$('#by').value = byName();
$('#by').oninput = e => localStorage.setItem('vs_by', e.target.value);

async function load() {
  ITEMS = await (await fetch('/api/items')).json();
  renderKinds(); renderList(); goto(cur);
}
function filtered() {
  const q = $('#search').value.trim().toLowerCase();
  return ITEMS.map((it,i)=>({...it,i})).filter(it => (curKind==='all'||it.kind===curKind) && (!q || it.text.includes(q) || it.id.toLowerCase().includes(q) || (it.roman||'').toLowerCase().includes(q)));
}
function renderKinds() {
  const counts = {}; ITEMS.forEach(it => { counts[it.kind] = counts[it.kind] || [0,0]; counts[it.kind][1]++; if (it.recorded) counts[it.kind][0]++; });
  const total = ITEMS.length, done = ITEMS.filter(i=>i.recorded).length;
  $('#overallLabel').textContent = `${done} / ${total} recorded`;
  $('#overallBar').style.width = Math.round(done/total*100) + '%';
  const order = ['names','words','syllables','aspirates','diacritics','units','sentences','sight','numerals','ui'];
  const html = [`<div class="kind${curKind==='all'?' active':''}" data-k="all"><span>All</span><small>${done}/${total}</small></div>`]
    .concat(order.map(k => `<div class="kind${curKind===k?' active':''}" data-k="${k}"><span>${KIND_LABEL[k]}</span><small>${(counts[k]||[0,0])[0]}/${(counts[k]||[0,0])[1]}</small></div>`));
  $('#kinds').innerHTML = html.join('');
  [...$('#kinds').children].forEach(el => el.onclick = () => { curKind = el.dataset.k; cur = 0; renderKinds(); renderList(); goto(0); });
}
function renderList() {
  const f = filtered();
  $('#list').innerHTML = f.map((it,j) => `<div class="row${it.recorded?' done':''}${j===cur?' cur':''}" data-j="${j}"><span class="dot"></span><span class="t">${it.text}</span></div>`).join('');
  [...$('#list').children].forEach((el,j) => el.onclick = () => goto(j));
}
function current() { return filtered()[cur]; }
function goto(j) {
  const f = filtered(); if (!f.length) return;
  cur = Math.max(0, Math.min(f.length-1, j));
  const it = f[cur];
  $('#kindtag').textContent = KIND_LABEL[it.kind] || it.kind;
  $('#big').textContent = it.big || it.text;
  $('#sub').innerHTML = [it.roman, it.en].filter(Boolean).join(' · ') || '&nbsp;';
  const note = $('#note'); if (it.note) { note.style.display='block'; note.textContent = it.note; } else note.style.display='none';
  $('#count').textContent = `${cur+1} / ${f.length}${curKind!=='all'?' · '+KIND_LABEL[curKind]:''} — item ${it.id}`;
  resetTake();
  [...$('#list').children].forEach((el,k)=>el.classList.toggle('cur', k===cur));
  const curEl = $('#list').children[cur]; if (curEl) curEl.scrollIntoView({block:'nearest'});
  if (it.recorded) { $('#playBtn').disabled = false; $('#playBtn').dataset.existing = `/audio/${it.kind}/${it.id}`; $('#playBtn').textContent = `▶ Play (${it.recordedBy||'recorded'})`; }
}
function resetTake() { recordedBlob = null; chunks = []; $('#saveBtn').disabled = true; $('#recBtn').textContent = '● Record'; $('#recBtn').classList.remove('on'); $('#timer').textContent = '0.0s'; }

let stream, t0, timerH;
async function toggleRecord() {
  if (mediaRecorder && mediaRecorder.state === 'recording') { mediaRecorder.stop(); return; }
  try { stream = stream || await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true } }); }
  catch (e) { toast('Microphone permission needed'); return; }
  const mime = ['audio/webm;codecs=opus','audio/webm','audio/mp4'].find(m => MediaRecorder.isTypeSupported(m)) || '';
  recordedMime = mime; chunks = [];
  mediaRecorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
  mediaRecorder.ondataavailable = e => e.data.size && chunks.push(e.data);
  mediaRecorder.onstop = () => { clearInterval(timerH); recordedBlob = new Blob(chunks, { type: recordedMime || 'audio/webm' }); $('#saveBtn').disabled = false; $('#playBtn').disabled = false; delete $('#playBtn').dataset.existing; $('#recBtn').textContent = '● Record'; $('#recBtn').classList.remove('on'); };
  mediaRecorder.start(); t0 = Date.now(); $('#recBtn').textContent = '■ Stop'; $('#recBtn').classList.add('on'); $('#saveBtn').disabled = true;
  timerH = setInterval(() => $('#timer').textContent = ((Date.now()-t0)/1000).toFixed(1) + 's', 100);
}
function play() {
  const p = $('#player'); const existing = $('#playBtn').dataset.existing;
  p.src = existing ? existing : URL.createObjectURL(recordedBlob); p.play();
}
async function save() {
  if (!recordedBlob) return;
  const it = current(); const ext = (recordedMime.includes('mp4')?'m4a':'webm');
  $('#saveBtn').disabled = true; $('#saveBtn').textContent = 'Saving…';
  try {
    const res = await fetch(`/api/save?kind=${it.kind}&id=${encodeURIComponent(it.id)}&by=${encodeURIComponent(byName())}&ext=${ext}`, { method:'POST', body: recordedBlob });
    const j = await res.json();
    if (!j.ok) { toast('Not saved: ' + j.error); $('#saveBtn').disabled = false; $('#saveBtn').textContent = 'Save & next'; return; }
    toast(`Saved (${j.duration.toFixed(2)}s)`);
    it.recorded = true; it.recordedBy = byName();
    const master = ITEMS.find(x => x.kind===it.kind && x.id===it.id); if (master) { master.recorded = true; master.recordedBy = byName(); }
    renderKinds(); renderList();
    advance();
  } catch (e) { toast('Save failed: ' + e.message); }
  $('#saveBtn').textContent = 'Save & next';
}
function advance() {
  const f = filtered(); let j = cur + 1;
  if ($('#skipDone').checked) while (j < f.length && f[j].recorded) j++;
  if (j >= f.length) { toast('That is everything in this list'); j = f.length - 1; }
  goto(j);
}
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.code === 'Space') { e.preventDefault(); toggleRecord(); }
  else if (e.code === 'Enter') { e.preventDefault(); save(); }
  else if (e.code === 'Backspace') { e.preventDefault(); resetTake(); }
  else if (e.code === 'ArrowRight') goto(cur+1);
  else if (e.code === 'ArrowLeft') goto(cur-1);
});
$('#recBtn').onclick = toggleRecord; $('#playBtn').onclick = play; $('#saveBtn').onclick = save;
$('#prev').onclick = () => goto(cur-1); $('#nextBtn').onclick = () => goto(cur+1);
$('#search').oninput = () => { cur = 0; renderList(); goto(0); };
load();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet; errors still raise

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, HTML.encode("utf8"), "text/html; charset=utf-8")
        elif path == "/api/items":
            self._send(200, state_payload())
        elif path.startswith("/audio/"):
            parts = path.split("/")
            if len(parts) == 4:
                _, _, kind, id_with_ext = parts
                fp = f"{ASSETS}/{kind}/{id_with_ext}"
                if not id_with_ext.endswith(".mp3"):
                    fp = f"{ASSETS}/{kind}/{id_with_ext}.mp3"
                if os.path.isfile(fp):
                    self._send(200, open(fp, "rb").read(), "audio/mpeg")
                    return
            self._send(404, {"error": "not found"})
        elif path.startswith("/fonts/"):
            name = path.split("/")[-1]
            fp = FONTS.get(name)
            if fp and os.path.isfile(fp):
                self._send(200, open(fp, "rb").read(), "font/ttf")
            else:
                self._send(404, {"error": "not found"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/save":
            self._send(404, {"error": "not found"})
            return
        qs = parse_qs(parsed.query)
        kind, id_ = qs.get("kind", [""])[0], qs.get("id", [""])[0]
        by = qs.get("by", [""])[0] or "unknown"
        ext = qs.get("ext", ["webm"])[0]
        if not any(it["kind"] == kind and it["id"] == id_ for it in ITEMS):
            self._send(400, {"ok": False, "error": f"unknown clip {kind}/{id_}"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        tmpdir = tempfile.mkdtemp()
        try:
            src = f"{tmpdir}/in.{ext}"
            open(src, "wb").write(raw)
            wav = f"{tmpdir}/out.wav"
            ffmpeg_decode_to_wav(src, wav)
            a, sr = sf.read(wav, dtype="float32")
            if len(a) / sr < MIN_CLIP_S:
                self._send(200, {"ok": False, "error": "recording too short — check the microphone"})
                return
            a = process_array(a, sr)
            write_clip(a, kind, id_, ASSETS, dry_run=False)
            ovr = load_overrides(OVERRIDES)
            ovr[f"{kind}/{id_}"] = {"method": "human", "recordedBy": by, "date": str(date.today())}
            save_overrides(ovr, OVERRIDES, dry_run=False)
            self._send(200, {"ok": True, "duration": len(a) / SR})
        except Exception as e:  # noqa: BLE001 — surface any ffmpeg/decode error to the browser instead of a stack trace
            self._send(200, {"ok": False, "error": str(e)})
        finally:
            for f in os.listdir(tmpdir):
                os.remove(f"{tmpdir}/{f}")
            os.rmdir(tmpdir)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    print(f"Voice Studio: {len(ITEMS)} clips. Open http://localhost:{port}/  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
