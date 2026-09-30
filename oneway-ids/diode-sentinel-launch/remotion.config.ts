import { Config } from '@remotion/cli/config';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
execFileSync(process.execPath, ['scripts/prepare-product.mjs'], { stdio: 'inherit' });
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// setMuted() is a no-argument setter; calling it with false still mutes.
if (!existsSync('public/music-master.wav') && !existsSync('public/music.mp3') && !existsSync('public/narration/intro.wav') && !existsSync('public/explainer-narration/intro.wav'))
    Config.setMuted();
Config.setAudioBitrate('192k');
