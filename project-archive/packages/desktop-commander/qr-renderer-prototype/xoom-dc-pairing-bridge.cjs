'use strict';
// Desktop Commander Xoom-native device verification presentation bridge.
// Called ONLY with the official provider device-code response.
// No network requests, browser launch, authentication decisions, or token storage.
const fs = require('node:fs');
const path = require('node:path');
const ROOT = '/tmp/xoom-dc-pairing';
const QR_PATH = ROOT + '/qr.pbm';
const STATE_PATH = ROOT + '/state.txt';
const QR_PATH_STAGING = ROOT + '/qr.pbm.stage';
const STATE_PATH_STAGING = ROOT + '/state.txt.stage';
const host = 'mcp.desktopcommander.app';
function ensureDir() {
 if(process.getuid && process.getuid()!==0)throw Error('PAIRING_REQUIRES_ROOT');
 if(!fs.existsSync(ROOT))fs.mkdirSync(ROOT,{mode:0o700});
 const info=fs.lstatSync(ROOT);
 if(!info.isDirectory() || info.isSymbolicLink() || info.uid!==0 || (info.mode & 0o077)!==0)
   throw Error('PAIRING_DIR_UNSAFE');
}
function writeState(status,code,expires) {
 ensureDir();
 const value = 'v1\n'+status+'\n'+code+'\n'+String(expires)+'\n';
 try {
  fs.writeFileSync(STATE_PATH_STAGING,value,{flag:'wx',mode:0o600});
  fs.renameSync(STATE_PATH_STAGING,STATE_PATH);
 } catch(e) {
  try { fs.unlinkSync(STATE_PATH_STAGING); } catch {}
  throw e;
 }
}
function clear(status) {
 if(!['AUTHORIZED','EXPIRED','STOPPED'].includes(status))status='STOPPED';
 if(!fs.existsSync(ROOT))return;
 ensureDir();
 for(const p of [QR_PATH,QR_PATH_STAGING,STATE_PATH_STAGING]) {
  try{fs.unlinkSync(p);}catch(e){if(e.code!=='ENOENT')throw e;}
 }
 writeState(status,'',0);
}
function publish(auth) {
 if(!auth || typeof auth!=='object')throw Error('PROVIDER_RESPONSE_INVALID');
 const url=String(auth.verification_uri_complete||'');
 const usercode=String(auth.user_code||'');
 const duration=Number(auth.expires_in);
 let parsed;
 try{parsed=new URL(url);}catch{throw Error('PROVIDER_URL_INVALID');}
 if(parsed.protocol!=='https:' || parsed.host!==host ||
    parsed.username || parsed.password || parsed.hash ||
    url.length<20 || url.length>1700)throw Error('PROVIDER_HOST_INVALID');
 if(!/^[A-Za-z0-9-]{4,32}$/.test(usercode))throw Error('USER_CODE_INVALID');
 if(!Number.isFinite(duration)||duration<30||duration>1800)throw Error('EXPIRY_INVALID');
 const QRCode=require('./vendor/QRCode/index.js');
 const Level=require('./vendor/QRCode/QRErrorCorrectLevel.js');
 const qr=new QRCode(-1,Level.Q);
 qr.addData(url);
 qr.make();
 const n=qr.getModuleCount();
 if(n<21 || n>145 || n%4!==1)throw Error('QR_SIZE_INVALID');
 const extent=n+8;
 const lines=['P1','# Direct first-party Desktop Commander verification',extent+' '+extent];
 for(let y=0;y<extent;y++) {
  const cells=[];
  for(let x=0;x<extent;x++)
   cells.push(x>=4 && x<extent-4 && y>=4 && y<extent-4 && qr.isDark(y-4,x-4)?'1':'0');
  lines.push(cells.join(' '));
 }
 const matrix=lines.join('\n')+'\n';
 const expires=Math.floor(Date.now()/1000)+Math.floor(duration);
 ensureDir();
 if(fs.existsSync(QR_PATH_STAGING))throw Error('STAGING_FILE_ALREADY_EXISTS');
 try {
  fs.writeFileSync(QR_PATH_STAGING,matrix,{mode:0o600,flag:'wx'});
  fs.renameSync(QR_PATH_STAGING,QR_PATH);
 }catch(e){
  try{fs.unlinkSync(QR_PATH_STAGING);}catch{}
  throw e;
 }
 writeState('PENDING',usercode,expires);
 return {side:extent,expires}; // No code or URL in logs.
}
module.exports={publish,clear};
