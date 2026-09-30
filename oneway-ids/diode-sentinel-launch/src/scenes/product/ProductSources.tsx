import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
import { Pulse, BrandMark, SceneBase, Heading } from './Shared';
export const ProductSources = () => { const f = useCurrentFrame(); return <SceneBase><Heading label={p.sources.label} title={p.sources.title}/><div style={{ position: 'absolute', left: 100, top: 238 }}>{f < 115 ? <ProductCamera clip="sources" duration={115}/> : <Sequence from={115} layout="none"><ProductCamera clip="correlation" duration={110}/></Sequence>}</div><div style={{ position: 'absolute', bottom: 110, right: 135, display: 'flex', gap: 14 }}>{p.sources.support.map((m, i) => <Reveal delay={105 + i * 8} key={m.name} style={{ padding: '14px 20px', background: '#08080be8', border: `1px solid ${t.border}`, borderRadius: 10, backdropFilter: 'blur(14px)' }}><div style={{ fontSize: 27, fontWeight: 500 }}>{m.name}</div><div style={{ fontSize: 20, color: t.muted, marginTop: 5 }}>{m.role}</div></Reveal>)}</div></SceneBase>; };
