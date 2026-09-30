import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
import { Pulse, BrandMark, SceneBase, Heading } from './Shared';
export const ProductClosing = () => <AbsoluteFill style={{ background: t.bg, color: t.text, fontFamily: t.font, alignItems: 'center', justifyContent: 'center' }}><Pulse /><Reveal><BrandMark size={85}/></Reveal><Reveal delay={9} style={{ fontSize: 145, fontWeight: 600, letterSpacing: -7, marginTop: 34 }}>{p.brand}</Reveal><Reveal delay={18} style={{ fontSize: 36, color: t.muted, marginTop: 25 }}>{p.closing.line}</Reveal><Reveal delay={30} style={{ fontSize: 31, marginTop: 50, color: t.accent, fontFamily: t.mono }}>{p.closing.by} {p.team}</Reveal><div style={{ position: 'absolute', bottom: 73, fontFamily: t.mono, fontSize: 21, color: t.muted }}>{p.closing.event}</div></AbsoluteFill>;
