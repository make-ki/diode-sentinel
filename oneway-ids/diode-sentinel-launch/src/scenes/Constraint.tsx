import React from 'react';
import {AbsoluteFill,useCurrentFrame,interpolate} from 'remotion';
import {film} from '../config';
import {theme as t} from '../theme';
import {DiodeDiagram} from '../ui/DiodeDiagram';
import {Headline,Reveal} from '../ui';
export const Constraint=()=>{const f=useCurrentFrame();const index=Math.min(2,Math.floor(Math.max(0,f-10)/45));const local=Math.max(0,f-10-index*45);const opacity=interpolate(local,[0,10,35,45],[0,1,1,0],{extrapolateRight:'clamp'});return <AbsoluteFill style={{alignItems:'center',background:t.bg}}><div style={{position:'absolute',top:180,opacity,fontSize:146,fontWeight:600,letterSpacing:-7}}>{film.hook[index]}</div><div style={{position:'absolute',top:530}}><DiodeDiagram/></div><Reveal delay={120} style={{position:'absolute',bottom:145,fontSize:36,color:t.muted}}>{film.direction}</Reveal></AbsoluteFill>};
