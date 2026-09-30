import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
import { Pulse, BrandMark, SceneBase, Heading } from './Shared';
export const ProductModel: React.FC<{
    index: number;
}> = ({ index }) => { const m = p.modelCards[index]; const f = useCurrentFrame(); const reveal = spring({ frame: f - 5, fps: 30, config: t.spring }); return <SceneBase><Heading label={m.role} title={m.title}/><div style={{ position: 'absolute', left: 100, top: 245 }}><ProductCamera clip={m.clip} width={1180} height={730} duration={125} model/></div><div style={{ position: 'absolute', left: 1350, top: 270, width: 450, opacity: reveal, transform: `translateX(${(1 - reveal) * 35}px)`, filter: `blur(${(1 - reveal) * 5}px)` }}><div style={{ height: 2, width: 70, background: t.accent, marginBottom: 36 }}/><div style={{ fontSize: 49, fontWeight: 600, letterSpacing: -1.5, lineHeight: 1.14, marginBottom: 40 }}>{m.name}</div>{m.features.map((line, i) => <Reveal delay={13 + i * 8} key={line} style={{ fontFamily: t.mono, fontSize: 26, color: t.muted, lineHeight: 1.45, padding: '23px 0', borderBottom: `1px solid ${t.border}` }}>{line}</Reveal>)}<div style={{ marginTop: 46, fontFamily: t.mono, fontSize: 19, color: t.muted, lineHeight: 1.6 }}>{m.note}</div></div></SceneBase>; };
