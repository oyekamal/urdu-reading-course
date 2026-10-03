// Urdu Qaida service worker (round 11p). This file is a TEMPLATE: `npm run build` (mobile/vite-sw-plugin.js) writes dist/sw.js with
// the build injected into the next line, so the worker (and its cache name) changes with every release. In dev BUILD stays null and
// this worker does nothing.
//
//   BUILD = { version: '<package version>-<content hash>', files: { 'rel/path': '<8-hex content hash>' }, eager: ['rel/path', ...] }
//
// Strategy
//   - eager (installed up front): the app shell and everything a screen needs but audio/PDF: index.html, every JS chunk (teacher-*.js and the
//     other lazy chunks), CSS, fonts, data/*.json, lesson markdown, img, lottie, the PDF index.
//   - lazy (cache-first on demand, runtime-cached; the page can ask for a background warm-up): audio/**.mp3 and pdf/*.pdf.
//   - every entry is keyed `<url>?h=<content hash>`, so an unchanged file is copied from the previous version's cache instead of downloaded
//     again, a changed file can never be served stale, and old caches are deleted on activate.
//   - update flow: a new worker installs and WAITS (the open page keeps a consistent old shell); the page shows "Update ready, tap to refresh"
//     and posts SKIP_WAITING; the first install (no controller yet) activates and claims at once.
const BUILD = /*URC_BUILD*/null;
const PREFIX = 'urc-';
const SCOPE = new URL('./', self.location).pathname;
const CACHE = BUILD ? PREFIX + BUILD.version : null;
const rel = url => { const p = new URL(url, self.location).pathname; const r = p.startsWith(SCOPE) ? p.slice(SCOPE.length) : p.replace(/^\//, ''); return decodeURIComponent(r) || 'index.html'; };
const keyOf = path => new URL(path + '?h=' + BUILD.files[path], self.location).href;
const MATCH = { ignoreVary: true };

if (!BUILD) {
  self.addEventListener('install', () => self.skipWaiting());
  self.addEventListener('activate', e => e.waitUntil((async () => { for (const k of await caches.keys()) if (k.startsWith(PREFIX)) await caches.delete(k); await self.clients.claim(); })()));
} else {
  self.addEventListener('install', e => e.waitUntil(install()));
  self.addEventListener('activate', e => e.waitUntil(activate()));
  self.addEventListener('fetch', onFetch);
  self.addEventListener('message', onMessage);
}

async function pool(items, n, fn) {
  let i = 0; const errs = [];
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => { for (; i < items.length;) { const it = items[i++]; try { await fn(it); } catch (e) { errs.push(e); } } }));
  return errs;
}

async function install() {
  const cache = await caches.open(CACHE);
  // 1. reuse what an older version already downloaded (same path AND same content hash), including lazily cached audio/PDFs
  for (const name of (await caches.keys()).filter(k => k.startsWith(PREFIX) && k !== CACHE)) {
    const old = await caches.open(name);
    for (const req of await old.keys()) {
      const u = new URL(req.url); const p = rel(u.href);
      if (BUILD.files[p] && u.searchParams.get('h') === BUILD.files[p] && !(await cache.match(req, MATCH))) { const r = await old.match(req, MATCH); if (r) await cache.put(req, r); }
    }
  }
  // 2. download the rest of the eager set; one failure fails the install (retried on the next visit), so a half-cached shell is never activated
  const todo = [];
  for (const p of BUILD.eager) if (!(await cache.match(keyOf(p), MATCH))) todo.push(p);
  const errs = await pool(todo, 8, async p => { const res = await fetch(p, { cache: 'reload' }); if (!res.ok) throw new Error(p + ' ' + res.status); await cache.put(keyOf(p), res); });
  if (errs.length) throw errs[0];
  // first install (nothing to keep consistent) or an upgrade from the pre-11p worker (its pages have no "update ready" button): take over now
  const legacy = (await caches.keys()).some(k => /^urc-v\d/.test(k));
  if (!self.registration.active || legacy) self.skipWaiting();
}

async function activate() {
  for (const k of await caches.keys()) if (k.startsWith(PREFIX) && k !== CACHE) await caches.delete(k);
  await self.clients.claim();
}

function onFetch(e) {
  const req = e.request;
  if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (u.origin !== self.location.origin) return;
  let p = rel(u.href);
  if (req.mode === 'navigate' && !(p in BUILD.files) && !/\.[a-z0-9]+$/i.test(p)) p = 'index.html';   // /reader/, /reader/?x -> the shell; a PDF opened in a tab is just a file
  if (!(p in BUILD.files)) return;                       // not part of the build (dev tools, unknown URLs): plain network
  e.respondWith(serve(req, p));
}

async function serve(req, p) {
  const cache = await caches.open(CACHE);
  let hit = await cache.match(keyOf(p), MATCH);
  if (!hit) {
    try {
      const res = await fetch(new URL(p, self.location).href);
      if (res.ok && res.status === 200) { cache.put(keyOf(p), res.clone()).catch(() => {}); hit = res; }
      else return res;
    } catch (err) { return req.mode === 'navigate' ? (await cache.match(keyOf('index.html'), MATCH)) || Response.error() : Response.error(); }
  }
  const range = req.headers.get('range');
  return range ? rangeOf(hit, range) : hit;
}

// <audio> asks for byte ranges; Safari insists on a proper 206. Serve one from the cached full body.
async function rangeOf(res, header) {
  const m = /^bytes=(\d*)-(\d*)$/.exec(header); if (!m) return res;
  const buf = await res.clone().arrayBuffer(), size = buf.byteLength;
  let start = m[1] === '' ? Math.max(0, size - Number(m[2])) : Number(m[1]); let end = m[1] !== '' && m[2] !== '' ? Math.min(Number(m[2]), size - 1) : size - 1;
  if (start >= size) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + size } });
  const h = new Headers(res.headers); h.set('Content-Range', `bytes ${start}-${end}/${size}`); h.set('Content-Length', String(end - start + 1)); h.set('Accept-Ranges', 'bytes');
  return new Response(buf.slice(start, end + 1), { status: 206, statusText: 'Partial Content', headers: h });
}

let warming = false;
async function warm() {
  if (warming) return; warming = true;
  try {
    if (self.navigator.connection && self.navigator.connection.saveData) return;
    const cache = await caches.open(CACHE);
    const todo = [];
    for (const p of Object.keys(BUILD.files)) if (p.startsWith('audio/') && !(await cache.match(keyOf(p), MATCH))) todo.push(p);
    for (let i = 0; i < todo.length; i += 4) {
      if (self.navigator.onLine === false) break;
      await Promise.all(todo.slice(i, i + 4).map(async p => { try { const res = await fetch(p); if (res.ok) await cache.put(keyOf(p), res); } catch (e) {} }));
      await new Promise(r => setTimeout(r, 120));         // low priority: leave room for whatever the child is doing
    }
  } finally { warming = false; }
}

function onMessage(e) {
  const d = e.data || {};
  if (d.type === 'SKIP_WAITING') self.skipWaiting();
  else if (d.type === 'WARM') e.waitUntil(warm());
  else if (d.type === 'VERSION' && e.source) e.source.postMessage({ type: 'VERSION', version: BUILD.version });
}
