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
import argparse, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error

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
    subprocess.run(["whisper", str(audio), "--model", "small", "--language", "en", "--word_timestamps", "True",
                    "--output_format", "json", "--output_dir", str(tmp)], check=True)
    j = json.loads((tmp / (audio.stem + ".json")).read_text())
    words = [{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
             for seg in j["segments"] for w in seg.get("words", [])]
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default=V.get("voice", "Aria"))
    ap.add_argument("--text", help="override the text (default: all scene voice-over lines)")
    ap.add_argument("--dry-run", action="store_true", help="show the request, call nothing")
    ap.add_argument("--force", action="store_true", help="overwrite an existing S2-05-vo.wav")
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

    words = parse_timestamps(res.get("timestamps"))
    src = "endpoint timestamps"
    if not words:
        print("⚠️ timestamps missing or in an unknown shape, running Whisper instead…")
        words = whisper_words(wav)
        src = "Whisper"
    (ROOT / "assets/words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))
    print(f"✅ {wav.relative_to(ROOT)} · {dur:.1f} s · {len(words)} timed words ({src}) → assets/words.json")
    if dur > DATA["length_s"] + 0.5:
        print(f"⚠️ voice is {dur:.1f} s but the short is {DATA['length_s']} s: tighten the script (S2-01) or speed up.")
    for s in DATA["scenes"]:
        first = next((w for w in words if w["start"] >= s["start"] - 1.5), None)
        if first:
            print(f"   clip {s['clips'][0]}: scene starts {s['start']} s, first word at {first['start']:.1f} s ({first['word']})")


if __name__ == "__main__":
    main()
