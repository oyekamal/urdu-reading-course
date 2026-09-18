# Urdu Reading Course — Human Voice Recording Script

## How to record (read this page first)

**Setup**
- A quiet room. No fan/AC hum, no TV, no traffic noise in the background. Close the window.
- Phone (or recorder) about 20 cm from your mouth — roughly a hand-span. Too close and every
  "p"/"b" pops; too far and the room noise creeps in.
- Use the phone's built-in Voice Recorder / Voice Memos app at the highest quality setting
  (usually labelled "Lossless" or "WAV" or "High quality"; if only an MP3 option exists that is
  fine too — the import script converts everything). One long take per session is easiest; you
  do not need to stop and start a new file for every line.

**Reading pattern — this is what makes auto-splitting work**
For every numbered line in this script:
1. Say the line number **in English words** ("one", "two", "three", … "four hundred
   seventy-four") — this is the marker the import script's silence-splitter and your own CSV
   cut-list will line up against.
2. Pause half a second.
3. Say the Urdu text **twice**, with a clear 2-second pause of silence between the two
   repetitions. Recording it twice gives whoever edits the files a second take to fall back on if
   the first one is off.
4. Pause 2 seconds before saying the next number.

Example, out loud: *"one 〈pause〉 اَلِف 〈2s silence〉 اَلِف 〈2s silence〉 two 〈pause〉 بے 〈2s
silence〉 بے …"*

**How to say each kind of item**
- **Letter names (section 1)** — say them exactly as taught in Pakistani schools: الف *alif*, ب
  *be*, پ *pe*, ت *te*, ٹ *ṭe*, ث *s̱e*, ج *jīm*, چ *che*, ح *baṛī ḥe*, خ *k͟he*, د *dāl*, ڈ *ḍāl*,
  ذ *ẕāl*, ر *re*, ڑ *ṛe*, ز *ze*, ژ *zhe*, س *sīn*, ش *shīn*, ص *ṣwād*, ض *ẓwād*, ط *t̤oʼe*, ظ
  *z̤oʼe*, ع *ʻain*, غ *g͟hain*, ف *fe*, ق *qāf*, ک *kāf*, گ *gāf*, ل *lām*, م *mīm*, ن *nūn*, ں
  *nūn g͟hunna*, و *wāʾo*, ہ *choṭī he / gol he*, ھ **دو چشمی ہے** (*do-chashmī he* — say the
  full three-word Urdu name, not just "he"), ء *hamza*, ی **چھوٹی یے** (*choṭī ye*, the full
  two-word name), ے **بڑی یے** (*baṛī ye*, the full two-word name). The romanisation column next
  to each line spells these out too.
- **Short vowels (diacritics, section 5, and any word marked "read the vowel marks" in the note
  column)** — the printed Urdu already carries the zabar/zer/pesh/jazm/tashdīd marks. Read the
  word **exactly as those marks show it**, not however you'd casually pronounce the unmarked
  spelling. This is the one place recording quality genuinely fixes a known machine-voice gap
  (the TTS model has no short-vowel marks in its training vocabulary and had to guess).
- **Numerals (section 9)** — say the number as a spoken word (صفر, ایک, دو, تین …), the way you'd
  say "two" out loud, not the digit's name or a spelled-out count.
- **Everything else** (example words, syllables, aspirate words, unit words and sentences, sight
  words) — read naturally, the way you'd say it to a child learning to read, at a calm, clear,
  unhurried pace. Don't over-enunciate into a robotic cadence — a slightly warm, unhurried
  "teacher voice" is exactly right.

**If you misread a line:** just stop, say "again" once, then redo that number from the start —
the person doing the import can find the redo by ear or trim it out; it does not need to be
perfect on the first pass.

**When you're done:** send the whole recording (one file or several session files) back, plus
tell us roughly how long each file is / which line numbers are in which file if you used more
than one session. That's all `scripts/import_recordings.py` needs.

---

## 1 · Letter names

1. `names/alif` | **الف** (alif) — unit 1 — 'a' in father when long; a silent seat for short vowels at the start of a word
2. `names/be` | **بے** (be) — unit 1 — 'b' in bat
3. `names/kaf` | **کاف** (kāf) — unit 1 — 'k' in kite
4. `names/lam` | **لام** (lām) — unit 1 — 'l' in log
5. `names/mim` | **میم** (mīm) — unit 1 — 'm' in mat
6. `names/nun` | **نون** (nūn) — unit 1 — 'n' in net
7. `names/te` | **تے** (te) — unit 2 — soft dental 't', tongue on the teeth (Spanish 'tú')
8. `names/choti_ye` | **چھوٹی یے** (choṭī ye) — unit 2 — 'y' in yes at the start; long 'ee' in the middle or end
9. `names/bari_ye` | **بڑی یے** (baṛī ye) — unit 2 — 'ay' in day; only ever a vowel, only at the end of a word or syllable
10. `names/pe` | **پے** (pe) — unit 3 — 'p' in pat
11. `names/tte` | **ٹے** (ṭe) — unit 3 — hard English 't' in tap, tongue curled back
12. `names/se` | **ثے** (s̱e) — unit 3 — 's' in sun (Arabic loanwords only)
13. `names/wao` | **واؤ** (wāʾo) — unit 4 — 'w'/'v' at the start; long 'oo' or 'o' otherwise
14. `names/re` | **رے** (re) — unit 4 — tapped 'r' (Spanish 'pero')
15. `names/dal` | **دال** (dāl) — unit 4 — soft dental 'd', tongue on the teeth
16. `names/he` | **ہے / گول ہے** (choṭī he (gol he)) — unit 4 — 'h' in hat; at the end of a word it usually just says 'a' (کمرہ kamra)
17. `names/sin` | **سین** (sīn) — unit 5 — 's' in sun
18. `names/shin` | **شین** (shīn) — unit 5 — 'sh' in shop
19. `names/jim` | **جیم** (jīm) — unit 5 — 'j' in jam
20. `names/che` | **چے** (che) — unit 5 — 'ch' in chair
21. `names/gaf` | **گاف** (gāf) — unit 5 — 'g' in go
22. `names/nun_ghunna` | **نون غنہ** (nūn g͟hunna) — unit 6 — nasalises the vowel before it, like French 'bon'; never at the start of a word
23. `names/do_chashmi_he` | **دو چشمی ہے** (do-chashmī he) — unit 6 — a puff of breath after the letter before it: بھ bh, پھ ph, کھ kh, گھ gh…; never alone at the start
24. `names/ddal` | **ڈال** (ḍāl) — unit 7 — hard English 'd' in dad, tongue curled back
25. `names/rre` | **ڑے** (ṛe) — unit 7 — a flapped 'r'/'d' made with the tongue curled back (no English match); never at the start
26. `names/ze` | **زے** (ze) — unit 7 — 'z' in zoo
27. `names/zhe` | **ژے** (zhe) — unit 7 — 's' in pleasure (Persian loanwords only, rare)
28. `names/fe` | **فے** (fe) — unit 8 — 'f' in fat
29. `names/qaf` | **قاف** (qāf) — unit 8 — a 'k' made far back in the throat (Arabic loanwords)
30. `names/khe` | **خے** (k͟he) — unit 8 — 'ch' in Scottish loch
31. `names/ghain` | **غین** (g͟hain) — unit 8 — a gargled 'g', like the French 'r'
32. `names/ain` | **عین** (ʻain) — unit 8 — in Urdu it mostly just carries the vowel written around it (عمر umar)
33. `names/bari_he` | **بڑی حے** (baṛī ḥe) — unit 8 — 'h' in hat (Arabic loanwords)
34. `names/swad` | **صاد** (ṣwād) — unit 9 — 's' in sun (Arabic loanwords; same sound as س)
35. `names/zwad` | **ضاد** (ẓwād) — unit 9 — 'z' in zoo (Arabic loanwords; same sound as ز)
36. `names/toe` | **طوے** (t̤oʼe) — unit 9 — soft 't' (Arabic loanwords; same sound as ت)
37. `names/zoe` | **ظوے** (z̤oʼe) — unit 9 — 'z' in zoo (Arabic loanwords; same sound as ز)
38. `names/zal` | **ذال** (ẕāl) — unit 9 — 'z' in zoo (Arabic loanwords; same sound as ز)
39. `names/hamza` | **ہمزہ** (hamza) — unit 10 — a tiny break between two vowels (کوئی ko-ī). It rides on ی as ئ, on و as ؤ, or stands alone as ء; آ is alif with a madd, long ā at the start of a word (آم ām)

## 2 · Example words (one per letter)

40. `words/alif` | **اب** (ab) — now — example word for alif
41. `words/be` | **بابا** (bābā) — father — example word for be
42. `words/kaf` | **کام** (kām) — work — example word for kāf
43. `words/lam` | **لال** (lāl) — red — example word for lām
44. `words/mim` | **مکان** (makān) — house — example word for mīm
45. `words/nun` | **نام** (nām) — name — example word for nūn
46. `words/te` | **تین** (tīn) — three — example word for te
47. `words/choti_ye` | **یار** (yār) — friend — example word for choṭī ye
48. `words/bari_ye` | **لے** (le) — take — example word for baṛī ye
49. `words/pe` | **پانی** (pānī) — water — example word for pe
50. `words/tte` | **ٹوپی** (ṭopī) — cap — example word for ṭe
51. `words/se` | **ثمر** (s̱amar) — fruit — example word for s̱e
52. `words/wao` | **وہ** (woh) — he / she / that — example word for wāʾo
53. `words/re` | **رات** (rāt) — night — example word for re
54. `words/dal` | **دو** (do) — two — example word for dāl
55. `words/he` | **ہم** (ham) — we — example word for choṭī he (gol he)
56. `words/sin` | **سال** (sāl) — year — example word for sīn
57. `words/shin` | **شام** (shām) — evening — example word for shīn
58. `words/jim` | **جوتا** (jūtā) — shoe — example word for jīm
59. `words/che` | **چار** (chār) — four — example word for che
60. `words/gaf` | **گلاب** (gulāb) — rose — example word for gāf
61. `words/nun_ghunna` | **میں** (maiṉ) — I / in — example word for nūn g͟hunna
62. `words/do_chashmi_he` | **گھر** (ghar) — house — example word for do-chashmī he
63. `words/ddal` | **ڈاک** (ḍāk) — mail — example word for ḍāl
64. `words/rre` | **لڑکا** (laṛkā) — boy — example word for ṛe
65. `words/ze` | **زبان** (zabān) — tongue / language — example word for ze
66. `words/zhe` | **ژالہ** (zhāla) — hailstone — example word for zhe
67. `words/fe` | **فرش** (farsh) — floor — example word for fe
68. `words/qaf` | **قلم** (qalam) — pen — example word for qāf
69. `words/khe` | **خط** (k͟hat) — letter — example word for k͟he
70. `words/ghain` | **غریب** (g͟harīb) — poor — example word for g͟hain
71. `words/ain` | **عمر** (ʻumr) — age — example word for ʻain
72. `words/bari_he` | **حال** (ḥāl) — condition — example word for baṛī ḥe
73. `words/swad` | **صبح** (ṣubḥ) — morning — example word for ṣwād
74. `words/zwad` | **ضرور** (ẓarūr) — certainly — example word for ẓwād
75. `words/toe` | **طوطا** (t̤ot̤ā) — parrot — example word for t̤oʼe
76. `words/zoe` | **ظاہر** (z̤āhir) — apparent — example word for z̤oʼe
77. `words/zal` | **ذائقہ** (ẕāʾiqa) — taste — example word for ẕāl
78. `words/hamza` | **کوئی** (koʾī) — someone / any — example word for hamza

## 3 · Syllables (consonant + long vowel)

79. `syllables/be_a` | **با** — be + long ā
80. `syllables/be_i` | **بی** — be + long ī
81. `syllables/be_u` | **بو** — be + long ū
82. `syllables/kaf_a` | **کا** — kāf + long ā
83. `syllables/kaf_i` | **کی** — kāf + long ī
84. `syllables/kaf_u` | **کو** — kāf + long ū
85. `syllables/lam_a` | **لا** — lām + long ā
86. `syllables/lam_i` | **لی** — lām + long ī
87. `syllables/lam_u` | **لو** — lām + long ū
88. `syllables/mim_a` | **ما** — mīm + long ā
89. `syllables/mim_i` | **می** — mīm + long ī
90. `syllables/mim_u` | **مو** — mīm + long ū
91. `syllables/nun_a` | **نا** — nūn + long ā
92. `syllables/nun_i` | **نی** — nūn + long ī
93. `syllables/nun_u` | **نو** — nūn + long ū
94. `syllables/te_a` | **تا** — te + long ā
95. `syllables/te_i` | **تی** — te + long ī
96. `syllables/te_u` | **تو** — te + long ū
97. `syllables/pe_a` | **پا** — pe + long ā
98. `syllables/pe_i` | **پی** — pe + long ī
99. `syllables/pe_u` | **پو** — pe + long ū
100. `syllables/tte_a` | **ٹا** — ṭe + long ā
101. `syllables/tte_i` | **ٹی** — ṭe + long ī
102. `syllables/tte_u` | **ٹو** — ṭe + long ū
103. `syllables/se_a` | **ثا** — s̱e + long ā
104. `syllables/se_i` | **ثی** — s̱e + long ī
105. `syllables/se_u` | **ثو** — s̱e + long ū
106. `syllables/re_a` | **را** — re + long ā
107. `syllables/re_i` | **ری** — re + long ī
108. `syllables/re_u` | **رو** — re + long ū
109. `syllables/dal_a` | **دا** — dāl + long ā
110. `syllables/dal_i` | **دی** — dāl + long ī
111. `syllables/dal_u` | **دو** — dāl + long ū
112. `syllables/he_a` | **ہا** — choṭī he (gol he) + long ā
113. `syllables/he_i` | **ہی** — choṭī he (gol he) + long ī
114. `syllables/he_u` | **ہو** — choṭī he (gol he) + long ū
115. `syllables/sin_a` | **سا** — sīn + long ā
116. `syllables/sin_i` | **سی** — sīn + long ī
117. `syllables/sin_u` | **سو** — sīn + long ū
118. `syllables/shin_a` | **شا** — shīn + long ā
119. `syllables/shin_i` | **شی** — shīn + long ī
120. `syllables/shin_u` | **شو** — shīn + long ū
121. `syllables/jim_a` | **جا** — jīm + long ā
122. `syllables/jim_i` | **جی** — jīm + long ī
123. `syllables/jim_u` | **جو** — jīm + long ū
124. `syllables/che_a` | **چا** — che + long ā
125. `syllables/che_i` | **چی** — che + long ī
126. `syllables/che_u` | **چو** — che + long ū
127. `syllables/gaf_a` | **گا** — gāf + long ā
128. `syllables/gaf_i` | **گی** — gāf + long ī
129. `syllables/gaf_u` | **گو** — gāf + long ū
130. `syllables/ddal_a` | **ڈا** — ḍāl + long ā
131. `syllables/ddal_i` | **ڈی** — ḍāl + long ī
132. `syllables/ddal_u` | **ڈو** — ḍāl + long ū
133. `syllables/ze_a` | **زا** — ze + long ā
134. `syllables/ze_i` | **زی** — ze + long ī
135. `syllables/ze_u` | **زو** — ze + long ū
136. `syllables/zhe_a` | **ژا** — zhe + long ā
137. `syllables/zhe_i` | **ژی** — zhe + long ī
138. `syllables/zhe_u` | **ژو** — zhe + long ū
139. `syllables/fe_a` | **فا** — fe + long ā
140. `syllables/fe_i` | **فی** — fe + long ī
141. `syllables/fe_u` | **فو** — fe + long ū
142. `syllables/qaf_a` | **قا** — qāf + long ā
143. `syllables/qaf_i` | **قی** — qāf + long ī
144. `syllables/qaf_u` | **قو** — qāf + long ū
145. `syllables/khe_a` | **خا** — k͟he + long ā
146. `syllables/khe_i` | **خی** — k͟he + long ī
147. `syllables/khe_u` | **خو** — k͟he + long ū
148. `syllables/ghain_a` | **غا** — g͟hain + long ā
149. `syllables/ghain_i` | **غی** — g͟hain + long ī
150. `syllables/ghain_u` | **غو** — g͟hain + long ū
151. `syllables/bari_he_a` | **حا** — baṛī ḥe + long ā
152. `syllables/bari_he_i` | **حی** — baṛī ḥe + long ī
153. `syllables/bari_he_u` | **حو** — baṛī ḥe + long ū
154. `syllables/swad_a` | **صا** — ṣwād + long ā
155. `syllables/swad_i` | **صی** — ṣwād + long ī
156. `syllables/swad_u` | **صو** — ṣwād + long ū
157. `syllables/zwad_a` | **ضا** — ẓwād + long ā
158. `syllables/zwad_i` | **ضی** — ẓwād + long ī
159. `syllables/zwad_u` | **ضو** — ẓwād + long ū
160. `syllables/toe_a` | **طا** — t̤oʼe + long ā
161. `syllables/toe_i` | **طی** — t̤oʼe + long ī
162. `syllables/toe_u` | **طو** — t̤oʼe + long ū
163. `syllables/zoe_a` | **ظا** — z̤oʼe + long ā
164. `syllables/zoe_i` | **ظی** — z̤oʼe + long ī
165. `syllables/zoe_u` | **ظو** — z̤oʼe + long ū
166. `syllables/zal_a` | **ذا** — ẕāl + long ā
167. `syllables/zal_i` | **ذی** — ẕāl + long ī
168. `syllables/zal_u` | **ذو** — ẕāl + long ū

## 4 · Aspirates (the do-chashmī he sound, in its example word)

169. `aspirates/bh` | **بھائی** (bhāʾī) — brother — carries the aspirate بھ (bh)
170. `aspirates/ph` | **پھول** (phūl) — flower — carries the aspirate پھ (ph)
171. `aspirates/th` | **تھالی** (thālī) — plate — carries the aspirate تھ (th)
172. `aspirates/ṭh` | **ٹھنڈا** (ṭhanḍā) — cold — carries the aspirate ٹھ (ṭh)
173. `aspirates/jh` | **جھنڈا** (jhanḍā) — flag — carries the aspirate جھ (jh)
174. `aspirates/chh` | **چھت** (chhat) — roof — carries the aspirate چھ (chh)
175. `aspirates/dh` | **دھاگا** (dhāgā) — thread — carries the aspirate دھ (dh)
176. `aspirates/ḍh` | **ڈھول** (ḍhol) — drum — carries the aspirate ڈھ (ḍh)
177. `aspirates/ṛh` | **پڑھنا** (paṛhnā) — to read — carries the aspirate ڑھ (ṛh)
178. `aspirates/kh` | **کھانا** (khānā) — food — carries the aspirate کھ (kh)
179. `aspirates/gh` | **گھر** (ghar) — house — carries the aspirate گھ (gh)

## 5 · Diacritics and their example words

180. `diacritics/zabar` | **زبر** (zabar) — short a (as in 'but')
181. `diacritics/zabar_ex` | **بَس** (bas) — enough — example for zabar
182. `diacritics/zer` | **زیر** (zer) — short i (as in 'bit')
183. `diacritics/zer_ex` | **دِل** (dil) — heart — example for zer
184. `diacritics/pesh` | **پیش** (pesh) — short u (as in 'put')
185. `diacritics/pesh_ex` | **گُل** (gul) — flower — example for pesh
186. `diacritics/jazm` | **جزم** (jazm (sukūn)) — no vowel after this letter
187. `diacritics/jazm_ex` | **سَبْزی** (sabzī) — vegetable — example for jazm (sukūn)
188. `diacritics/tashdid` | **تشدید** (tashdīd) — double the letter
189. `diacritics/tashdid_ex` | **بچّہ** (bachcha) — child — example for tashdīd
190. `diacritics/khari_zabar` | **کھڑا زبر** (khaṛā zabar) — long ā without alif
191. `diacritics/khari_zabar_ex` | **اعلیٰ** (aʻlā) — high — example for khaṛā zabar

## 6 · Unit words

192. `units/u01_00` | **اب** (ab) — unit 1 (The first six) — now; read the vowel marks: اَب
193. `units/u01_01` | **بابا** (bābā) — unit 1 (The first six) — dad
194. `units/u01_02` | **امام** (imām) — unit 1 (The first six) — prayer leader; read the vowel marks: اِمام
195. `units/u01_03` | **نام** (nām) — unit 1 (The first six) — name
196. `units/u01_04` | **کام** (kām) — unit 1 (The first six) — work
197. `units/u01_05` | **کل** (kal) — unit 1 (The first six) — tomorrow / yesterday; read the vowel marks: کَل
198. `units/u01_06` | **لال** (lāl) — unit 1 (The first six) — red
199. `units/u01_07` | **بال** (bāl) — unit 1 (The first six) — hair
200. `units/u01_08` | **ناک** (nāk) — unit 1 (The first six) — nose
201. `units/u01_09` | **کان** (kān) — unit 1 (The first six) — ear
202. `units/u01_10` | **مان** (mān) — unit 1 (The first six) — accept
203. `units/u01_11` | **نمک** (namak) — unit 1 (The first six) — salt; read the vowel marks: نَمَک
204. `units/u01_12` | **ملک** (mulk) — unit 1 (The first six) — country; read the vowel marks: مُلْک
205. `units/u01_13` | **کمال** (kamāl) — unit 1 (The first six) — wonder; read the vowel marks: کَمال
206. `units/u01_14` | **نانا** (nānā) — unit 1 (The first six) — maternal grandfather
207. `units/u01_15` | **کالا** (kālā) — unit 1 (The first six) — black
208. `units/u01_16` | **مالا** (mālā) — unit 1 (The first six) — garland
209. `units/u01_17` | **مکان** (makān) — unit 1 (The first six) — house; read the vowel marks: مَکان
210. `units/u01_18` | **املا** (imlā) — unit 1 (The first six) — dictation; read the vowel marks: اِملا
211. `units/u01_19` | **کمان** (kamān) — unit 1 (The first six) — bow; read the vowel marks: کَمان
212. `units/u02_00` | **تم** (tum) — unit 2 (Dots and the two ye) — you; read the vowel marks: تُم
213. `units/u02_01` | **تین** (tīn) — unit 2 (Dots and the two ye) — three
214. `units/u02_02` | **بیل** (bail) — unit 2 (Dots and the two ye) — ox; read the vowel marks: بَیل
215. `units/u02_03` | **میل** (mīl) — unit 2 (Dots and the two ye) — mile
216. `units/u02_04` | **نیلا** (nīlā) — unit 2 (Dots and the two ye) — blue
217. `units/u02_05` | **کیلا** (kelā) — unit 2 (Dots and the two ye) — banana
218. `units/u02_06` | **تیل** (tel) — unit 2 (Dots and the two ye) — oil
219. `units/u02_07` | **لے** (le) — unit 2 (Dots and the two ye) — take
220. `units/u02_08` | **کے** (ke) — unit 2 (Dots and the two ye) — of
221. `units/u02_09` | **نے** (ne) — unit 2 (Dots and the two ye) — (agent marker)
222. `units/u02_10` | **تالی** (tālī) — unit 2 (Dots and the two ye) — clap
223. `units/u02_11` | **بلی** (billī) — unit 2 (Dots and the two ye) — cat; read the vowel marks: بِلّی
224. `units/u02_12` | **تالا** (tālā) — unit 2 (Dots and the two ye) — lock
225. `units/u02_13` | **کتاب** (kitāb) — unit 2 (Dots and the two ye) — book; read the vowel marks: کِتاب
226. `units/u02_14` | **بیتاب** (betāb) — unit 2 (Dots and the two ye) — restless
227. `units/u02_15` | **تکیا** (takiya) — unit 2 (Dots and the two ye) — pillow; read the vowel marks: تَکِیا
228. `units/u02_16` | **مالی** (mālī) — unit 2 (Dots and the two ye) — gardener
229. `units/u02_17` | **ناتا** (nātā) — unit 2 (Dots and the two ye) — relation
230. `units/u02_18` | **تالاب** (tālāb) — unit 2 (Dots and the two ye) — pond
231. `units/u02_19` | **کمانی** (kamānī) — unit 2 (Dots and the two ye) — spring; read the vowel marks: کَمانی
232. `units/u03_00` | **پانی** (pānī) — unit 3 (Finishing the be family) — water
233. `units/u03_01` | **پل** (pul) — unit 3 (Finishing the be family) — bridge; read the vowel marks: پُل
234. `units/u03_02` | **ٹوپی** (ṭopī) — unit 3 (Finishing the be family) — cap (و comes in unit 4, preview)
235. `units/u03_03` | **پتا** (patā) — unit 3 (Finishing the be family) — address; read the vowel marks: پَتا
236. `units/u03_04` | **پاک** (pāk) — unit 3 (Finishing the be family) — pure
237. `units/u03_05` | **پیٹ** (peṭ) — unit 3 (Finishing the be family) — stomach
238. `units/u03_06` | **ٹب** (ṭab) — unit 3 (Finishing the be family) — tub; read the vowel marks: ٹَب
239. `units/u03_07` | **پتلی** (patlī) — unit 3 (Finishing the be family) — thin; read the vowel marks: پَتْلی
240. `units/u03_08` | **ثابت** (s̱ābit) — unit 3 (Finishing the be family) — proven; read the vowel marks: ثابِت
241. `units/u03_09` | **پیپل** (pīpal) — unit 3 (Finishing the be family) — fig tree; read the vowel marks: پیپَل
242. `units/u03_10` | **ٹماٹر** (ṭamāṭar) — unit 3 (Finishing the be family) — tomato (ر preview); read the vowel marks: ٹَماٹَر
243. `units/u03_11` | **ٹانکا** (ṭānkā) — unit 3 (Finishing the be family) — stitch; read the vowel marks: ٹانْکا
244. `units/u03_12` | **پیالا** (piyālā) — unit 3 (Finishing the be family) — bowl; read the vowel marks: پِیالا
245. `units/u03_13` | **نپا** (napā) — unit 3 (Finishing the be family) — measured; read the vowel marks: نَپا
246. `units/u03_14` | **پلک** (palak) — unit 3 (Finishing the be family) — eyelash; read the vowel marks: پَلَک
247. `units/u03_15` | **کپاس** (kapās) — unit 3 (Finishing the be family) — cotton (س preview); read the vowel marks: کَپاس
248. `units/u03_16` | **تپتا** (taptā) — unit 3 (Finishing the be family) — scorching; read the vowel marks: تَپْتا
249. `units/u03_17` | **پتلا** (patlā) — unit 3 (Finishing the be family) — thin; read the vowel marks: پَتْلا
250. `units/u03_18` | **ٹکٹ** (ṭikaṭ) — unit 3 (Finishing the be family) — ticket; read the vowel marks: ٹِکَٹ
251. `units/u03_19` | **بٹن** (baṭan) — unit 3 (Finishing the be family) — button; read the vowel marks: بَٹَن
252. `units/u04_00` | **وہ** (woh) — unit 4 (The non-joiners) — he / she / that; read the vowel marks: وُہ
253. `units/u04_01` | **دو** (do) — unit 4 (The non-joiners) — two
254. `units/u04_02` | **دن** (din) — unit 4 (The non-joiners) — day; read the vowel marks: دِن
255. `units/u04_03` | **دال** (dāl) — unit 4 (The non-joiners) — lentils
256. `units/u04_04` | **دم** (dam) — unit 4 (The non-joiners) — breath; read the vowel marks: دَم
257. `units/u04_05` | **رات** (rāt) — unit 4 (The non-joiners) — night
258. `units/u04_06` | **روٹی** (roṭī) — unit 4 (The non-joiners) — bread
259. `units/u04_07` | **دور** (dūr) — unit 4 (The non-joiners) — far
260. `units/u04_08` | **ہم** (ham) — unit 4 (The non-joiners) — we; read the vowel marks: ہَم
261. `units/u04_09` | **ہار** (hār) — unit 4 (The non-joiners) — necklace
262. `units/u04_10` | **کمرہ** (kamra) — unit 4 (The non-joiners) — room; read the vowel marks: کَمْرہ
263. `units/u04_11` | **بادام** (bādām) — unit 4 (The non-joiners) — almond
264. `units/u04_12` | **دادا** (dādā) — unit 4 (The non-joiners) — grandfather
265. `units/u04_13` | **دریا** (daryā) — unit 4 (The non-joiners) — river; read the vowel marks: دَرْیا
266. `units/u04_14` | **ہوا** (hawā) — unit 4 (The non-joiners) — wind; read the vowel marks: ہَوا
267. `units/u04_15` | **راہ** (rāh) — unit 4 (The non-joiners) — path
268. `units/u04_16` | **دودھ** (dūdh) — unit 4 (The non-joiners) — milk (ھ preview)
269. `units/u04_17` | **مور** (mor) — unit 4 (The non-joiners) — peacock
270. `units/u04_18` | **پودا** (paudā) — unit 4 (The non-joiners) — plant; read the vowel marks: پَودا
271. `units/u04_19` | **نہر** (nahar) — unit 4 (The non-joiners) — canal; read the vowel marks: نَہَر
272. `units/u05_00` | **سب** (sab) — unit 5 (Sīn, jīm and gāf) — all; read the vowel marks: سَب
273. `units/u05_01` | **سو** (so) — unit 5 (Sīn, jīm and gāf) — hundred / sleep
274. `units/u05_02` | **سال** (sāl) — unit 5 (Sīn, jīm and gāf) — year
275. `units/u05_03` | **شام** (shām) — unit 5 (Sīn, jīm and gāf) — evening
276. `units/u05_04` | **شیر** (sher) — unit 5 (Sīn, jīm and gāf) — lion
277. `units/u05_05` | **جوتا** (jūtā) — unit 5 (Sīn, jīm and gāf) — shoe
278. `units/u05_06` | **جام** (jām) — unit 5 (Sīn, jīm and gāf) — goblet
279. `units/u05_07` | **چار** (chār) — unit 5 (Sīn, jīm and gāf) — four
280. `units/u05_08` | **چاند** (chānd) — unit 5 (Sīn, jīm and gāf) — moon
281. `units/u05_09` | **چابی** (chābī) — unit 5 (Sīn, jīm and gāf) — key
282. `units/u05_10` | **گلاب** (gulāb) — unit 5 (Sīn, jīm and gāf) — rose; read the vowel marks: گُلاب
283. `units/u05_11` | **گاجر** (gājar) — unit 5 (Sīn, jīm and gāf) — carrot; read the vowel marks: گاجَر
284. `units/u05_12` | **گانا** (gānā) — unit 5 (Sīn, jīm and gāf) — song
285. `units/u05_13` | **سبک** (sabuk) — unit 5 (Sīn, jīm and gāf) — light; read the vowel marks: سَبُک
286. `units/u05_14` | **شادی** (shādī) — unit 5 (Sīn, jīm and gāf) — wedding
287. `units/u05_15` | **جنگل** (jangal) — unit 5 (Sīn, jīm and gāf) — forest; read the vowel marks: جَنگَل
288. `units/u05_16` | **مچھلی** (machhlī) — unit 5 (Sīn, jīm and gāf) — fish (ھ preview); read the vowel marks: مَچھلی
289. `units/u05_17` | **گرم** (garm) — unit 5 (Sīn, jīm and gāf) — hot; read the vowel marks: گَرْم
290. `units/u05_18` | **سردی** (sardī) — unit 5 (Sīn, jīm and gāf) — cold; read the vowel marks: سَرْدی
291. `units/u05_19` | **دوست** (dost) — unit 5 (Sīn, jīm and gāf) — friend; read the vowel marks: دوسْت
292. `units/u06_00` | **میں** (maiṉ) — unit 6 (Breath and nose) — I / in; read the vowel marks: مَیں
293. `units/u06_01` | **ہاں** (hāṉ) — unit 6 (Breath and nose) — yes
294. `units/u06_02` | **کہاں** (kahāṉ) — unit 6 (Breath and nose) — where; read the vowel marks: کَہاں
295. `units/u06_03` | **ہیں** (haiṉ) — unit 6 (Breath and nose) — are; read the vowel marks: ہَیں
296. `units/u06_04` | **گھر** (ghar) — unit 6 (Breath and nose) — house; read the vowel marks: گَھر
297. `units/u06_05` | **بھائی** (bhāʾī) — unit 6 (Breath and nose) — brother (ئ preview); read the vowel marks: بَھائی
298. `units/u06_06` | **پھول** (phūl) — unit 6 (Breath and nose) — flower
299. `units/u06_07` | **تھالی** (thālī) — unit 6 (Breath and nose) — plate
300. `units/u06_08` | **ٹھنڈا** (ṭhanḍā) — unit 6 (Breath and nose) — cold (ڈ preview); read the vowel marks: ٹَھنڈا
301. `units/u06_09` | **کھانا** (khānā) — unit 6 (Breath and nose) — food
302. `units/u06_10` | **دھاگا** (dhāgā) — unit 6 (Breath and nose) — thread
303. `units/u06_11` | **چھت** (chhat) — unit 6 (Breath and nose) — roof; read the vowel marks: چَھت
304. `units/u06_12` | **جھولا** (jhūlā) — unit 6 (Breath and nose) — swing
305. `units/u06_13` | **ہاتھ** (hāth) — unit 6 (Breath and nose) — hand
306. `units/u06_14` | **دودھ** (dūdh) — unit 6 (Breath and nose) — milk
307. `units/u06_15` | **مچھلی** (machhlī) — unit 6 (Breath and nose) — fish; read the vowel marks: مَچھلی
308. `units/u06_16` | **آنکھ** (āṉkh) — unit 6 (Breath and nose) — eye
309. `units/u06_17` | **یہاں** (yahāṉ) — unit 6 (Breath and nose) — here; read the vowel marks: یَہاں
310. `units/u06_18` | **سکھانا** (sikhānā) — unit 6 (Breath and nose) — to teach; read the vowel marks: سِکھانا
311. `units/u06_19` | **بھالو** (bhālū) — unit 6 (Breath and nose) — bear; read the vowel marks: بَھالو
312. `units/u07_00` | **ڈاک** (ḍāk) — unit 7 (Retroflex and z) — mail
313. `units/u07_01` | **ڈبہ** (ḍabba) — unit 7 (Retroflex and z) — box; read the vowel marks: ڈَبّہ
314. `units/u07_02` | **لڑکا** (laṛkā) — unit 7 (Retroflex and z) — boy; read the vowel marks: لَڑْکا
315. `units/u07_03` | **لڑکی** (laṛkī) — unit 7 (Retroflex and z) — girl; read the vowel marks: لَڑْکی
316. `units/u07_04` | **بڑا** (baṛā) — unit 7 (Retroflex and z) — big; read the vowel marks: بَڑا
317. `units/u07_05` | **پڑھنا** (paṛhnā) — unit 7 (Retroflex and z) — to read; read the vowel marks: پَڑھنا
318. `units/u07_06` | **زبان** (zabān) — unit 7 (Retroflex and z) — tongue / language; read the vowel marks: زَبان
319. `units/u07_07` | **زمین** (zamīn) — unit 7 (Retroflex and z) — earth; read the vowel marks: زَمین
320. `units/u07_08` | **ژالہ** (zhāla) — unit 7 (Retroflex and z) — hailstone; read the vowel marks: ژَالہ
321. `units/u07_09` | **روزانہ** (rozāna) — unit 7 (Retroflex and z) — daily
322. `units/u07_10` | **ڈھول** (ḍhol) — unit 7 (Retroflex and z) — drum
323. `units/u07_11` | **گڑیا** (guṛiyā) — unit 7 (Retroflex and z) — doll; read the vowel marks: گُڑِیا
324. `units/u07_12` | **سڑک** (saṛak) — unit 7 (Retroflex and z) — road; read the vowel marks: سَڑَک
325. `units/u07_13` | **زرد** (zard) — unit 7 (Retroflex and z) — yellow; read the vowel marks: زَرْد
326. `units/u07_14` | **ڈر** (ḍar) — unit 7 (Retroflex and z) — fear; read the vowel marks: ڈَر
327. `units/u07_15` | **کپڑا** (kapṛā) — unit 7 (Retroflex and z) — cloth; read the vowel marks: کَپْڑا
328. `units/u07_16` | **مزا** (mazā) — unit 7 (Retroflex and z) — fun; read the vowel marks: مَزا
329. `units/u07_17` | **انڈا** (anḍā) — unit 7 (Retroflex and z) — egg; read the vowel marks: اَنڈا
330. `units/u07_18` | **ٹھنڈا** (ṭhanḍā) — unit 7 (Retroflex and z) — cold; read the vowel marks: ٹَھنڈا
331. `units/u07_19` | **گھڑی** (ghaṛī) — unit 7 (Retroflex and z) — watch; read the vowel marks: گَھڑی
332. `units/u08_00` | **فرش** (farsh) — unit 8 (Sounds from Arabic and Persian) — floor; read the vowel marks: فَرْش
333. `units/u08_01` | **فون** (fon) — unit 8 (Sounds from Arabic and Persian) — phone
334. `units/u08_02` | **قلم** (qalam) — unit 8 (Sounds from Arabic and Persian) — pen; read the vowel marks: قَلَم
335. `units/u08_03` | **قمیض** (qamīẕ) — unit 8 (Sounds from Arabic and Persian) — shirt (ض preview); read the vowel marks: قَمیض
336. `units/u08_04` | **خط** (k͟hat) — unit 8 (Sounds from Arabic and Persian) — letter (ط preview); read the vowel marks: خَط
337. `units/u08_05` | **خوش** (k͟hush) — unit 8 (Sounds from Arabic and Persian) — happy; read the vowel marks: خُوش
338. `units/u08_06` | **غریب** (g͟harīb) — unit 8 (Sounds from Arabic and Persian) — poor; read the vowel marks: غَریب
339. `units/u08_07` | **باغ** (bāg͟h) — unit 8 (Sounds from Arabic and Persian) — garden
340. `units/u08_08` | **عمر** (ʻumr) — unit 8 (Sounds from Arabic and Persian) — age; read the vowel marks: عُمْر
341. `units/u08_09` | **علم** (ʻilm) — unit 8 (Sounds from Arabic and Persian) — knowledge; read the vowel marks: عِلْم
342. `units/u08_10` | **حال** (ḥāl) — unit 8 (Sounds from Arabic and Persian) — condition
343. `units/u08_11` | **حلوہ** (ḥalwa) — unit 8 (Sounds from Arabic and Persian) — halwa; read the vowel marks: حَلْوہ
344. `units/u08_12` | **صاف** (ṣāf) — unit 8 (Sounds from Arabic and Persian) — clean (ص preview)
345. `units/u08_13` | **فوج** (fauj) — unit 8 (Sounds from Arabic and Persian) — army; read the vowel marks: فَوج
346. `units/u08_14` | **وقت** (waqt) — unit 8 (Sounds from Arabic and Persian) — time; read the vowel marks: وَقْت
347. `units/u08_15` | **خالی** (k͟hālī) — unit 8 (Sounds from Arabic and Persian) — empty
348. `units/u08_16` | **غم** (g͟ham) — unit 8 (Sounds from Arabic and Persian) — grief; read the vowel marks: غَم
349. `units/u08_17` | **عام** (ʻām) — unit 8 (Sounds from Arabic and Persian) — common
350. `units/u08_18` | **حساب** (ḥisāb) — unit 8 (Sounds from Arabic and Persian) — maths; read the vowel marks: حِساب
351. `units/u08_19` | **دفتر** (daftar) — unit 8 (Sounds from Arabic and Persian) — office; read the vowel marks: دَفْتَر
352. `units/u09_00` | **صبح** (ṣubḥ) — unit 9 (Same sound, different letter) — morning; read the vowel marks: صُبْح
353. `units/u09_01` | **صبر** (ṣabr) — unit 9 (Same sound, different letter) — patience; read the vowel marks: صَبْر
354. `units/u09_02` | **ضرور** (ẕarūr) — unit 9 (Same sound, different letter) — certainly; read the vowel marks: ضَرور
355. `units/u09_03` | **مریض** (marīẕ) — unit 9 (Same sound, different letter) — patient; read the vowel marks: مَریض
356. `units/u09_04` | **طالب** (t̤ālib) — unit 9 (Same sound, different letter) — student; read the vowel marks: طالِب
357. `units/u09_05` | **طوطا** (t̤ot̤ā) — unit 9 (Same sound, different letter) — parrot
358. `units/u09_06` | **ظاہر** (z̤āhir) — unit 9 (Same sound, different letter) — apparent; read the vowel marks: ظاہِر
359. `units/u09_07` | **ظلم** (z̤ulm) — unit 9 (Same sound, different letter) — cruelty; read the vowel marks: ظُلْم
360. `units/u09_08` | **ذائقہ** (ẕāʾiqa) — unit 9 (Same sound, different letter) — taste (ئ preview); read the vowel marks: ذائِقَہ
361. `units/u09_09` | **ذمہ** (ẕimma) — unit 9 (Same sound, different letter) — responsibility; read the vowel marks: ذِمّہ
362. `units/u09_10` | **صابن** (ṣābun) — unit 9 (Same sound, different letter) — soap; read the vowel marks: صابُن
363. `units/u09_11` | **ضد** (ẕid) — unit 9 (Same sound, different letter) — stubbornness; read the vowel marks: ضِد
364. `units/u09_12` | **طاقت** (t̤āqat) — unit 9 (Same sound, different letter) — strength; read the vowel marks: طاقَت
365. `units/u09_13` | **حفاظت** (ḥifāz̤at) — unit 9 (Same sound, different letter) — protection; read the vowel marks: حِفاظَت
366. `units/u09_14` | **ذرا** (ẕarā) — unit 9 (Same sound, different letter) — a little; read the vowel marks: ذَرا
367. `units/u09_15` | **خاص** (k͟hāṣ) — unit 9 (Same sound, different letter) — special
368. `units/u09_16` | **ثواب** (s̱awāb) — unit 9 (Same sound, different letter) — reward; read the vowel marks: ثَواب
369. `units/u09_17` | **نظر** (naz̤ar) — unit 9 (Same sound, different letter) — sight; read the vowel marks: نَظْر
370. `units/u09_18` | **لفظ** (lafz̤) — unit 9 (Same sound, different letter) — word; read the vowel marks: لَفْظ
371. `units/u09_19` | **صحیح** (ṣaḥīḥ) — unit 9 (Same sound, different letter) — correct; read the vowel marks: صَحیح
372. `units/u10_00` | **آم** (ām) — unit 10 (Hamza, marks and numbers) — mango
373. `units/u10_01` | **آپ** (āp) — unit 10 (Hamza, marks and numbers) — you (polite)
374. `units/u10_02` | **کوئی** (koʾī) — unit 10 (Hamza, marks and numbers) — someone
375. `units/u10_03` | **گئے** (gaʾe) — unit 10 (Hamza, marks and numbers) — went; read the vowel marks: گَئے
376. `units/u10_04` | **مسئلہ** (masʾala) — unit 10 (Hamza, marks and numbers) — problem; read the vowel marks: مَسْئَلہ
377. `units/u10_05` | **بچّہ** (bachcha) — unit 10 (Hamza, marks and numbers) — child; read the vowel marks: بَچّہ
378. `units/u10_06` | **اللّٰہ** (allāh) — unit 10 (Hamza, marks and numbers) — God; read the vowel marks: اَللّٰہ
379. `units/u10_07` | **دعا** (duʻā) — unit 10 (Hamza, marks and numbers) — prayer; read the vowel marks: دُعا
380. `units/u10_08` | **سؤال** (suwāl) — unit 10 (Hamza, marks and numbers) — question; read the vowel marks: سُؤال
381. `units/u10_09` | **آئینہ** (āʾīna) — unit 10 (Hamza, marks and numbers) — mirror
382. `units/u10_10` | **نئی** (naʾī) — unit 10 (Hamza, marks and numbers) — new (f.); read the vowel marks: نَئی
383. `units/u10_11` | **چائے** (chāʾe) — unit 10 (Hamza, marks and numbers) — tea
384. `units/u10_12` | **گائے** (gāʾe) — unit 10 (Hamza, marks and numbers) — cow
385. `units/u10_13` | **اعلیٰ** (aʻlā) — unit 10 (Hamza, marks and numbers) — high; read the vowel marks: اَعلیٰ
386. `units/u10_14` | **صلوٰۃ** (ṣalāt) — unit 10 (Hamza, marks and numbers) — prayer; read the vowel marks: صَلوٰۃ
387. `units/u10_15` | **دنیا** (dunyā) — unit 10 (Hamza, marks and numbers) — world; read the vowel marks: دُنیا
388. `units/u10_16` | **ابّا** (abbā) — unit 10 (Hamza, marks and numbers) — dad; read the vowel marks: اَبّا
389. `units/u10_17` | **امّی** (ammī) — unit 10 (Hamza, marks and numbers) — mum; read the vowel marks: اَمّی
390. `units/u10_18` | **مکّہ** (makka) — unit 10 (Hamza, marks and numbers) — Makkah; read the vowel marks: مَکّہ
391. `units/u10_19` | **اچّھا** (achchhā) — unit 10 (Hamza, marks and numbers) — good; read the vowel marks: اَچّھا
392. `units/u11_00` | **کا** (kā) — unit 11 (Reading like a grown-up) — of (m.)
393. `units/u11_01` | **کی** (kī) — unit 11 (Reading like a grown-up) — of (f.)
394. `units/u11_02` | **کے** (ke) — unit 11 (Reading like a grown-up) — of (pl.)
395. `units/u11_03` | **سے** (se) — unit 11 (Reading like a grown-up) — from
396. `units/u11_04` | **پر** (par) — unit 11 (Reading like a grown-up) — on; read the vowel marks: پَر
397. `units/u11_05` | **کہ** (keh) — unit 11 (Reading like a grown-up) — that; read the vowel marks: کَہ
398. `units/u11_06` | **اور** (aur) — unit 11 (Reading like a grown-up) — and; read the vowel marks: اَور
399. `units/u11_07` | **ہے** (hai) — unit 11 (Reading like a grown-up) — is; read the vowel marks: ہَے
400. `units/u11_08` | **ہیں** (haiṉ) — unit 11 (Reading like a grown-up) — are; read the vowel marks: ہَیں
401. `units/u11_09` | **نے** (ne) — unit 11 (Reading like a grown-up) — (agent)
402. `units/u11_10` | **کو** (ko) — unit 11 (Reading like a grown-up) — to
403. `units/u11_11` | **نہیں** (nahīṉ) — unit 11 (Reading like a grown-up) — no / not; read the vowel marks: نَہیں
404. `units/u11_12` | **تھا** (thā) — unit 11 (Reading like a grown-up) — was
405. `units/u11_13` | **تھی** (thī) — unit 11 (Reading like a grown-up) — was (f.)
406. `units/u11_14` | **کیا** (kyā) — unit 11 (Reading like a grown-up) — what
407. `units/u11_15` | **بھی** (bhī) — unit 11 (Reading like a grown-up) — also
408. `units/u11_16` | **لیکن** (lekin) — unit 11 (Reading like a grown-up) — but; read the vowel marks: لیکِن
409. `units/u11_17` | **اگر** (agar) — unit 11 (Reading like a grown-up) — if; read the vowel marks: اَگَر
410. `units/u11_18` | **پھر** (phir) — unit 11 (Reading like a grown-up) — then; read the vowel marks: پِھر
411. `units/u11_19` | **بہت** (bahut) — unit 11 (Reading like a grown-up) — very; read the vowel marks: بَہُت

## 7 · Unit sentences

412. `sentences/u01_00` | **بابا کا کام** (bābā kā kām) — unit 1 (The first six) — dad's work
413. `sentences/u01_01` | **کالا بال** (kālā bāl) — unit 1 (The first six) — black hair
414. `sentences/u01_02` | **نمک لا** (namak lā) — unit 1 (The first six) — bring salt; read the vowel marks: نَمَک لا
415. `sentences/u02_00` | **تین کتاب** (tīn kitāb) — unit 2 (Dots and the two ye) — three books; read the vowel marks: تین کِتاب
416. `sentences/u02_01` | **بلی کالی ہے** (billī kālī hai) — unit 2 (Dots and the two ye) — the cat is black (ہے is a sight word); read the vowel marks: بِلّی کالی ہَے
417. `sentences/u02_02` | **نیلا تکیا لے** (nīlā takiya le) — unit 2 (Dots and the two ye) — take the blue pillow; read the vowel marks: نیلا تَکِیا لے
418. `sentences/u03_00` | **پانی لا** (pānī lā) — unit 3 (Finishing the be family) — bring water
419. `sentences/u03_01` | **پتلی بلی** (patlī billī) — unit 3 (Finishing the be family) — thin cat; read the vowel marks: پَتْلی بِلّی
420. `sentences/u03_02` | **میں ٹوپی لے** (maiṉ ṭopī le) — unit 3 (Finishing the be family) — (preview) I take the cap; read the vowel marks: مَیں ٹوپی لے
421. `sentences/u04_00` | **دو روٹی** (do roṭī) — unit 4 (The non-joiners) — two breads
422. `sentences/u04_01` | **وہ کمرہ بڑا ہے** (woh kamra baṛā hai) — unit 4 (The non-joiners) — (preview) that room is big; read the vowel marks: وُہ کَمْرہ بَڑا ہَے
423. `sentences/u04_02` | **ہم دور ہیں** (ham dūr haiṉ) — unit 4 (The non-joiners) — we are far; read the vowel marks: ہَم دور ہَیں
424. `sentences/u05_00` | **چار گلاب** (chār gulāb) — unit 5 (Sīn, jīm and gāf) — four roses; read the vowel marks: چار گُلاب
425. `sentences/u05_01` | **شیر جنگل میں ہے** (sher jangal meṉ hai) — unit 5 (Sīn, jīm and gāf) — the lion is in the forest; read the vowel marks: شیر جَنگَل مَیں ہَے
426. `sentences/u05_02` | **دوست کا جوتا** (dost kā jūtā) — unit 5 (Sīn, jīm and gāf) — friend's shoe; read the vowel marks: دوسْت کا جوتا
427. `sentences/u06_00` | **میں گھر میں ہوں** (maiṉ ghar meṉ hūṉ) — unit 6 (Breath and nose) — I am at home; read the vowel marks: مَیں گَھر مَیں ہوں
428. `sentences/u06_01` | **پھول کہاں ہیں** (phūl kahāṉ haiṉ) — unit 6 (Breath and nose) — where are the flowers; read the vowel marks: پھول کَہاں ہَیں
429. `sentences/u06_02` | **بھائی کھانا کھاتا ہے** (bhāʾī khānā khātā hai) — unit 6 (Breath and nose) — brother eats food; read the vowel marks: بَھائی کھانا کھاتا ہَے
430. `sentences/u07_00` | **لڑکا سڑک پر ہے** (laṛkā saṛak par hai) — unit 7 (Retroflex and z) — the boy is on the road; read the vowel marks: لَڑْکا سَڑَک پَر ہَے
431. `sentences/u07_01` | **بڑا ڈبہ** (baṛā ḍabba) — unit 7 (Retroflex and z) — big box; read the vowel marks: بَڑا ڈَبّہ
432. `sentences/u07_02` | **زمین زرد ہے** (zamīn zard hai) — unit 7 (Retroflex and z) — the ground is yellow; read the vowel marks: زَمین زَرْد ہَے
433. `sentences/u08_00` | **قلم کہاں ہے** (qalam kahāṉ hai) — unit 8 (Sounds from Arabic and Persian) — where is the pen; read the vowel marks: قَلَم کَہاں ہَے
434. `sentences/u08_01` | **باغ خالی ہے** (bāg͟h k͟hālī hai) — unit 8 (Sounds from Arabic and Persian) — the garden is empty; read the vowel marks: باغ خالی ہَے
435. `sentences/u08_02` | **وقت کیا ہوا ہے** (waqt kyā huā hai) — unit 8 (Sounds from Arabic and Persian) — what time is it; read the vowel marks: وَقْت کیا ہُوا ہَے
436. `sentences/u09_00` | **صبح صاف ہے** (ṣubḥ ṣāf hai) — unit 9 (Same sound, different letter) — the morning is clear; read the vowel marks: صُبْح صاف ہَے
437. `sentences/u09_01` | **طوطا ذرا بڑا ہے** (t̤ot̤ā ẕarā baṛā hai) — unit 9 (Same sound, different letter) — the parrot is a bit big; read the vowel marks: طوطا ذَرا بَڑا ہَے
438. `sentences/u09_02` | **یہ لفظ صحیح ہے** (yeh lafz̤ ṣaḥīḥ hai) — unit 9 (Same sound, different letter) — this word is correct; read the vowel marks: یِہ لَفْظ صَحیح ہَے
439. `sentences/u10_00` | **آپ کا نام کیا ہے؟** (āp kā nām kyā hai?) — unit 10 (Hamza, marks and numbers) — what is your name?; read the vowel marks: آپ کا نام کیا ہَے؟
440. `sentences/u10_01` | **چائے میں ۲ چمچ چینی** (chāʾe meṉ do chamach chīnī) — unit 10 (Hamza, marks and numbers) — 2 spoons of sugar in the tea; read the vowel marks: چائے مَیں ۲ چَمَچ چینی
441. `sentences/u10_02` | **کوئی مسئلہ نہیں۔** (koʾī masʾala nahīṉ.) — unit 10 (Hamza, marks and numbers) — no problem.; read the vowel marks: کوئی مَسْئَلہ نَہیں۔
442. `sentences/u11_00` | **میرا نام کمال ہے اور میں لاہور میں رہتا ہوں۔** (merā nām kamāl hai aur maiṉ lāhaur meṉ rahtā hūṉ.) — unit 11 (Reading like a grown-up) — my name is Kamal and I live in Lahore.; read the vowel marks: میرا نام کَمال ہَے اَور مَیں لاہَور مَیں رَہْتا ہوں۔
443. `sentences/u11_01` | **بچے اسکول جاتے ہیں لیکن آج چھٹی ہے۔** (bachche iskūl jāte haiṉ lekin āj chhuṭṭī hai.) — unit 11 (Reading like a grown-up) — the children go to school but today is a holiday.; read the vowel marks: بَچّے اِسْکول جاتے ہَیں لیکِن آج چُھٹّی ہَے۔
444. `sentences/u11_02` | **اگر بارش ہوئی تو ہم گھر پر رہیں گے۔** (agar bārish huʾī to ham ghar par raheṉ ge.) — unit 11 (Reading like a grown-up) — if it rains we will stay home.; read the vowel marks: اَگَر بارِش ہُوئی تو ہَم گَھر پَر رَہیں گے۔

## 8 · Sight words

445. `sight/00` | **کا** (kā) — high-frequency sight word — say naturally, not spelled out
446. `sight/01` | **کی** (kī) — high-frequency sight word — say naturally, not spelled out
447. `sight/02` | **کے** (ke) — high-frequency sight word — say naturally, not spelled out
448. `sight/03` | **سے** (se) — high-frequency sight word — say naturally, not spelled out
449. `sight/04` | **پر** (par) — high-frequency sight word — say naturally, not spelled out
450. `sight/05` | **کہ** (keh) — high-frequency sight word — say naturally, not spelled out
451. `sight/06` | **اور** (aur) — high-frequency sight word — say naturally, not spelled out
452. `sight/07` | **ہے** (hai) — high-frequency sight word — say naturally, not spelled out
453. `sight/08` | **ہیں** (haiṉ) — high-frequency sight word — say naturally, not spelled out
454. `sight/09` | **نے** (ne) — high-frequency sight word — say naturally, not spelled out
455. `sight/10` | **کو** (ko) — high-frequency sight word — say naturally, not spelled out
456. `sight/11` | **میں** (maiṉ) — high-frequency sight word — say naturally, not spelled out
457. `sight/12` | **نہیں** (nahīṉ) — high-frequency sight word — say naturally, not spelled out
458. `sight/13` | **وہ** (woh) — high-frequency sight word — say naturally, not spelled out
459. `sight/14` | **یہ** — high-frequency sight word — say naturally, not spelled out
460. `sight/15` | **اس** — high-frequency sight word — say naturally, not spelled out
461. `sight/16` | **تھا** (thā) — high-frequency sight word — say naturally, not spelled out
462. `sight/17` | **تھی** (thī) — high-frequency sight word — say naturally, not spelled out
463. `sight/18` | **کیا** (kyā) — high-frequency sight word — say naturally, not spelled out
464. `sight/19` | **بھی** (bhī) — high-frequency sight word — say naturally, not spelled out

## 9 · Numerals (spoken as words)

465. `numerals/0` | **صفر** — the number 0, spoken as a word
466. `numerals/1` | **ایک** — the number 1, spoken as a word
467. `numerals/2` | **دو** (do) — the number 2, spoken as a word
468. `numerals/3` | **تین** (tīn) — the number 3, spoken as a word
469. `numerals/4` | **چار** (chār) — the number 4, spoken as a word
470. `numerals/5` | **پانچ** — the number 5, spoken as a word
471. `numerals/6` | **چھے** — the number 6, spoken as a word
472. `numerals/7` | **سات** — the number 7, spoken as a word
473. `numerals/8` | **آٹھ** — the number 8, spoken as a word
474. `numerals/9` | **نو** — the number 9, spoken as a word


---

Total: 474 clips (matches `assets/audio/manifest.json`, 474 entries).
