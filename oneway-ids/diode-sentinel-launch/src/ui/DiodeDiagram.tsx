import React from 'react';
import {useCurrentFrame} from 'remotion';
import {theme as t} from '../theme';
import {film} from '../config';
export const DiodeDiagram:React.FC=()=>{const f=useCurrentFrame();return <div style={{position:'relative',width:1500,height:290}}>
<svg width="1500" height="290" viewBox="0 0 1500 290">
<defs><linearGradient id="pipe"><stop stopColor="#ff8a1f" stopOpacity="0"/><stop offset=".5" stopColor="#ff8a1f"/><stop offset="1" stopColor="#ff8a1f" stopOpacity=".2"/></linearGradient></defs>
<path d="M80 110 H1400" stroke="url(#pipe)" strokeWidth="2"/>
<path d="M1400 102 L1415 110 L1400 118" fill="none" stroke={t.accent} strokeWidth="2"/>
<ellipse cx="740" cy="110" rx={95+Math.sin(f/18)*5} ry={92+Math.sin(f/18)*5} fill="none" stroke={t.accent} opacity=".15" strokeWidth="1.5"/>
<path d="M695 55 L780 110 L695 165 Z" fill="#111" stroke={t.accent} strokeWidth="3"/>
<path d="M785 55 V165" stroke={t.accent} strokeWidth="4"/>
{Array.from({length:8},(_,i)=>{const x=90+((f*6+i*173)%1290);return <rect key={i} x={x} y={104} width={20} height={12} rx={3} fill={t.accent} opacity={.3+i*.08}/>})}
<path d="M1180 220 H865" stroke="#666670" strokeWidth="2" strokeDasharray="8 12"/>
<path d="M865 212 L850 220 L865 228" fill="none" stroke="#666670" strokeWidth="2"/>
<rect x="790" y="184" width="18" height="74" rx="2" fill={t.border}/>
<path d="M940 196 L988 244 M988 196 L940 244" stroke={t.critical} strokeWidth="3"/>
</svg>
<div style={{position:'absolute',top:155,left:60,fontFamily:t.mono,fontSize:22,color:t.muted}}>{film.diagram.source}</div>
<div style={{position:'absolute',top:8,left:545,fontFamily:t.mono,fontSize:23,color:t.accent}}>{film.diagram.diode}</div>
<div style={{position:'absolute',top:155,right:10,fontFamily:t.mono,fontSize:22,color:t.muted}}>{film.diagram.sensor}</div>
<div style={{position:'absolute',top:257,left:890,fontFamily:t.mono,fontSize:22,color:t.muted}}>{film.diagram.return}</div>
</div>};
