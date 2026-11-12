#!/usr/bin/env python3
"""S2-05 voice-over: text-to-speech with ElevenLabs through fal.ai.

  FAL_KEY=... python3 -I scripts/make_voice.py [--voice Aria] [--text "..."] [--dry-run] [--force]

Reads the script from assets/short.json (scenes[].vo) and settings from its "voice" block.
Key: environment variable FAL_KEY, or the macOS Keychain item with service name "fal-key".
The key is never printed or written to a file.
Writes: remotion/public/S2-05-vo.wav (+ .mp3 original), assets/words.json (word timings for the
animated captions). Word timings come from the endpoint's timestamps; if their shape is not
recognised, Whisper is used on the audio instead.
"""
import argparse, difflib, json, os, pathlib, re, subprocess, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "assets/short.json").read_text(encoding="utf-8"))
V = DATA.get("voice", {})


def get_key():
    k = os.environ.get("FAL_KEY")
    if k:
        return k.strip()
    try:
        out = subprocess.run(["security", "find-generic-password", "-s", "fal-key", "-w"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return ""


def call(url, key, body=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
                                 method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:400]
        sys.exit(f"fal.ai HTTP {e.code}: {msg}" + ("\n(401/403: key missing, wrong or no credit)" if e.code in (401, 403) else ""))


def run_fal(endpoint, payload, key):
    r = call(f"https://queue.fal.run/{endpoint}", key, payload)
    if "audio" in r:
        return r
    status_url, response_url = r.get("status_url"), r.get("response_url")
    for _ in range(90):
        s = call(status_url, key)
        st = s.get("status")
        if st == "COMPLETED":
            return call(response_url or s.get("response_url"), key)
        if st not in ("IN_QUEUE", "IN_PROGRESS"):
            sys.exit(f"fal.ai job ended with status {st}: {json.dumps(s)[:300]}")
        time.sleep(2)
    sys.exit("fal.ai job timed out")


def parse_timestamps(ts):
    """Return [{word,start,end}] seconds, or [] if the shape is not recognised."""
    out = []
    if not isinstance(ts, list):
        return out
    for e in ts:
        if not isinstance(e, dict):
            return []
        w = e.get("word") or e.get("text") or e.get("token")
        s = e.get("start", e.get("start_time", e.get("start_s")))
        t = e.get("end", e.get("end_time", e.get("end_s")))
        if w is None or s is None or t is None:
            return []
        out.append({"word": str(w).strip(), "start": float(s), "end": float(t)})
    return [x for x in out if x["word"]]


def whisper_words(audio):
    tmp = ROOT / "assets" / "_whisper"
    tmp.mkdir(exist_ok=True)
    try:
        r = subprocess.run(["whisper", str(audio), "--model", "small", "--language", "en", "--word_timestamps", "True",
                            "--output_format", "json", "--output_dir", str(tmp)], capture_output=True, text=True)
        out = tmp / (audio.stem + ".json")
        if r.returncode != 0 or not out.exists():
            sys.exit("Whisper failed:\n" + (r.stderr or r.stdout)[-600:])
        j = json.loads(out.read_text())
        return [{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
                for seg in j["segments"] for w in seg.get("words", [])]
    finally:
        for f in tmp.glob("*"):
            f.unlink()
        tmp.rmdir()


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def align(script_words, timed):
    """Give every word of OUR script a real time. Matching words take the recognised timing;
    words the recogniser wrote differently (numbers, mishearings) are spread between their
    matched neighbours. Captions then show the script's wording with the speech's timing."""
    n = len(script_words)
    if not n or not timed:
        return []
    a = [_norm(w) for w in script_words]
    b = [_norm(x["word"]) for x in timed]
    out = [None] * n
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            out[blk.a + k] = (timed[blk.b + k]["start"], timed[blk.b + k]["end"])
    i = 0
    while i < n:
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < n and out[j] is None:
            j += 1
        left = out[i - 1][1] if i > 0 else timed[0]["start"]
        right = out[j][0] if j < n else timed[-1]["end"]
        right = max(right, left)
        wts = [len(_norm(script_words[k])) + 2 for k in range(i, j)]
        tot, acc = sum(wts), 0
        for k in range(i, j):
            s0 = left + (right - left) * acc / tot
            acc += wts[k - i]
            out[k] = (s0, left + (right - left) * acc / tot)
        i = j
    return [{"word": w, "start": round(s, 3), "end": round(e, 3)} for w, (s, e) in zip(script_words, out)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default=V.get("voice", "Aria"))
    ap.add_argument("--text", help="override the text (default: all scene voice-over lines)")
    ap.add_argument("--dry-run", action="store_true", help="show the request, call nothing")
    ap.add_argument("--force", action="store_true", help="overwrite an existing S2-05-vo.wav")
    ap.add_argument("--timing-only", action="store_true", help="no fal.ai call, no key, no cost: redo word timings from the existing S2-05-vo.wav")
    a = ap.parse_args()

    text = a.text or " ".join(s["vo"] for s in DATA["scenes"])
    endpoint = V.get("endpoint", "fal-ai/elevenlabs/tts/eleven-v3")
    payload = {"text": text, "voice": a.voice, "stability": V.get("stability", 0.5), "timestamps": True,
               "apply_text_normalization": "auto", "output_format": V.get("output_format", "mp3_44100_128")}
    if V.get("language_code"):
        payload["language_code"] = V["language_code"]

    print(f"🎙️ endpoint {endpoint} · voice {a.voice} · {len(text)} characters")
    if a.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    wav = ROOT / "remotion/public/S2-05-vo.wav"
    if a.timing_only:
        if not wav.exists():
            sys.exit("no remotion/public/S2-05-vo.wav yet: generate it first")
        finish(wav, None, text, "Whisper")
        return
    if wav.exists() and not a.force:
        sys.exit(f"{wav.relative_to(ROOT)} exists (use --force to replace it)")
    key = get_key()
    if not key:
        sys.exit("No fal.ai key: set FAL_KEY for this command, or store it once in the Keychain "
                 "(service name 'fal-key').")

    res = run_fal(endpoint, payload, key)
    url = res["audio"]["url"]
    mp3 = ROOT / "remotion/public/S2-05-vo.mp3"
    mp3.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, mp3)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(wav)], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                               capture_output=True, text=True).stdout.strip() or 0)

    finish(wav, res.get("timestamps"), text, "endpoint timestamps")


def finish(wav, ts, text, label):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                               capture_output=True, text=True).stdout.strip() or 0)
    raw = parse_timestamps(ts)
    src = label
    if not raw:
        if ts is not None:
            print("⚠️ timestamps in an unknown shape, running Whisper instead…")
        raw = whisper_words(wav)
        src = "Whisper"
    words = align(text.split(), raw)
    (ROOT / "assets/words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))
    print(f"✅ {wav.relative_to(ROOT)} · {dur:.1f} s · {len(words)} script words timed from {src} ({len(raw)} recognised) → assets/words.json")
    if dur > DATA["length_s"] + 0.5:
        print(f"⚠️ voice is {dur:.1f} s but the short is {DATA['length_s']} s: tighten the script (S2-01) or speed up.")
    # the voice drives the cuts: each scene starts when its first word is spoken
    idx, starts = 0, []
    for s in DATA["scenes"]:
        starts.append(0.0 if idx == 0 else words[min(idx, len(words) - 1)]["start"])
        idx += len(s["vo"].split())
    ends = starts[1:] + [round(words[-1]["end"] + 0.3, 2)]
    rows = [{"clip": s["clips"][0], "start": round(a, 2), "end": round(b, 2), "dur": round(b - a, 2)}
            for s, a, b in zip(DATA["scenes"], starts, ends)]
    timing = {"length_s": int(-(-ends[-1] // 1)), "scenes": rows}
    (ROOT / "assets/scene_timing.json").write_text(json.dumps(timing, indent=1))
    print("   scene timing from the voice → assets/scene_timing.json (Remotion cuts follow it):")
    for r in rows:
        flag = "  ⚠️ longer than a Flow clip (max ~8 s): speed it up or make a second clip" if r["dur"] > 8.2 else ""
        print(f"   clip {r['clip']}: {r['start']:.1f}–{r['end']:.1f} s ({r['dur']:.1f} s){flag}")


if __name__ == "__main__":
    main()
