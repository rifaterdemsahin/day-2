import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import short from './short.json';
import avail from '../public/available.json';

type Scene = (typeof short.scenes)[number];
type W = {text: string; from: number; to: number}; // frames, local to the scene
const C = short.captions;

// Real word timings (Whisper, assets/words.json) when present; otherwise spread the
// script words over the scene by length, with a short lead-in and tail.
const wordsFor = (s: Scene, fps: number): W[] => {
  const dur = (s.end - s.start) * fps;
  const real = (avail.words as {word: string; start: number; end: number}[]).filter((w) => w.start >= s.start && w.start < s.end);
  if (real.length) {
    return real.map((w) => ({text: String(w.word).trim(), from: Math.round((w.start - s.start) * fps), to: Math.round((w.end - s.start) * fps)}));
  }
  const toks = s.vo.split(/\s+/).filter(Boolean);
  const lead = Math.round(C.lead_s * fps);
  const room = dur - lead - Math.round(C.tail_s * fps);
  const wts = toks.map((t) => t.replace(/[^\p{L}\p{N}]/gu, '').length + 2);
  const tot = wts.reduce((a, b) => a + b, 0);
  let acc = 0;
  return toks.map((t, i) => {
    const from = lead + Math.round((room * acc) / tot);
    acc += wts[i];
    return {text: t, from, to: lead + Math.round((room * acc) / tot)};
  });
};

// pages of a few words; a page also ends after . ? ! ,
const pagesOf = (ws: W[]): W[][] => {
  const pages: W[][] = [];
  let cur: W[] = [];
  ws.forEach((w) => {
    cur.push(w);
    if (cur.length >= C.words_per_page || /[.?!,]$/.test(w.text)) {
      pages.push(cur);
      cur = [];
    }
  });
  if (cur.length) pages.push(cur);
  return pages;
};

export const AnimatedCaptions: React.FC<{s: Scene}> = ({s}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pages = pagesOf(wordsFor(s, fps));
  const idx = pages.reduce((a, p, i) => (frame >= p[0].from ? i : a), -1);
  if (idx < 0) return null;
  const page = pages[idx];
  return (
    <div style={{position: 'absolute', left: 60, right: 170, bottom: 400, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', }}>
      {page.map((w, i) => {
        if (frame < w.from) return null;
        const pop = spring({frame: frame - w.from, fps, durationInFrames: C.pop_frames, config: {damping: 11, stiffness: 220}});
        const active = frame >= w.from && frame < Math.max(w.to, w.from + 1) && (i === page.length - 1 || frame < page[i + 1].from);
        const scale = interpolate(pop, [0, 1], [0.55, active ? 1.14 : 1]);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              margin: '4px 16px',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontWeight: 900,
              fontSize: C.font_size,
              textTransform: 'uppercase',
              color: active ? C.active_color : C.text_color,
              WebkitTextStroke: `10px ${C.stroke}`,
              paintOrder: 'stroke fill',
              textShadow: active ? `0 0 32px ${C.active_color}` : 'none',
              transform: `translateY(${interpolate(pop, [0, 1], [24, 0])}px) scale(${scale})`,
              opacity: interpolate(pop, [0, 0.5], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
