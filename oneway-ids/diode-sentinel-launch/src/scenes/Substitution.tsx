import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {film} from '../config';
import {theme as t} from '../theme';
import {Eyebrow,Headline,Panel,AlertRow,Split,Footer} from '../ui';
export const Substitution=()=>{const f=useCurrentFrame();const i=f<95?0:1;const row=film.substitution.rows[i];return <AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.substitution.eyebrow}</Eyebrow><Headline lines={film.substitution.headline}/></>} right={<Panel key={i}><AlertRow {...row}/><div style={{width:64,height:2,background:t.accent,marginTop:28}}/></Panel>}/><Footer>{film.substitution.footer}</Footer></AbsoluteFill>};
