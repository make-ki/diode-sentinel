import React from 'react';
import {AbsoluteFill} from 'remotion';import {film} from '../config';import {theme as t} from '../theme';
import {Eyebrow,Headline,SourceList,Split,Footer} from '../ui';
export const Honesty=()=><AbsoluteFill style={{background:t.bg}}><Split left={<><Eyebrow>{film.honesty.eyebrow}</Eyebrow><Headline lines={film.honesty.headline}/></>} right={<SourceList rows={film.honesty.rows}/>}/><Footer><div style={{color:t.amber}}>{film.honesty.qualifier}</div>{film.honesty.remedy}</Footer></AbsoluteFill>;
