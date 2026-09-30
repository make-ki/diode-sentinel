import React from 'react';
import {AbsoluteFill} from 'remotion';
import {film} from '../config';import {theme as t} from '../theme';
import {Eyebrow,Headline,Panel,StatCard,Split,Footer} from '../ui';
export const CNN=()=><AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.cnn.eyebrow}</Eyebrow><Headline lines={film.cnn.headline}/></>} right={<Panel>{film.cnn.stats.map((s,i)=><StatCard key={s.label} {...s} delay={i*8}/>)}</Panel>}/><Footer>{film.cnn.qualifier}</Footer></AbsoluteFill>;
