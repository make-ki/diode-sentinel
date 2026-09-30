import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
export const Pulse = () => { const f = useCurrentFrame(); const glow = interpolate(f, [0, 18, 45, 110], [0, .6, .16, .08], { extrapolateRight: 'clamp' }); return <div style={{ position: 'absolute', width: 700, height: 700, left: 610, top: 100, borderRadius: '50%', background: 'radial-gradient(circle,#ff8a1f12,transparent 68%)', opacity: glow, transform: `scale(${1 + f * .001})` }}/>; };
export const BrandMark: React.FC<{
    size?: number;
}> = ({ size = 62 }) => <svg width={size} height={size} viewBox="0 0 64 64"><path d="M8 32 H47 M34 16 L50 32 L34 48 M55 9 V55" stroke={t.accent} strokeWidth="3" fill="none"/></svg>;
export const SceneBase: React.FC<{
    children: React.ReactNode;
}> = ({ children }) => <AbsoluteFill style={{ background: t.bg, color: t.text, fontFamily: t.font }}>{children}<div style={{ position: 'absolute', bottom: 30, left: 105, color: t.muted, fontFamily: t.mono, fontSize: 19, letterSpacing: .5 }}>{p.qualifier}</div><div style={{ position: 'absolute', top: 44, right: 100, color: t.muted, fontFamily: t.mono, fontSize: 20 }}>{p.team}</div></AbsoluteFill>;
export const Heading: React.FC<{
    label: string;
    title: string;
}> = ({ label, title }) => <div style={{ position: 'absolute', top: 42, left: 100, right: 100 }}><Reveal style={{ fontFamily: t.mono, fontSize: 23, color: t.accent, letterSpacing: 1, marginBottom: 15 }}>{label}</Reveal><Reveal delay={6} style={{ fontSize: 78, fontWeight: 600, letterSpacing: -3.5, lineHeight: 1.08 }}>{title}</Reveal></div>;
