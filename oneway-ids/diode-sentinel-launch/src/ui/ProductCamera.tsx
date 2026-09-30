import React from 'react';
import { OffthreadVideo, staticFile, useCurrentFrame, interpolate, Easing, spring } from 'remotion';
import { capture } from '../capture.generated';
import { theme as t } from '../theme';
type Profile = {
    zoom: readonly [
        number,
        number
    ];
    center: readonly [
        number,
        number
    ];
    start?: number;
    endCenter?: readonly [
        number,
        number
    ];
    panDelay?: number;
};
const profiles: Record<string, Profile> = { overview: { zoom: [1.18, 1.42], center: [965, 365], start: 1.5 }, evidence: { zoom: [1.75, 2.05], center: [792, 280], endCenter: [792, 450], start: 3.0, panDelay: 96 }, sources: { zoom: [1.26, 1.30], center: [905, 310], start: 4.6 }, correlation: { zoom: [1.62, 1.80], center: [792, 505], start: 5.4 }, dns: { zoom: [1.38, 1.50], center: [792, 380] }, encrypted: { zoom: [1.38, 1.50], center: [792, 393] }, scan: { zoom: [1.42, 1.58], center: [792, 410] }, exfil: { zoom: [1.42, 1.54], center: [792, 410] }, sensor: { zoom: [2.0, 2.1], center: [1160, 115], start: 1.7 } };
export const ProductCamera: React.FC<{
    clip: string;
    width?: number;
    height?: number;
    duration?: number;
    model?: boolean;
}> = ({ clip, width = 1720, height = 738, duration = 240, model = false }) => { const f = useCurrentFrame(); const profile = profiles[clip]; const progress = interpolate(f, [profile.panDelay ?? 0, duration], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(.2, .7, .2, 1) }); const info = (capture.clips as Record<string, {
    recordedSeconds: number;
}>)[clip]; const start = model ? Math.max(0, (info?.recordedSeconds ?? 8) - 4.7) : (profile.start ?? 0); const zoom = interpolate(progress, [0, 1], profile.zoom as [
    number,
    number
]); const center = profile.center.map((v, i) => interpolate(progress, [0, 1], [v, profile.endCenter?.[i] ?? v])); const x = Math.max(width - 1600 * zoom, Math.min(0, width / 2 - center[0] * zoom)); const y = Math.max(height - 1000 * zoom, Math.min(0, height / 2 - center[1] * zoom)); const enter = spring({ frame: f, fps: 30, config: t.spring }); return <div style={{ position: 'relative', width, height, overflow: 'hidden', borderRadius: 20, border: '1px solid #333338', background: '#000', boxShadow: '0 35px 110px #000b,0 0 90px #ff8a1f08', transform: `perspective(2200px) translateY(${(1 - enter) * 24}px) rotateX(${(1 - enter) * 2}deg)`, opacity: enter }}><OffthreadVideo src={staticFile(`captures/${clip}.mp4`)} startFrom={Math.round(start * 30)} muted style={{ position: 'absolute', left: 0, top: 0, width: 1600, height: 1000, transformOrigin: '0 0', transform: `translate(${x}px,${y}px) scale(${zoom})` }}/><div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', boxShadow: 'inset 0 0 60px #0003', borderRadius: 20 }}/><div style={{ position: 'absolute', top: 0, left: 60, right: 60, height: 1, background: 'linear-gradient(90deg,transparent,#fff5,transparent)' }}/></div>; };
