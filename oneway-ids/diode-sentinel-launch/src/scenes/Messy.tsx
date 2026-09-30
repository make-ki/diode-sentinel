import React from 'react';
import {AbsoluteFill} from 'remotion';import {film} from '../config';import {theme as t} from '../theme';
import {Eyebrow,Headline,Panel,SeverityBadge,AlertRow,Split,Footer} from '../ui';
export const Messy=()=><AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.messy.eyebrow}</Eyebrow><Headline lines={film.messy.headline}/></>} right={<Panel><SeverityBadge label={film.messy.badge} critical/><AlertRow label={film.messy.signal} signal={film.messy.detail} detail={film.messy.remedy} critical delay={7}/><div style={{fontSize:26,color:t.amber,lineHeight:1.4,marginTop:25}}>{film.messy.outcome}</div></Panel>}/></AbsoluteFill>;
