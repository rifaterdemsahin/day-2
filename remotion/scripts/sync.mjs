// Copies the one source of truth (../assets/short.json) next to the code and
// records which clips/voice exist, so Studio shows real clips or placeholders.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, '..', 'assets', 'short.json'), 'utf8'));
// the voice drives the cuts: assets/scene_timing.json (written by scripts/make_voice.py) overrides scene times
const tp = path.join(root, '..', 'assets', 'scene_timing.json');
if (fs.existsSync(tp)) {
  const tm = JSON.parse(fs.readFileSync(tp, 'utf8'));
  data.length_s = tm.length_s;
  for (const sc of data.scenes) {
    const r = tm.scenes.find((x) => x.clip === sc.clips[0]);
    if (r) { sc.start = r.start; sc.end = r.end; }
  }
}
fs.writeFileSync(path.join(root, 'src', 'short.json'), JSON.stringify(data, null, 2));
const clipsDir = path.join(root, 'public', 'clips');
const clips = fs.existsSync(clipsDir) ? fs.readdirSync(clipsDir).filter((f) => /^S2-04-.+\.mp4$/.test(f)) : [];
const vo = fs.existsSync(path.join(root, 'public', 'S2-05-vo.wav')) ? 'S2-05-vo.wav' : null;
// optional real word timings from Whisper (S2-05): assets/words.json = [{word, start, end}] in seconds on the final timeline
const wp = path.join(root, '..', 'assets', 'words.json');
const words = fs.existsSync(wp) ? JSON.parse(fs.readFileSync(wp, 'utf8')) : [];
fs.writeFileSync(path.join(root, 'public', 'available.json'), JSON.stringify({clips, vo, words}, null, 2));
console.log(`sync: ${clips.length} clip(s), voice ${vo ? 'found' : 'not yet'}, ${words.length} timed word(s)`);
