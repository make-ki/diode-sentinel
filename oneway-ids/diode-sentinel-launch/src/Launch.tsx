import React from 'react';
import {AbsoluteFill,Audio,staticFile,interpolate} from 'remotion';
import {TransitionSeries,linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {theme as t} from './theme';import {cuts,film} from './config';import {assets} from './assets.generated';
import {Constraint} from './scenes/Constraint';import {Positioning} from './scenes/Positioning';import {Contract} from './scenes/Contract';import {Substitution} from './scenes/Substitution';import {Clock} from './scenes/Clock';import {CNN} from './scenes/CNN';import {Replay} from './scenes/Replay';import {Models} from './scenes/Models';import {Honesty} from './scenes/Honesty';import {Messy} from './scenes/Messy';import {Closing} from './scenes/Closing';
const scenes=[Constraint,Positioning,Contract,Substitution,Clock,CNN,Replay,Models,Honesty,Messy,Closing];
export const Launch=()=><AbsoluteFill style={{background:t.bg,fontFamily:t.font,color:t.text}}><TransitionSeries>{cuts.map((cut,i)=>{const Scene=scenes[i];return <React.Fragment key={cut.id}>{i>0&&<TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:12})}/>}<TransitionSeries.Sequence durationInFrames={cut.end-cut.start+(i<cuts.length-1?12:0)}><Scene/></TransitionSeries.Sequence></React.Fragment>})}</TransitionSeries>{assets.music&&<Audio src={staticFile('music.mp3')} volume={f=>Math.min(interpolate(f,[0,30],[0,1],{extrapolateRight:'clamp'}),interpolate(f,[film.duration-60,film.duration],[1,0],{extrapolateLeft:'clamp'}))}/>}</AbsoluteFill>;
