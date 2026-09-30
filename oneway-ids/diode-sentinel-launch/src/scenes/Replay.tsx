import React from 'react';
import {AbsoluteFill} from 'remotion';import {film} from '../config';import {theme as t} from '../theme';
import {Eyebrow,Headline,Panel,StatCard,Split,Footer} from '../ui';
export const Replay=()=><AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.replay.eyebrow}</Eyebrow><Headline lines={film.replay.headline}/></>} right={<Panel>{film.replay.stats.map((s,i)=><StatCard key={s.label} {...s} delay={i*8}/>)}</Panel>}/><Footer>{film.replay.qualifier}</Footer></AbsoluteFill>;
