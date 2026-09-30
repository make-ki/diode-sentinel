import React from 'react';
import {AbsoluteFill,useCurrentFrame,interpolate} from 'remotion';
import {film} from '../config';
import {theme as t} from '../theme';
import {Eyebrow,Headline,Reveal} from '../ui';
export const Positioning=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{justifyContent:'center',padding:110,background:t.bg}}><Eyebrow>{film.positioning[0]}</Eyebrow><Headline lines={film.positioning.slice(1)} size={155}/><Reveal delay={24} style={{fontSize:33,color:t.muted,marginTop:35}}>{film.brand}</Reveal><div style={{position:'absolute',width:3,height:600,background:`linear-gradient(transparent,${t.accent},transparent)`,right:180,top:240,boxShadow:`0 0 50px ${t.accent}66`,transform:`translateY(${interpolate(f,[0,120],[25,-25])}px)`}}/></AbsoluteFill>};
