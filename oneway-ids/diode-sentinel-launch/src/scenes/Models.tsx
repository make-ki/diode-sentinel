import React from 'react';
import {AbsoluteFill} from 'remotion';import {film} from '../config';import {theme as t} from '../theme';
import {Eyebrow,Headline,Panel,AlertRow,Split} from '../ui';
export const Models=()=><AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.models.eyebrow}</Eyebrow><Headline lines={film.models.headline}/></>} right={<Panel>{film.models.rows.map((s,i)=><AlertRow key={s.name} label={s.name} signal={s.signal} detail={s.detail} delay={i*12}/>)}</Panel>}/></AbsoluteFill>;
