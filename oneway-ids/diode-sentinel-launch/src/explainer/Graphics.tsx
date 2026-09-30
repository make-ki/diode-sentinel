import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type Stage = 'receive' | 'organize' | 'models' | 'fusion' | 'handoff';
type Props = {stage: Stage};
const W = 1100;
const H = 650;
const amber = theme.accent;
const pale = '#f3f0eb';
const dim = '#888891';
const panel = '#101014';

function useMotion(delay = 0) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: Math.max(0, frame - delay), fps, config: theme.spring});
}

function Svg({children, title}: {children: React.ReactNode; title: string}) {
  return <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title}
    style={{width: '100%', height: '100%', display: 'block', overflow: 'visible'}}>
    <defs>
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#29292f"/><stop offset=".5" stopColor="#141418"/><stop offset="1" stopColor="#09090c"/></linearGradient>
      <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop stopColor={amber} stopOpacity=".05"/><stop offset=".5" stopColor={amber} stopOpacity=".8"/><stop offset="1" stopColor={amber} stopOpacity=".05"/></linearGradient>
      <radialGradient id="halo"><stop stopColor={amber} stopOpacity=".16"/><stop offset="1" stopColor={amber} stopOpacity="0"/></radialGradient>
      <pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#fff" strokeOpacity=".025" strokeWidth="1"/></pattern>
      <filter id="softGlow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <rect width={W} height={H} fill="#060608" rx="22"/>
    <rect width={W} height={H} fill="url(#grid)" rx="22"/>
    <ellipse cx="550" cy="322" rx="460" ry="260" fill="url(#halo)"/>
    {children}
  </svg>;
}

function Label({x, y, children, size = 27, color = pale, weight = 500, mono = false, anchor = 'start'}: {
  x: number; y: number; children: React.ReactNode; size?: number; color?: string; weight?: number; mono?: boolean; anchor?: 'start' | 'middle' | 'end';
}) {
  return <text x={x} y={y} textAnchor={anchor} fill={color} fontFamily={mono ? theme.mono : theme.font} fontSize={size} fontWeight={weight}>{children}</text>;
}

function Node({x, y, w, h, title, sub, delay = 0, accent = false}: {x:number;y:number;w:number;h:number;title:string;sub?:string;delay?:number;accent?:boolean}) {
  const p = useMotion(delay);
  return <g opacity={p} transform={`translate(0 ${18 * (1 - p)})`}>
    <rect x={x} y={y} width={w} height={h} rx="16" fill={panel} stroke={accent ? amber : '#323238'} strokeWidth={accent ? 2 : 1.4}/>
    {accent && <rect x={x+1} y={y+1} width={w-2} height="4" rx="2" fill={amber} opacity=".85"/>}
    <Label x={x+22} y={y+43} size={Math.min(28,(w-44)/(title.length*.56))} weight={600} color={accent ? '#ffe0b6' : pale}>{title}</Label>
    {sub && <Label x={x+22} y={y+74} size={Math.min(19,(w-44)/(sub.length*.52))} color={dim}>{sub}</Label>}
  </g>;
}

function ModelRow({x, y, title, sub, delay = 0, accent = false}: {x:number;y:number;title:string;sub:string;delay?:number;accent?:boolean}) {
  const p = useMotion(delay);
  return <g opacity={p} transform={`translate(0 ${14 * (1 - p)})`}>
    <rect x={x} y={y} width="370" height="54" rx="12" fill={panel} stroke={accent ? '#74532f' : '#323238'} strokeWidth="1.4"/>
    <Label x={x+16} y={y+23} size={20} weight={600} color={accent ? '#ffe0b6' : pale}>{title}</Label>
    <Label x={x+16} y={y+43} size={15} color={dim}>{sub}</Label>
  </g>;
}

function Flow({d, delay = 0, dashed = false}: {d: string; delay?: number; dashed?: boolean}) {
  const p = useMotion(delay);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const period = Math.max(1, Math.round(fps * 3.8));
  const dashOffset = -((Math.max(0, frame - delay) % period) / period) * 1000;
  return <g opacity={p}>
    <path d={d} fill="none" stroke={dashed ? '#77777e' : 'url(#glow)'} strokeWidth="3" strokeDasharray={dashed ? '8 10' : undefined}/>
    {!dashed && <path d={d} pathLength="1000" fill="none" stroke={amber} strokeWidth="5" strokeLinecap="round" strokeDasharray="24 976" strokeDashoffset={dashOffset} opacity=".9" filter="url(#softGlow)"/>}
  </g>;
}

export const DiodeMark = ({size}: {size: number}) => <svg width={size} height={size} viewBox="0 0 100 100" aria-label="one-way diode mark">
  <path d="M15 18h70v64H15z" fill="#101014" stroke="#4a4a50" strokeWidth="3"/>
  <path d="M24 50h38" stroke={amber} strokeWidth="6" strokeLinecap="round"/><path d="m55 36 18 14-18 14z" fill={amber}/>
  <path d="M80 31v38" stroke="#55555b" strokeWidth="4" strokeLinecap="round"/>
</svg>;

export const PipelineGraphic = ({stage}: Props) => {
  const tag = (text: string) => <g><rect x="64" y="42" width="218" height="38" rx="19" fill="#19191e" stroke="#35353a"/><Label x={173} y={68} size={16} color={amber} mono anchor="middle">{text.toUpperCase()}</Label></g>;
  const title = (text: string) => <Label x={64} y={137} size={40} weight={600}>{text}</Label>;
  if (stage === 'receive') return <Svg title="One-way packet observation crosses the diode to the receive-side sensor">
    {tag('Receive side')}{title('One direction. A stream of observations.')}
    {[0,1,2].map((i)=><g key={i} opacity={useMotion(i*8)} transform={`translate(${80+i*5} ${220+i*66})`}>
      <rect width="342" height="48" rx="8" fill="#17171b" stroke="#3b3b42"/><rect x="0" y="0" width="9" height="48" rx="4" fill={amber} opacity={.8}/>
      <Label x={28} y={32} size={20} mono color="#d0cdd0">SRC  →  DST</Label><Label x={214} y={32} size={16} mono color={dim}>SIZE · TIME</Label>
    </g>)}
    <Flow d="M430 324 C490 324 500 324 555 324" delay={8}/>
    <g transform="translate(470 245)"><path d="M0 0h120v158H0z" fill="url(#metal)" stroke="#494950" strokeWidth="2"/><path d="M26 78h40" stroke={amber} strokeWidth="7" strokeLinecap="round"/><path d="m58 60 24 18-24 18z" fill={amber}/><path d="M94 45v66" stroke="#77777e" strokeWidth="5"/><Label x={60} y={194} size={16} color={dim} anchor="middle">ONE WAY</Label></g>
    <Flow d="M596 324 C655 324 652 324 710 324" delay={15}/>
    <Node x={710} y={253} w={300} h={144} title="Receive-side sensor" sub="Observe · organize · record" delay={12} accent/>
    <Label x={80} y={492} size={23} color={dim}>Source · destination · size · time</Label>
  </Svg>;
  if (stage === 'organize') return <Svg title="Packets become flows and time-window summaries, while DNS and ClientHello metadata branch to their consumers">
    {tag('Organize')}{title('One packet becomes useful in company.')}
    <Node x={66} y={266} w={230} h={108} title="Packets" sub="headers + time" delay={0}/>
    <Flow d="M296 320 C350 320 330 225 390 225" delay={5}/><Flow d="M296 320 C350 320 330 415 390 415" delay={5}/>
    <Node x={390} y={170} w={262} h={110} title="Flow summaries" sub="grouped observations" delay={6} accent/>
    <Node x={390} y={360} w={262} h={110} title="Timed windows" sub="clock closes the window" delay={10}/>
    <Flow d="M296 286 H326 V157 H735 V238 H760" delay={13}/><Flow d="M296 356 C390 545 650 545 760 455" delay={15}/>
    <Node x={760} y={185} w={270} h={106} title="DNS label" sub="when query is present" delay={15}/>
    <Node x={760} y={404} w={270} h={106} title="ClientHello" sub="when fully observed" delay={18}/>
    <Label x={760} y={338} size={20} color={amber}>Available metadata</Label>
    <Label x={66} y={552} size={21} color={dim}>Flows and windows form alongside packet-level observations.</Label>
  </Svg>;
  if (stage === 'models') return <Svg title="Different named models receive only their relevant observations through parallel branches">
    {tag('Parallel model inputs')}{title('Each signal has its own destination.')}
    <Node x={58} y={267} w={236} h={104} title="Observed data" sub="flow · window · label" delay={0}/>
    {[
      ['Character CNN','DNS query-label characters'],['Sequence CNN','packet-size and timing sequence'],['XGBoost · encrypted','ClientHello metadata + flow'],['XGBoost · exfil','transfer-window features'],['Random Forest','scan-window fan-out'],['LightGBM','flow-level corroboration'],['Isolation Forest','eligible corroboration only'],
    ].map(([a,b],i)=>{const y=151+i*59;return <React.Fragment key={a}><Flow d={`M294 319 C340 319 340 ${y+27} 405 ${y+27}`} delay={4+i*2}/><ModelRow x={405} y={y} title={a} sub={b} delay={7+i*2} accent={i<5}/></React.Fragment>})}
    <Node x={827} y={260} w={225} h={132} title="Signals" sub="qualified records" delay={20} accent/>
    {[178,237,296,355,414,473].map((y,i)=><Flow key={y} d={`M775 ${y} C800 ${y} 800 326 827 326`} delay={16+i}/>) }
    <Flow d="M775 532 C810 532 810 296 775 296" delay={23} dashed/>
    <Label x={58} y={612} size={18} color={dim}>Isolation Forest supports eligible models; each branch requires its own observed inputs.</Label>
  </Svg>;
  if (stage === 'fusion') return <Svg title="Recorded signals from a source can qualify for a separate recent-signal correlation">
    {tag('Correlate')}{title('Evidence first. Correlation follows.')}
    <Node x={68} y={184} w={300} h={90} title="Signal · same source" sub="recorded by a detector" delay={0}/>
    <Node x={68} y={301} w={300} h={90} title="Signal · same source" sub="another qualifying signal" delay={7}/>
    <Node x={68} y={418} w={300} h={90} title="Signal · same source" sub="within recent history" delay={14}/>
    <Flow d="M368 229 C440 229 440 319 516 319" delay={4}/><Flow d="M368 346 C440 346 440 319 516 319" delay={10}/><Flow d="M368 463 C440 463 440 319 516 319" delay={16}/>
    <g opacity={useMotion(18)}><circle cx="610" cy="319" r="105" fill="#111115" stroke="#5a4a36" strokeWidth="2"/><circle cx="610" cy="319" r="80" fill="none" stroke={amber} strokeOpacity=".35" strokeDasharray="3 10"/><Label x={610} y={309} size={25} weight={600} anchor="middle">Source</Label><Label x={610} y={344} size={20} color={dim} anchor="middle">correlation</Label></g>
    <Flow d="M715 319 C774 319 774 319 832 319" delay={22}/><Node x={832} y={253} w={216} h={132} title="Evidence" sub="with contributors" delay={24} accent/>
    <Label x={68} y={568} size={21} color={dim}>Recent qualifying signals · decay · escalation suppression</Label>
  </Svg>;
  return <Svg title="Analyst inspects a recorded alert and its evidence in the dashboard">
    {tag('Analyst handoff')}{title('The record stays inspectable.')}
    <g opacity={useMotion(2)}>
      <rect x="95" y="175" width="910" height="360" rx="18" fill="#0d0d11" stroke="#3a3a40" strokeWidth="2"/>
      <path d="M95 227h910" stroke="#29292e"/><circle cx="123" cy="201" r="6" fill={amber}/><circle cx="145" cy="201" r="6" fill="#4c4c52"/><circle cx="167" cy="201" r="6" fill="#4c4c52"/>
      <rect x="125" y="258" width="226" height="240" rx="12" fill="#141418" stroke="#29292e"/><Label x={151} y={294} size={18} color={dim}>SOURCE FILTER</Label><Label x={151} y={343} size={24} mono>selected source</Label><rect x="148" y="370" width="178" height="2" fill="#35353b"/><Label x={151} y={416} size={18} color={dim}>RECENT SIGNALS</Label><Label x={151} y={454} size={19}>Contributing signals</Label>
      <Label x={394} y={284} size={18} color={amber}>SELECTED ALERT</Label><Label x={394} y={330} size={31} weight={600}>Recorded evidence</Label><Label x={394} y={373} size={22} color={dim}>Named measurements · original record</Label>
      <rect x="394" y="409" width="548" height="54" rx="10" fill="#17171c" stroke="#38383f"/><Label x={420} y={444} size={19} mono color="#d5d2ce">event  →  evidence  →  analyst</Label>
      <rect x="394" y="478" width="205" height="36" rx="18" fill="#392817"/><Label x={496} y={502} size={16} color="#ffd39b" anchor="middle">Download evidence JSON</Label>
    </g>
    <Label x={95} y={590} size={20} color={dim}>Recorded fields and values come from the selected dashboard event.</Label>
  </Svg>;
};

export const RhythmGraphic = () => {
  const frame = useCurrentFrame();
  const markerX = interpolate(frame % 180, [0, 180], [170, 930]);
  const irregular = [0, .15, .41, .48, .80, .99, 1.23, 1.67, 1.79, 2.25, 2.39, 2.96];
  return <Svg title="Illustrative comparison of regularly and irregularly spaced packet arrivals">
    <Label x={65} y={104} size={40} weight={600}>Timing is part of the observation.</Label>
    <Label x={65} y={151} size={20} color={amber}>ILLUSTRATIVE FLOW-START PATTERNS</Label>
    <Label x={90} y={250} size={26} weight={600}>Regular starts</Label><Label x={90} y={447} size={26} weight={600}>Irregular starts</Label>
    <path d="M90 303H1010M90 500H1010" stroke="#4a4a50" strokeWidth="2"/>
    {[0,1,2,3,4,5,6,7,8,9,10,11].map(i=><g key={`r${i}`}><path d={`M${135+i*75} 291v24`} stroke={amber} strokeWidth="4"/><circle cx={135+i*75} cy="303" r="6" fill={amber}/></g>)}
    {irregular.map((n,i)=><g key={`i${i}`}><path d={`M${135+n*250} 488v24`} stroke="#f1b55c" strokeWidth="4"/><circle cx={135+n*250} cy="500" r="6" fill="#f1b55c"/></g>)}
    <path d={`M${markerX} 205V526`} stroke="#fff" strokeOpacity=".42" strokeWidth="1" strokeDasharray="4 7"/>
    <Label x={90} y={578} size={21} color={dim}>A beacon rule can compare observed start-time spacing and its variation.</Label>
  </Svg>;
};

export const RollingGraphic = () => {
  const frame = useCurrentFrame();
  const shown = Math.min(20, Math.floor(interpolate(frame, [0, 42], [0, 20], {extrapolateRight:'clamp'})));
  return <Svg title="Illustrative rolling scan: ten unique destination and port pairs in each of two adjacent ten-second windows within a sixty-second horizon">
    <Label x={64} y={98} size={39} weight={600}>The horizon keeps both windows in view.</Label>
    <Label x={64} y={141} size={20} color={amber}>ILLUSTRATIVE ROLLING CONTEXT · OPTIONAL RULE</Label>
    <rect x="65" y="192" width="970" height="330" rx="18" fill="#0c0c10" stroke="#37373e" strokeWidth="2"/>
    <Label x={98} y={234} size={22} color={dim}>60-second retained horizon</Label>
    <rect x="102" y="267" width="388" height="190" rx="14" fill="#151519" stroke="#50402d"/><rect x="510" y="267" width="490" height="190" rx="14" fill="#151519" stroke="#50402d"/>
    <Label x={296} y={305} size={24} weight={600} anchor="middle">Window 1 · 10 s</Label><Label x={755} y={305} size={24} weight={600} anchor="middle">Window 2 · next 10 s</Label>
    {Array.from({length:10},(_,i)=><g key={i} opacity={i<shown?1:.16}><rect x={125+(i%5)*66} y={329+Math.floor(i/5)*48} width="46" height="30" rx="6" fill={i<shown?amber:'#424249'} opacity={i<shown?.82:1}/><text x={148+(i%5)*66} y={351+Math.floor(i/5)*48} fill="#101014" fontFamily={theme.mono} fontSize="13" textAnchor="middle">D/P</text></g>)}
    {Array.from({length:10},(_,i)=><g key={`b${i}`} opacity={i+10<shown?1:.16}><rect x={535+(i%5)*86} y={329+Math.floor(i/5)*48} width="63" height="30" rx="6" fill={i+10<shown?'#ffbd68':'#424249'} opacity={i+10<shown?.82:1}/><text x={566+(i%5)*86} y={351+Math.floor(i/5)*48} fill="#101014" fontFamily={theme.mono} fontSize="13" textAnchor="middle">new</text></g>)}
    <Label x={102} y={493} size={21} color={dim}>10 distinct destination/port pairs</Label><Label x={510} y={493} size={21} color={dim}>10 different pairs · union = {shown}</Label>
    <Label x={65} y={578} size={20} color={dim}>The illustrated union reaches the existing 20-pair threshold across adjacent windows.</Label>
  </Svg>;
};

export const SourceHistoryGraphic = () => <Svg title="A destination known to source A may be new within source B's retained history">
  <Label x={64} y={102} size={39} weight={600}>Novelty depends on whose history.</Label>
  <Label x={64} y={146} size={20} color={amber}>ILLUSTRATIVE SOURCE-CONTEXT RULE · OPT-IN</Label>
  <Node x={86} y={225} w={348} h={232} title="Source A" sub="retained destination history" delay={0} accent/>
  <Node x={666} y={225} w={348} h={232} title="Source B" sub="its own retained history" delay={7}/>
  <g opacity={useMotion(10)}><rect x="144" y="337" width="230" height="62" rx="12" fill="#1c1813" stroke="#795528"/><Label x={259} y={377} size={27} mono anchor="middle">destination X</Label></g>
  <g opacity={useMotion(15)}><rect x="690" y="337" width="298" height="62" rx="12" fill="#121216" stroke="#55555c" strokeDasharray="5 6"/><Label x={839} y={377} size={22} mono anchor="middle">not in retained set</Label></g>
  <path d="M434 367H666" fill="none" stroke="#77777e" strokeWidth="2" strokeDasharray="5 8"/>
  <Label x={550} y={311} size={17} color={amber} anchor="middle">same destination</Label>
  <Label x={86} y={518} size={21} color={dim}>Known to A</Label><Label x={666} y={518} size={19} color={dim}>New within B's covered history</Label>
  <Label x={64} y={580} size={19} color={dim}>Retained lookback and coverage qualify the novelty signal.</Label>
</Svg>;

export const DNSGraphic = () => {
  const frame = useCurrentFrame();
  const offset = (Math.floor(frame/16)%9);
  const chars = ['d','o','m','a','i','n','l','a','b','e','l'];
  return <Svg title="A character window moves over a generic DNS domain label for the Character CNN">
    <Label x={64} y={102} size={39} weight={600}>A domain label is a sequence of characters.</Label>
    <Label x={64} y={146} size={20} color={amber}>DNS QUERY INPUT · GENERIC LABEL</Label>
    <rect x="90" y="250" width="920" height="124" rx="16" fill="#111115" stroke="#3d3d44"/>
    {chars.map((c,i)=><g key={i}><rect x={112+i*73} y="270" width="58" height="82" rx="8" fill={i>=offset&&i<offset+4?'#382719':'#19191e'} stroke={i>=offset&&i<offset+4?amber:'#303037'} strokeWidth={i>=offset&&i<offset+4?2:1}/><text x={141+i*73} y="323" fill={pale} fontFamily={theme.mono} fontSize="34" textAnchor="middle">{c===' '?'·':c}</text></g>)}
    <path d={`M${141+offset*73} 390v18h${(3)*73}v-18`} fill="none" stroke={amber} strokeWidth="3"/>
    <g transform="translate(120 456)"><rect width="350" height="82" rx="14" fill="#111115" stroke="#494950"/><Label x={25} y={34} size={19} color={dim}>SLIDING CHARACTER WINDOW</Label><Label x={25} y={66} size={24} color={amber}>Character CNN</Label></g>
    <Label x={526} y={489} size={23} color={dim}>Separate from DNS shape rules</Label>
    <Label x={64} y={590} size={19} color={dim}>Character windows give the model an observed sequence to examine.</Label>
  </Svg>;
};

export const EncryptedGraphic = () => {
  return <Svg title="Parallel encrypted-session analysis: packet sequence remains eligible independently of complete ClientHello metadata">
    <Label x={64} y={102} size={39} weight={600}>Two branches. Different observations.</Label>
    <Label x={64} y={146} size={20} color={amber}>ENCRYPTED-SESSION ANALYSIS</Label>
    <Node x={80} y={258} w={230} h={130} title="Observed flow" sub="sizes · timing · metadata" delay={0} accent/>
    <Flow d="M310 307 C390 307 390 228 478 228" delay={5}/><Flow d="M310 342 C390 342 390 439 478 439" delay={5}/>
    <Node x={478} y={168} w={292} h={120} title="Packet sequence" sub="sequence CNN branch" delay={8}/>
    <Node x={478} y={379} w={292} h={120} title="ClientHello" sub="complete metadata required" delay={11} accent/>
    <Flow d="M770 228 C810 228 824 228 856 228" delay={15}/><Flow d="M770 439 C810 439 824 439 856 439" delay={17}/>
    <Node x={856} y={174} w={196} h={108} title="Sequence CNN" delay={15} accent/>
    <Node x={856} y={385} w={196} h={108} title="XGBoost" sub="metadata model" delay={17} accent/>
    <g opacity={useMotion(25)}><rect x="80" y="525" width="454" height="61" rx="12" fill="#101014" stroke="#36363d"/><circle cx="108" cy="555" r="7" fill={amber}/><Label x={130} y={551} size={17} color={dim}>Public QUIC Initial inputs</Label><Label x={130} y={574} size={15} color={dim}>can reveal ClientHello metadata.</Label></g>
    <g opacity={useMotion(28)}><rect x="558" y="525" width="494" height="61" rx="12" fill="#101014" stroke="#36363d"/><Label x={580} y={551} size={16} color={dim}>No complete ClientHello? XGBoost stays ineligible.</Label><Label x={580} y={574} size={15} color={dim}>Sequence CNN remains independently eligible.</Label></g>
  </Svg>;
};
