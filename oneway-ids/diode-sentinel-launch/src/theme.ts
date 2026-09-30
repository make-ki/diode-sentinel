import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';
export const theme = {
  bg:'#030305', panel:'#0b0b0f', border:'#252529', text:'#fafafa', muted:'#9c9ca5',
  accent:'#ff8a1f', critical:'#ff4d4d', amber:'#ffd166',
  font:loadInter('normal',{weights:['400','500','600','700'],subsets:['latin']}).fontFamily,
  mono:loadMono('normal',{weights:['400','500'],subsets:['latin']}).fontFamily,
  spring:{damping:28,stiffness:110,mass:1},
};
