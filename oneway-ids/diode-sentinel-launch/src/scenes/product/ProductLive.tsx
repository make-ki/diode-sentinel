import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { theme as t } from '../../theme';
import { product as p } from '../../product-config';
import { Reveal } from '../../ui';
import { ProductCamera } from '../../ui/ProductCamera';
import { Pulse, BrandMark, SceneBase, Heading } from './Shared';
export const ProductLive = () => <SceneBase><Heading label={p.live.label} title={p.live.title}/><div style={{ position: 'absolute', left: 100, top: 238 }}><ProductCamera clip="overview" duration={252}/></div></SceneBase>;
