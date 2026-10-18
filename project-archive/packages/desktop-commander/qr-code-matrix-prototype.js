#!/usr/bin/env node
'use strict';
/**
 * Xoom Desktop Commander QR matrix feasibility harness.
 * OFFLINE DEVELOPMENT TOOL; NOT YET IN TWRP/AGENT.
 * Reads one official verification URL from stdin (never argv, logs, or SD).
 * Exports ASCII PBM with four-module white quiet-zone for future native renderer.
 * QR engine: separately installed qrcode-terminal v0.12.0 (Apache-2.0), see README.
 * Requires QR_VENDOR_DIR pointing to the package's vendor/QRCode directory.
 */
const fs=require('node:fs');
const path=require('node:path');
const {URL}=require('node:url');
const dest=process.argv[2];
const vendor=process.env.QR_VENDOR_DIR;
function die(msg){ process.stderr.write('QR_ERROR_'+msg+'\n');process.exit(3); }
if(process.argv.length!==3 || !dest || !vendor)die('ARGUMENTS');
if(!path.isAbsolute(dest))die('ABSOLUTE_OUTPUT_REQUIRED');
if(!fs.existsSync(path.join(vendor,'index.js')))die('VENDOR_NOT_INSTALLED');
const QRCode=require(path.join(vendor,'index.js'));
const Level=require(path.join(vendor,'QRErrorCorrectLevel.js'));
const input=fs.readFileSync(0,'utf8').trim();
if(input.length<15 || input.length>2048)die('URL_LENGTH');
let url;
try{url=new URL(input);}catch{die('MALFORMED_URL');}
if(url.protocol!=='https:' || url.username || url.password || url.port ||
   !['mcp.desktopcommander.app','desktopcommander.app'].includes(url.hostname))
   die('UNTRUSTED_HOST_OR_SCHEME');
if(url.hash)die('FRAGMENT_NOT_SUPPORTED');
const qrcode=new QRCode(-1,Level.Q);
try{qrcode.addData(input);qrcode.make();}catch{die('QR_CAPACITY');}
const n=qrcode.getModuleCount();
if(n<21 || n>145 || !(n%4===1))die('MATRIX_SIZE');
const b=4,N=n+2*b;
const rows=['P1','# Xoom pairing QR, 4-module quiet-zone, 1=black, RAM only',N+' '+N];
for(let y=0;y<N;y++){
 const parts=[];
 for(let x=0;x<N;x++){
  const black=(x>=b && y>=b && x<b+n && y<b+n) ? qrcode.isDark(y-b,x-b) : false;
  parts.push(black?'1':'0');
 }
 rows.push(parts.join(' '));
}
const value=rows.join('\n')+'\n';
const dir=path.dirname(dest);
const st=fs.statSync(dir);
if(!st.isDirectory() || st.isSymbolicLink())die('UNSAFE_DIRECTORY');
if(fs.existsSync(dest) || fs.existsSync(dest+'.stage'))die('TARGET_ALREADY_EXISTS');
const tmp=dest+'.stage';
try{
 fs.writeFileSync(tmp,value,{encoding:'ascii',flag:'wx',mode:0o600});
 fs.renameSync(tmp,dest);
}catch(e){try{fs.unlinkSync(tmp)}catch{}die('WRITE_FAILED');}
process.stdout.write('QR_MATRIX_READY dimensions='+N+'x'+N+' modules='+n+' quiet_zone=4\n');
