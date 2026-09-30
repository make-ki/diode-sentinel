import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, interpolate } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { timeline } from './product-timeline.generated';
import { narration } from './narration.generated';
import { productAssets } from './product-assets.generated';
import { product } from './product-config';
import { theme } from './theme';
import { ProductIntro, ProductLive, ProductEvidence, ProductSources, ProductModel, ProductPassive, ProductClosing } from './scenes/ProductScenes';
const Music = () => productAssets.music ? <Audio src={staticFile(productAssets.music)} volume={f => { const fadeIn = Math.min(1, f / 30); const fadeOut = Math.min(1, (product.duration - f) / 60); let duck = 1; for (const n of narration) {
    const start = n.startFrame, end = start + n.durationFrames;
    duck = Math.min(duck, interpolate(f, [start - 8, start, end, end + 12], [1, .27, .27, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
} return .72 * Math.max(0, Math.min(fadeIn, fadeOut)) * duck; }}/> : null;
export const ProductFilm = () => { const scenes = [<ProductIntro />, <ProductLive />, <ProductEvidence />, <ProductSources />, <ProductModel index={0}/>, <ProductModel index={1}/>, <ProductModel index={2}/>, <ProductModel index={3}/>, <ProductPassive />, <ProductClosing />]; return <AbsoluteFill style={{ background: theme.bg }}><TransitionSeries>{timeline.map((cut, i) => <React.Fragment key={cut.id}>{i > 0 && <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })}/>}<TransitionSeries.Sequence durationInFrames={cut.end - cut.start + (i < timeline.length - 1 ? 10 : 0)}>{scenes[i]}</TransitionSeries.Sequence></React.Fragment>)}</TransitionSeries><Music />{productAssets.narration && narration.map(n => <Sequence key={n.id} from={n.startFrame} durationInFrames={n.durationFrames}><Audio src={staticFile(n.file)} volume={1}/></Sequence>)}</AbsoluteFill>; };
