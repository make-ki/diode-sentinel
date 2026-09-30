import React from 'react';
import { Composition } from 'remotion';
import { ProductFilm } from './ProductFilm';
import { product } from './product-config';
import {ExplainerFilm} from './explainer/ExplainerFilm';
import {explainer} from './explainer/data.generated';
export const Root = () => <><Composition id="DiodeSentinelProductDemo" component={ProductFilm} durationInFrames={product.duration} fps={product.fps} width={product.width} height={product.height}/><Composition id="DiodeSentinelExplainer" component={ExplainerFilm} durationInFrames={explainer.duration} fps={explainer.fps} width={explainer.width} height={explainer.height}/></>;
