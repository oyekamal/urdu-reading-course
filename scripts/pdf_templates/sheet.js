// Start dot + arrow for tracing guides.
// Where the dot goes (data-mode):
//   default    : the app's own tracer rule (mobile/src/drills.js writeIt): just outside the right edge of the glyph, a little below the top of that edge.
//   topmost    : the highest point of the letter (tall strokes that begin at the top: lam, dal family, ain family).
//   baseRight  : the right end of the lower stroke (kaf/gaf: the base stroke comes first, hamza seat: the body comes first).
// Middle and end forms start where the line comes in from the previous letter (right end of the joining line), arrow below the line.
// The arrow is drawn beside the ink, never on top of it (data-dir: left, leftb, down, downleft).
window.placeStarts = function () {
  const k = 96 / 25.4, NS = 'http://www.w3.org/2000/svg';
  for (const g of document.querySelectorAll('g.sd')) {
    const em = +g.dataset.em, cx = +g.dataset.cx, by = +g.dataset.by, px = em * k, mode = g.dataset.mode || 'default';
    const W = Math.ceil(px * 3), H = Math.ceil(px * 2.2), c = document.createElement('canvas'); c.width = W; c.height = H;
    const x = c.getContext('2d', { willReadFrequently: true }); x.direction = 'rtl'; x.textAlign = 'center'; x.textBaseline = 'alphabetic';
    x.font = px + 'px "URC Naskh"'; const bl = Math.round(H * 0.62); x.fillText(g.dataset.txt, W / 2, bl);
    const d = x.getImageData(0, 0, W, H).data, s = px / 170;
    let maxx = 0, top = H, bottom = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 0) { const xx = (i >> 2) % W, yy = (i >> 2) / W | 0; if (xx > maxx) maxx = xx; if (yy < top) top = yy; if (yy > bottom) bottom = yy; }
    let sx, sy;
    if (mode === 'topmost') {
      let t0 = top;
      if (g.dataset.above === '1') { // the letter's own dot sits above the body: skip that blob (rows separated by an empty gap)
        const rowHas = y => { for (let xx = 0; xx < W; xx++) if (d[(y * W + xx) * 4 + 3] > 0) return true; return false; };
        let y = top; while (y < H && rowHas(y)) y++; let g0 = y; while (g0 < H && !rowHas(g0)) g0++;
        if (g0 < H && g0 - y >= 2 && g0 - top < 0.5 * px) t0 = g0;
      }
      let mx = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) { const xx = (i >> 2) % W, yy = (i >> 2) / W | 0; if (yy >= t0 && yy < t0 + 3 * s && xx > mx) mx = xx; }
      sx = mx + 14 * s; sy = t0 + 8 * s;
    } else if (mode === 'baseRight') {
      let mx = 0, my = bl; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) { const xx = (i >> 2) % W, yy = (i >> 2) / W | 0; if (yy > bl - 0.2 * px && yy < bl + 0.02 * px && xx > mx) { mx = xx; my = yy; } }
      sx = mx + 12 * s; sy = my - 8 * s;
    } else {
      let tb = top;
      if (g.dataset.above === '1') { // skip the letter's own dot blob (separated from the body by empty rows)
        const rowHas = y => { for (let xx = 0; xx < W; xx++) if (d[(y * W + xx) * 4 + 3] > 0) return true; return false; };
        let y = top; while (y < H && rowHas(y)) y++; let g0 = y; while (g0 < H && !rowHas(g0)) g0++;
        if (g0 < H && g0 - y >= 2 && g0 - top < 0.5 * px) tb = g0;
      }
      let t2 = H, mx2 = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) { const xx = (i >> 2) % W, yy = (i >> 2) / W | 0; if (yy >= tb && xx > mx2) mx2 = xx; }
      for (let i = 3; i < d.length; i += 4) if (d[i] > 0) { const xx = (i >> 2) % W, yy = (i >> 2) / W | 0; if (yy >= tb && xx > mx2 - 6 * s && yy < t2) t2 = yy; }
      sx = mx2 + 10 * s; sy = t2 + 20 * s;
    }
    const dx = cx + (sx - W / 2) / k, dy = by + (sy - bl) / k, R = +g.dataset.r || 1.15;
    const mk = (t, a) => { const e = document.createElementNS(NS, t); for (const q in a) e.setAttribute(q, a[q]); g.appendChild(e); return e; };
    mk('circle', { cx: dx, cy: dy, r: R, fill: '#12766c' });
    if (g.dataset.arrow === '1') {
      const dir = g.dataset.dir, L = 10, st = { fill: 'none', stroke: '#12766c', 'stroke-width': .75, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
      const glyphTop = by + (top - bl) / k, glyphBot = by + (bottom - bl) / k;
      let x1, y1, x2, y2, head;
      if (dir === 'down') { x1 = dx + 3.2; y1 = dy - 1; x2 = x1; y2 = y1 + L; head = `M${x2 - 1.8} ${y2 - 2.4}L${x2} ${y2}L${x2 + 1.8} ${y2 - 2.4}`; }
      else if (dir === 'downleft') { x1 = dx + 4; y1 = dy - 2.5; x2 = x1 - L * .45; y2 = y1 + L * .85; head = `M${x2 + 2.8} ${y2 - .6}L${x2} ${y2}L${x2 + .6} ${y2 - 2.8}`; }
      else if (dir === 'leftb') { x1 = dx; y1 = Math.max(dy + 4, glyphBot + 2.4); x2 = x1 - L; y2 = y1; head = `M${x2 + 2.4} ${y2 - 1.8}L${x2} ${y2}L${x2 + 2.4} ${y2 + 1.8}`; }
      else { x1 = dx - 1; y1 = Math.max(2, Math.min(dy - 5.4, glyphTop - 2.5)); x2 = x1 - L; y2 = y1; head = `M${x2 + 2.4} ${y2 - 1.8}L${x2} ${y2}L${x2 + 2.4} ${y2 + 1.8}`; }
      mk('path', { ...st, d: `M${x1} ${y1}L${x2} ${y2}${head}` });
    }
    g.dataset.dot = dx.toFixed(2) + ',' + dy.toFixed(2);
  }
};

// Chromium writes a CSS border/background with border-radius as hundreds of path segments (about 1 KB per circle);
// an SVG rect is about 80 bytes. Swap every rounded border/background for an SVG child painted behind the element's
// own content (isolation:isolate keeps its z-index:-1 inside the element).
window.vectorizeBorders = function () {
  const NS = 'http://www.w3.org/2000/svg';
  for (const e of document.querySelectorAll('body *')) {
    if (e.closest('svg')) continue;
    const cs = getComputedStyle(e), bw = parseFloat(cs.borderTopWidth) || 0, hasB = bw > 0 && cs.borderTopStyle !== 'none';
    const bg = cs.backgroundColor, hasBg = bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
    if (cs.borderTopLeftRadius === '0px' || (!hasB && !hasBg) || cs.backgroundImage !== 'none') continue;
    const W = e.offsetWidth, H = e.offsetHeight; if (!W || !H) continue;
    let r = cs.borderTopLeftRadius; r = r.includes('%') ? Math.min(W, H) * parseFloat(r) / 100 : parseFloat(r); r = Math.min(r, Math.min(W, H) / 2);
    if (cs.position === 'static') e.style.position = 'relative';
    e.style.isolation = 'isolate';
    const s = document.createElementNS(NS, 'svg'); s.setAttribute('width', W); s.setAttribute('height', H); s.setAttribute('viewBox', `0 0 ${W} ${H}`);
    s.style.cssText = `position:absolute;left:${-bw}px;top:${-bw}px;z-index:-1;overflow:visible;pointer-events:none;width:${W}px;height:${H}px`;
    const x = hasB ? bw / 2 : 0, rc = document.createElementNS(NS, 'rect');
    const a = { x, y: x, width: W - 2 * x, height: H - 2 * x, rx: Math.max(0, r - x), fill: hasBg ? bg : 'none' };
    if (hasB) { a.stroke = cs.borderTopColor; a['stroke-width'] = bw; if (cs.borderTopStyle === 'dashed') a['stroke-dasharray'] = `${bw * 3} ${bw * 3}`; }
    for (const k in a) rc.setAttribute(k, a[k]); s.appendChild(rc);
    e.style.backgroundColor = 'transparent'; if (hasB) e.style.borderColor = 'transparent'; e.insertBefore(s, e.firstChild);
  }
};
