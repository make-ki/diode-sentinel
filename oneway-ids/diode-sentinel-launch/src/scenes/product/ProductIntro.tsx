import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
import { Pulse, BrandMark, SceneBase, Heading } from './Shared';
export const ProductIntro = () => { const f = useCurrentFrame(); const sweep = interpolate(f, [5, 80], [-20, 120], { extrapolateRight: 'clamp' }); return <AbsoluteFill style={{ background: t.bg, fontFamily: t.font, color: t.text, alignItems: 'center', justifyContent: 'center' }}><Pulse /><Reveal><BrandMark size={80}/></Reveal><Reveal delay={8} style={{ fontSize: 148, fontWeight: 600, letterSpacing: -7, marginTop: 34 }}><span style={{ display: 'inline-block', backgroundImage: `linear-gradient(110deg,#dedee3 ${sweep - 10}%,#fff ${sweep}%,#dedee3 ${sweep + 10}%)`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{p.brand}</span></Reveal><Reveal delay={20} style={{ color: t.muted, fontSize: 35, marginTop: 25 }}>{p.intro.line}</Reveal></AbsoluteFill>; };
