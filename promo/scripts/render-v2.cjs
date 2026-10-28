// Node 24 on this Windows host requires hidden-window mode for renderer-owned Chrome.
// Local process wrapper only: dependencies and unrelated applications are unchanged.
const childProcess=require('node:child_process');const nativeSpawn=childProcess.spawn;
childProcess.spawn=function(exe,args,opts){return nativeSpawn(exe,args,process.platform==='win32'&&/chrome(?:-headless-shell)?\.exe$/i.test(exe)?{...opts,windowsHide:true}:opts)};const path=require('node:path'),fs=require('node:fs');const {bundle}=require('@remotion/bundler');const {selectComposition,renderMedia,renderStill}=require('@remotion/renderer');
const root=path.resolve(__dirname,'..');process.chdir(root);
let browserExecutable=process.env.REMOTION_BROWSER_EXECUTABLE;
if(!browserExecutable && process.platform==='win32'){
 const installed=require('@playwright/test').chromium.executablePath().replace('chromium-','chromium_headless_shell-').replace('chrome-win64','chrome-headless-shell-win64').replace('chrome.exe','chrome-headless-shell.exe');
 if(fs.existsSync(installed))browserExecutable=installed;
}
// If unset, the official renderer resolves/downloads its supported platform browser.
if(browserExecutable&&!fs.existsSync(browserExecutable))throw Error('REMOTION_BROWSER_EXECUTABLE does not exist');
(async()=>{const mode=process.argv[2]||'all';fs.mkdirSync('output',{recursive:true});fs.mkdirSync('review-v2',{recursive:true});
 const serveUrl=await bundle({entryPoint:path.join(root,'src/Root.tsx'),publicDir:path.join(root,'public'),onProgress:()=>{}});
 async function comp(id){return selectComposition({serveUrl,id,browserExecutable,logLevel:'error'})}
 async function still(id,frame,name,scale=1){await renderStill({serveUrl,composition:await comp(id),output:path.join(root,name),frame,scale,browserExecutable,logLevel:'error'});console.log('Still '+name)}
 async function movie(id,name,scale=1,crf=18){let last=-1;await renderMedia({serveUrl,composition:await comp(id),outputLocation:path.join(root,name),codec:'h264',pixelFormat:'yuv420p',crf,scale,concurrency:4,browserExecutable,logLevel:'error',onProgress:p=>{const n=Math.floor(p.progress*10);if(n>last){last=n;console.log(id+' '+n*10+'%')}}});await require('./normalize-video.cjs')(path.join(root,name));console.log('Rendered '+name)}
 if(mode==='validate'){for(const id of ['YouTubeLaunch','VerticalReel','GithubPreview','Thumbnail']){const c=await comp(id);console.log(`${id}: ${c.width}x${c.height}, ${c.durationInFrames} frames`)}return}
 if(mode==='thumbnail'){await still('Thumbnail',0,'output/review-yt-thumbnail.png');return}
 if(mode==='frames'){for(const [f,n]of[[75,'noise'],[300,'signal'],[360,'reveal-entry'],[495,'reveal'],[830,'workflow-action'],[1035,'chart'],[1170,'actual-chart'],[1260,'mobile-entry'],[1395,'responsive'],[1635,'pipeline'],[2040,'cta']])await still('YouTubeLaunch',f,'review-v2/design-'+n+'.png');await still('VerticalReel',450,'review-v2/design-vertical.png');await still('VerticalReel',580,'review-v2/design-vertical-ui.png');await still('VerticalReel',870,'review-v2/design-vertical-cta.png');await still('GithubPreview',130,'review-v2/design-preview.png');await still('Thumbnail',0,'output/review-yt-thumbnail.png');return}
 if(mode==='rough'){await movie('YouTubeLaunch','review-v2/rough-cut.mp4',.5,25);return}
 if(['youtube','all'].includes(mode))await movie('YouTubeLaunch','output/review-yt-youtube-1080p.mp4');
 if(['reel','all'].includes(mode))await movie('VerticalReel','output/review-yt-reel-vertical.mp4');
 if(['github','all'].includes(mode)){await movie('GithubPreview','output/review-yt-github-preview.mp4',1,20);await require('./make-gif.cjs')();}
 if(mode==='all')await still('Thumbnail',0,'output/review-yt-thumbnail.png');
})().catch(e=>{console.error(e.stack);process.exitCode=1});
