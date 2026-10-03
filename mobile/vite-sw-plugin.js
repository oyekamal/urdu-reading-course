// Build step for the service worker (round 11p). After Vite has written dist/ (incl. everything copied from public/):
//   1. removes files the app no longer references (the full Urdu TTFs; the app loads the WOFF2 subsets) so they are neither published nor cached
//   2. hashes every remaining file and writes dist/sw.js = public/sw.js with the build injected:
//        version = <package version>-<12 hex of the hash over all file hashes>, files = path -> 8 hex content hash, eager = what install must fetch
// A new build with any changed byte therefore changes sw.js, so browsers install it and the page offers "Update ready".
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, writeFileSync, statSync, rmSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

// Audio the first minutes need (onboarding, letter names, example words, units 0 and 1) ships with the install, the rest of the clips are
// fetched on demand and warmed in the background; PDFs are on demand only.
const EAGER_AUDIO = p => /^audio\/(ui|names|words|syllables)\//.test(p) || /^audio\/units\/u0[01]_/.test(p);
const LAZY = p => (p.startsWith('audio/') && !EAGER_AUDIO(p)) || (p.startsWith('pdf/') && p.endsWith('.pdf'));
const SKIP = p => p === 'sw.js' || p.startsWith('.vite/') || p === 'lottie/preview.html' || p === 'lottie/CREDITS.md' || p === 'lottie/list.json' || p === 'img/list.json' || p.endsWith('.ttf') || p.endsWith('.map');

function walk(dir, out = []) {
  for (const n of readdirSync(dir)) { const f = join(dir, n); statSync(f).isDirectory() ? walk(f, out) : out.push(f); }
  return out;
}

export function swPlugin(version) {
  let outDir = 'dist';
  return {
    name: 'urdu-sw',
    apply: 'build',
    enforce: 'post',
    configResolved(c) { outDir = c.build.outDir; },
    closeBundle() {
      const root = outDir;
      for (const f of walk(root)) if (f.endsWith('.ttf')) rmSync(f);
      // pretty-printed content JSON -> compact (units.json was 35 KB of indentation): fewer bytes on the wire for every platform, same data
      for (const f of walk(root)) if (/[\\/]data[\\/][^\\/]+\.json$|[\\/]pdf[\\/]index\.json$/.test(f)) { try { const raw = readFileSync(f, 'utf8'), min = JSON.stringify(JSON.parse(raw)); if (min.length < raw.length) writeFileSync(f, min); } catch (e) { /* leave as is */ } }
      const files = {}, eager = [];
      for (const f of walk(root).sort()) {
        const p = relative(root, f).split(sep).join('/');
        if (SKIP(p)) continue;
        files[p] = createHash('sha256').update(readFileSync(f)).digest('hex').slice(0, 8);
        if (!LAZY(p)) eager.push(p);
      }
      const all = createHash('sha256').update(JSON.stringify(files)).digest('hex').slice(0, 12);
      const build = { version: `${version}-${all}`, files, eager };
      const tpl = readFileSync(join(root, 'sw.js'), 'utf8');
      if (!tpl.includes('/*URC_BUILD*/null')) throw new Error('sw.js template marker missing');
      writeFileSync(join(root, 'sw.js'), tpl.replace('/*URC_BUILD*/null', () => JSON.stringify(build)));
      const mb = n => (n / 1048576).toFixed(2);
      const size = l => l.reduce((a, p) => a + statSync(join(root, p)).size, 0);
      console.log(`\n[urdu-sw] ${build.version}: ${eager.length} eager files (${mb(size(eager))} MB), ${Object.keys(files).length - eager.length} lazy (${mb(size(Object.keys(files).filter(LAZY)))} MB)`);
    },
  };
}

// Inline the (single) stylesheet into index.html: no render-blocking request, so the first paint needs only the HTML. relative url()s are
// rewritten from "../" (the file lived in assets/) to "./" (index.html lives at the root).
export function inlineCss() {
  return {
    name: 'urdu-inline-css',
    apply: 'build',
    enforce: 'post',
    transformIndexHtml: {
      order: 'post',
      handler(html, ctx) {
        const bundle = ctx && ctx.bundle; if (!bundle) return html;
        return html.replace(/<link rel="stylesheet"[^>]*href="\.\/(assets\/[^"]+\.css)"[^>]*>/g, (m, f) => {
          const a = bundle[f]; if (!a || a.type !== 'asset') return m;
          const css = String(a.source).replace(/url\(\.\.\//g, 'url(./'); delete bundle[f];
          return `<style>${css}</style>`;
        });
      },
    },
  };
}
