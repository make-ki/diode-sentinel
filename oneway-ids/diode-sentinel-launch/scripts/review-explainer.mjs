import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import {readFileSync, mkdirSync, writeFileSync} from 'node:fs';
import path from 'node:path';

const root=process.cwd();
const beats=JSON.parse(readFileSync('explainer-beats.json','utf8'));
const output=path.join(root,'out/explainer-review');
mkdirSync(output,{recursive:true});
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),symlinkPublicDir:true});
const browser=await openBrowser('chrome',{browserExecutable:'/home/stark/.nix-profile/bin/chromium',logLevel:'error'});
const errors=[];
const onBrowserLog=log=>{if(log.type==='error')errors.push(log.text);};
const shots=[];
try{
  const composition=await selectComposition({serveUrl,id:'DiodeSentinelExplainer',puppeteerInstance:browser,onBrowserLog});
  for(let i=0;i<beats.cuts.length;i++){
    const cut=beats.cuts[i];
    const end=beats.cuts[i+1]?.frame??beats.durationFrames;
    const frames=[['graphic',Math.min(end-1,cut.graphicRevealFrame+110)]];
    if(!['intro','closing'].includes(cut.id)) {
      frames.push(['software',Math.min(end-1,cut.uiRevealFrame+250)]);
      frames.push(['completion',end-50]);
    }
    for(const [kind,frame] of frames){
      const file=path.join(output,`${cut.id}-${kind}.png`);
      await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:file,imageFormat:'png',onBrowserLog});
      shots.push({scene:cut.id,kind,frame,file});
      console.log(`Reviewed frame ${cut.id}/${kind}`);
    }
  }
}finally{await browser.close({silent:true});}
writeFileSync(path.join(output,'frames.json'),JSON.stringify({shots,browserErrors:errors},null,2));
if(errors.length)throw new Error(JSON.stringify(errors));
