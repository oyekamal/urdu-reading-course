import pkg from './package.json' with { type: 'json' };
export default { base: './', define: { __APP_VERSION__: JSON.stringify(pkg.version) }, build: { target: 'es2019', assetsInlineLimit: 0 } };
