// Copies the one source of truth (../assets/short.json) next to the code and
// records which clips/voice exist, so Studio shows real clips or placeholders.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
fs.copyFileSync(path.join(root, '..', 'assets', 'short.json'), path.join(root, 'src', 'short.json'));
const clipsDir = path.join(root, 'public', 'clips');
const clips = fs.existsSync(clipsDir) ? fs.readdirSync(clipsDir).filter((f) => /^S2-04-.+\.mp4$/.test(f)) : [];
const vo = fs.existsSync(path.join(root, 'public', 'S2-05-vo.wav')) ? 'S2-05-vo.wav' : null;
fs.writeFileSync(path.join(root, 'public', 'available.json'), JSON.stringify({clips, vo}, null, 2));
console.log(`sync: ${clips.length} clip(s), voice ${vo ? 'found' : 'not yet'}`);
