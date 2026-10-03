import pkg from './package.json' with { type: 'json' };
import { swPlugin, inlineCss } from './vite-sw-plugin.js'; // round 11p: writes dist/sw.js with the build version + precache manifest
// Production Content-Security-Policy (round 11a): injected into the built index.html only, so the dev server keeps its inline HMR client.
// No inline scripts, no eval, nothing from another origin; styles may be inline (the app sets style attributes); object/embed/base/form are closed.
const CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob: data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'";
const csp = () => ({
  name: 'urdu-csp',
  apply: 'build',
  transformIndexHtml: { order: 'post', handler: html => html.replace(/<meta charset="utf-8">/i, m => `${m}\n<meta http-equiv="Content-Security-Policy" content="${CSP}">`) },
});
export default { base: './', plugins: [csp(), inlineCss(), swPlugin(pkg.version)], define: { __APP_VERSION__: JSON.stringify(pkg.version) }, build: { target: 'es2019', assetsInlineLimit: 0 } };
