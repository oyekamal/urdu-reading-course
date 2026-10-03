#!/usr/bin/env python3
"""Subset the two Urdu fonts for the app (round 11p, perf): keep the Urdu repertoire (letters incl. the Urdu-only ones, vowel marks,
punctuation, both digit sets, joiners, space/ASCII digits+punctuation) and ALL shaping tables (GSUB/GPOS/GDEF, every feature), so
joined forms come out identical. Output is WOFF2 into mobile/public/fonts/. Full TTFs stay in assets/fonts/ for the PDF/card tools.

  python3 scripts/subset_fonts.py            # writes NotoNaskhArabic-ur.woff2, NotoNastaliqUrdu-ur.woff2
Run by scripts/sync_mobile_content.sh. Needs fonttools + brotli.
"""
import pathlib, sys
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / 'assets/fonts', ROOT / 'mobile/public/fonts'
RANGES = [
    (0x20, 0x7E), (0xA0, 0x24F), (0x2B0, 0x2FF), (0x300, 0x36F), (0x1E00, 0x1EFF),   # space, ASCII, Latin-1 + Latin Extended (romanisation inside .ur runs), modifier letters, combining marks (names like kām, ṭh)
    (0x60C, 0x60C), (0x61B, 0x61B), (0x61F, 0x61F),                          # Arabic comma, semicolon, question mark
    (0x621, 0x63A), (0x640, 0x655), (0x658, 0x658),                          # letters, tatweel, vowel marks (fatha..sukun, hamza marks), mark noon ghunna
    (0x660, 0x66D), (0x670, 0x670), (0x674, 0x674),                          # Arabic-Indic digits, % . , *, dagger alef, high hamza
    (0x679, 0x679), (0x67E, 0x67E), (0x686, 0x686), (0x688, 0x688), (0x690, 0x691), (0x698, 0x698),   # ٹ پ چ ڈ ڑ ژ
    (0x6A9, 0x6A9), (0x6AD, 0x6AD), (0x6AF, 0x6AF), (0x6BA, 0x6BB), (0x6BE, 0x6BE),                  # ک گ ں ھ
    (0x6C0, 0x6C3), (0x6C6, 0x6C8), (0x6CC, 0x6CC), (0x6D2, 0x6D5),                                  # ہ ۂ ۃ ی ے ۓ ۔
    (0x6F0, 0x6F9),                                                          # Extended Arabic-Indic digits (Urdu numerals)
    (0x200C, 0x200F), (0x2013, 0x2014), (0x2018, 0x2019), (0x201C, 0x201D), (0x2022, 0x2022), (0x2026, 0x2026), (0x25CC, 0x25CC),
]
UNICODES = [c for a, b in RANGES for c in range(a, b + 1)]
JOBS = [('NotoNaskhArabic.ttf', 'NotoNaskhArabic-ur.woff2'), ('NotoNastaliqUrdu-Regular.ttf', 'NotoNastaliqUrdu-ur.woff2')]

def main():
    DST.mkdir(parents=True, exist_ok=True)
    for src, dst in JOBS:
        opts = subset.Options(); opts.layout_features = ['*']; opts.notdef_outline = True; opts.name_IDs = ['*']; opts.flavor = 'woff2'
        opts.glyph_names = False; opts.hinting = False; opts.legacy_kern = True; opts.layout_closure = True
        font = TTFont(SRC / src); n0 = len(font.getGlyphOrder())
        s = subset.Subsetter(opts); s.populate(unicodes=UNICODES); s.subset(font)
        out = DST / dst; font.flavor = 'woff2'; font.save(out)
        print(f'{src}: {(SRC / src).stat().st_size:>7} B, {n0} glyphs  ->  {dst}: {out.stat().st_size:>7} B, {len(TTFont(out).getGlyphOrder())} glyphs')

if __name__ == '__main__':
    sys.exit(main())
