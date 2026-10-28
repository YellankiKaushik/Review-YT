// Read-only approved hash verification. V1 is optional, retained locally when present.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');const read=n=>JSON.parse(fs.readFileSync(path.join(root,'docs',n),'utf8'));
function hash(file){return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')}
const assets=read('asset-manifest.json'),delivery=read('delivery-manifest.json');
for(const a of assets.assets)if(hash(path.join(root,a.file))!==a.sha256)throw Error('Input hash mismatch '+a.file);
for(const a of delivery.finals)if(hash(path.join(root,'output',a.file))!==a.sha256)throw Error('Approved media changed '+a.file);
let legacy=0;for(const a of assets.legacy||[]){const file=path.join(root,'output',a.file);if(fs.existsSync(file)){if(hash(file)!==a.sha256)throw Error('V1 changed');legacy++}}
console.log(`Verified ${assets.assets.length} inputs, ${delivery.finals.length} approved finals; ${legacy} optional local V1 files unchanged`);
