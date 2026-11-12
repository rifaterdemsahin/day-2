import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile} from 'remotion';
import short from './short.json';
import avail from '../public/available.json';

const FPS = 30;
type Scene = (typeof short.scenes)[number];

// deterministic star field so placeholders look the same every render
const stars = Array.from({length: 70}, (_, i) => {
  const r = (n: number) => ((Math.sin(i * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  return {x: r(1) * 100, y: r(2) * 100, s: 2 + r(3) * 5, o: 0.2 + r(4) * 0.6};
});

const Placeholder: React.FC<{s: Scene}> = ({s}) => (
  <AbsoluteFill style={{background: 'linear-gradient(160deg,#050816,#1a1250 60%,#2b0f4a)'}}>
    {stars.map((st, i) => (
      <div key={i} style={{position: 'absolute', left: `${st.x}%`, top: `${st.y}%`, width: st.s, height: st.s, borderRadius: '50%', background: '#fff', opacity: st.o}} />
    ))}
    <div style={{position: 'absolute', left: 80, right: 80, top: 760, color: '#97a3d6', fontFamily: 'system-ui', fontSize: 44, lineHeight: 1.4, textAlign: 'center'}}>
      🎞️ Clip {s.clips[0]} not generated yet
      <br />
      <span style={{fontSize: 38}}>{s.visual}</span>
    </div>
  </AbsoluteFill>
);

const SceneView: React.FC<{s: Scene}> = ({s}) => {
  const c = s.clips[0];
  const file = `S2-04-${c}.mp4`;
  const have = (avail.clips as string[]).includes(file);
  return (
    <AbsoluteFill>
      {have ? (
        <OffthreadVideo src={staticFile(`clips/${file}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      ) : (
        <Placeholder s={s} />
      )}
      {/* big label: upper third, clear of platform buttons */}
      <div style={{position: 'absolute', left: 60, right: 60, top: 300, textAlign: 'center', color: '#fff', fontFamily: 'system-ui', fontWeight: 900, fontSize: 112, textShadow: '0 0 30px #4dd8ff'}}>
        {s.text}
      </div>
      {/* caption: safe area (bottom 20% and right 15% stay free) */}
      <div style={{position: 'absolute', left: 60, right: 170, bottom: 400, textAlign: 'center'}}>
        <span style={{display: 'inline-block', background: '#000a', color: '#fff', fontFamily: 'system-ui', fontWeight: 700, fontSize: 58, lineHeight: 1.3, padding: '14px 26px', borderRadius: 24}}>
          {s.vo}
        </span>
      </div>
    </AbsoluteFill>
  );
};

export const Short: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    {short.scenes.map((s) => (
      <Sequence key={s.clips[0]} from={s.start * FPS} durationInFrames={(s.end - s.start) * FPS}>
        <SceneView s={s} />
      </Sequence>
    ))}
    {avail.vo ? <Audio src={staticFile(avail.vo)} /> : null}
  </AbsoluteFill>
);
