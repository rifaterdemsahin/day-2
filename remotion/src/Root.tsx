import React from 'react';
import {Composition} from 'remotion';
import short from './short.json';
import {Short} from './Short';

export const FPS = 30;

export const Root: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    durationInFrames={short.length_s * FPS}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
