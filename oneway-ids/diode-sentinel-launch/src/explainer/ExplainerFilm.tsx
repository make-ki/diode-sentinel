import React from 'react';
import {AbsoluteFill, Audio, Easing, Freeze, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {theme as t} from '../theme';
import {explainer as film} from './data.generated';
import {DiodeMark, DNSGraphic, EncryptedGraphic, PipelineGraphic, RhythmGraphic, RollingGraphic, SourceHistoryGraphic} from './Graphics';

type Scene = typeof film.scenes[number];
type ClipInfo = {recordedSeconds: number; focus?: {x:number;y:number;width:number;height:number}; file?: string};
const clips = (film.capture as unknown as {clips: Record<string, ClipInfo>}).clips;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Reveal: React.FC<{children: React.ReactNode; delay?: number; style?: React.CSSProperties}> = ({children, delay=0, style}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame-delay, fps, config: {damping: 36, stiffness: 72, mass: 1.2}});
  return <div style={{...style, opacity:p, transform:`translateY(${(1-p)*18}px)`, filter:`blur(${(1-p)*5}px)`}}>{children}</div>;
};

const Graphic: React.FC<{kind:string}> = ({kind}) => {
  if (kind==='rhythm') return <RhythmGraphic/>;
  if (kind==='rolling') return <RollingGraphic/>;
  if (kind==='history') return <SourceHistoryGraphic/>;
  if (kind==='dns') return <DNSGraphic/>;
  if (kind==='encrypted') return <EncryptedGraphic/>;
  return <PipelineGraphic stage={kind as 'receive'|'organize'|'models'|'fusion'|'handoff'}/>;
};

const profiles: Record<string,{zoom:number;start:[number,number];end:[number,number];positions?:[number,number,number][]}> = {
  overview: {zoom:1.25,start:[900,280],end:[920,405]},
  beacon: {zoom:1.86,start:[800,335],end:[800,365]},
  'rolling-scan': {zoom:1.72,start:[800,335],end:[800,375]},
  'source-context': {zoom:1.76,start:[800,330],end:[800,790],positions:[[0,800,330],[8,800,350],[16,800,390],[22,800,770],[26,800,790]]},
  dns: {zoom:1.78,start:[800,330],end:[800,380]},
  'encrypted-metadata': {zoom:1.82,start:[800,345],end:[800,565],positions:[[0,800,345],[10,800,370],[16,800,420],[23,800,565],[32,800,565]]},
  'scan-model': {zoom:1.8,start:[800,340],end:[800,420]},
  'source-correlation': {zoom:1.6,start:[1130,310],end:[800,460],positions:[[0,1130,310],[5,1120,310],[10,950,330],[15,800,370],[19,800,425],[23,800,460]]},
  'evidence-export': {zoom:1.64,start:[800,330],end:[800,800],positions:[[0,800,330],[8,800,350],[14,800,620],[19,800,790],[23,800,810],[28,800,800]]},
};

const DashboardClip: React.FC<{name:string;duration:number;width:number;height:number}> = ({name,duration,width,height}) => {
  const frame = useCurrentFrame();
  const profile = profiles[name] ?? profiles.beacon;
  const p = interpolate(frame,[80,Math.max(81,duration-45)],[0,1],{...clamp,easing:Easing.bezier(.25,.1,.25,1)});
  const center = profile.positions
    ? [1,2].map(i=>interpolate(frame/30,profile.positions!.map(key=>key[0]),profile.positions!.map(key=>key[i]),{...clamp,easing:Easing.bezier(.25,.1,.25,1)}))
    : profile.start.map((n,i)=>interpolate(p,[0,1],[n,profile.end[i]]));
  const zoom = profile.zoom + p*.035;
  const x = Math.max(width-1600*zoom,Math.min(0,width/2-center[0]*zoom));
  const y = Math.max(height-1000*zoom,Math.min(0,height/2-center[1]*zoom));
  const recorded = clips[name]?.recordedSeconds ?? duration/30;
  const clipFrames = Math.max(1,Math.floor(recorded*30)-1);
  const video = <OffthreadVideo src={staticFile(`explainer-captures/${name}.mp4`)} muted playbackRate={1}
    style={{position:'absolute',width:1600,height:1000,left:0,top:0,transformOrigin:'0 0',transform:`translate(${x}px,${y}px) scale(${zoom})`}}/>;
  return <div style={{position:'relative',width,height,overflow:'hidden',background:'#000'}}>
    {frame<clipFrames ? video : <Freeze frame={clipFrames}>{video}</Freeze>}
    <div style={{position:'absolute',inset:0,pointerEvents:'none',boxShadow:'inset 0 0 55px #0003'}}/>
  </div>;
};

const SceneView: React.FC<{scene:Scene}> = ({scene}) => {
  const f = useCurrentFrame();
  const length = scene.end-scene.start;
  const hasUI = Boolean(scene.clip && scene.clipAvailable);
  const showUI = hasUI && f>=scene.uiReveal;
  const longTitle = scene.title.length>36 || scene.id==='models';
  const panelTop = longTitle ? 350 : 260;
  const panelHeight = longTitle ? 635 : 725;
  const entry = spring({frame:f-scene.graphicReveal,fps:30,config:{damping:36,stiffness:70,mass:1.2}});
  const camera = interpolate(f,[0,length],[0,1],clamp);
  if(scene.id==='closing') return <AbsoluteFill style={{background:'#000',fontFamily:t.font,color:t.text,alignItems:'center',justifyContent:'center'}}>
    <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 50% 45%,#ff8a1f0c,transparent 55%)'}}/>
    <Reveal delay={12}><DiodeMark size={118}/></Reveal>
    <Reveal delay={24} style={{fontSize:148,fontWeight:600,letterSpacing:-7,marginTop:30}}>Diode Sentinel</Reveal>
    <Reveal delay={48} style={{fontSize:58,letterSpacing:-1.8,color:'#c8c8cc',marginTop:18}}>See everything. Touch nothing.</Reveal>
    <Reveal delay={95} style={{fontSize:26,fontFamily:t.mono,color:t.accent,marginTop:72}}>Built by samarags</Reveal>
  </AbsoluteFill>;
  return <AbsoluteFill style={{background:'#000',color:t.text,fontFamily:t.font}}>
    <AbsoluteFill style={{background:`radial-gradient(ellipse at ${45+camera*8}% 50%,#ff8a1f06,transparent 65%)`}}/>
    <div style={{position:'absolute',top:44,left:96,right:96,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
      <Reveal style={{fontSize:20,fontFamily:t.mono,color:t.accent,letterSpacing:1.2}}>{scene.label}</Reveal>
      <div style={{display:'flex',gap:12,alignItems:'center',fontSize:22,color:'#b5b5bd'}}><DiodeMark size={32}/>Diode Sentinel</div>
    </div>
    <Reveal delay={12} style={{position:'absolute',top:103,left:96,right:96,fontSize:longTitle?105:116,fontWeight:600,letterSpacing:-4.8,lineHeight:1.06}}>{scene.title}</Reveal>
    <div style={{position:'absolute',left:96,top:panelTop,width:1728,height:panelHeight,border:'1px solid #303036',borderRadius:22,overflow:'hidden',boxShadow:'0 24px 80px #000b,0 0 90px #ff8a1f05',opacity:entry,transform:`perspective(2400px) translateY(${(1-entry)*22}px) rotateX(${(1-entry)*1.1}deg)`}}>
      <Sequence from={scene.graphicReveal} durationInFrames={hasUI?scene.uiReveal-scene.graphicReveal+22:undefined} layout="none">
        <div style={{position:'absolute',inset:0,opacity:hasUI?interpolate(f,[scene.uiReveal,scene.uiReveal+22],[1,0],clamp):1}}>
          <Freeze frame={Math.max(0,Math.floor((f-scene.graphicReveal)*.55))}><Graphic kind={scene.graphic}/></Freeze>
        </div>
      </Sequence>
      {hasUI && <Sequence from={scene.uiReveal} layout="none"><div style={{position:'absolute',inset:0,opacity:interpolate(f,[scene.uiReveal,scene.uiReveal+22],[0,1],clamp)}}><DashboardClip name={scene.clip!} duration={length-scene.uiReveal} width={1728} height={panelHeight}/></div></Sequence>}
      <div style={{position:'absolute',top:0,left:60,right:60,height:1,background:'linear-gradient(90deg,transparent,#ffe1bf55,transparent)',pointerEvents:'none'}}/>
    </div>
    <div style={{position:'absolute',bottom:32,left:100,right:100,display:'flex',justifyContent:'space-between',fontSize:21,fontFamily:t.mono,color:'#a5a5ae'}}>
      <span>{showUI?'Recorded software · Synthetic replay':'Illustrative diagram · Receive-side observations'}</span>
      <span>samarags</span>
    </div>
    <div style={{position:'absolute',bottom:0,left:0,height:2,width:`${Math.min(1,f/length)*100}%`,background:'linear-gradient(90deg,#ff8a1f99,#ff8a1f22)'}}/>
  </AbsoluteFill>;
};

const Music = () => film.music ? <Audio src={staticFile(film.music)} volume={frame=>{
  const fadeIn=Math.min(1,frame/30),fadeOut=Math.min(1,(film.duration-frame)/60);
  let duck=1;
  for(const voice of film.narration){
    const begin=voice.startFrame,end=begin+voice.durationFrames;
    duck=Math.min(duck,interpolate(frame,[begin-16,begin,end,end+24],[1,.48,.48,1],clamp));
  }
  return .82*Math.max(0,Math.min(fadeIn,fadeOut))*duck;
}}/> : null;

export const ExplainerFilm = () => <AbsoluteFill style={{background:'#000'}}>
  <TransitionSeries>{film.scenes.map((scene,i)=><React.Fragment key={scene.id}>
    {i>0&&<TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:24})}/>}
    <TransitionSeries.Sequence durationInFrames={scene.end-scene.start+(i<film.scenes.length-1?24:0)}><SceneView scene={scene}/></TransitionSeries.Sequence>
  </React.Fragment>)}</TransitionSeries>
  <Music/>
  {film.narration.map(voice=><Sequence key={voice.id} from={voice.startFrame} durationInFrames={voice.durationFrames}><Audio src={staticFile(voice.file)} volume={1}/></Sequence>)}
</AbsoluteFill>;
