import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const target = process.argv[2];
const renders = {
  product: ['DiodeSentinelProductDemo', 'out/diode-sentinel-product-demo.mp4'],
  explainer: ['DiodeSentinelExplainer', 'out/diode-sentinel-explainer.mp4'],
};

if (!(target in renders)) {
  console.error('Usage: node scripts/render.mjs <product|explainer>');
  process.exit(2);
}

const [composition, output] = renders[target];
const args = [
  'remotion', 'render', 'src/index.ts', composition, output,
  '--concurrency=2', '--crf=18',
];
if (target === 'explainer') args.push('--offthreadvideo-cache-size-in-bytes=268435456');

const browser = process.env.CHROMIUM_PATH || process.env.CHROME_BIN;
const candidates = [
  browser,
  '/home/stark/.nix-profile/bin/chromium',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);
const selectedBrowser = candidates.find((candidate) => existsSync(candidate));
if (selectedBrowser) args.push(`--browser-executable=${selectedBrowser}`);

const result = spawnSync('npx', args, { stdio: 'inherit', shell: process.platform === 'win32' });
if (result.error) {
  console.error(`Could not start Remotion: ${result.error.message}`);
  process.exit(1);
}
process.exit(result.status ?? 1);
