'use strict';
// Experimental Xoom v0.4 FS worker: launched under UID/GID2000, not root.
const fs=require('node:fs'), fsp=fs.promises, path=require('node:path'), crypto=require('node:crypto');
const ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch',UID=2000,MAX=32768,F=fs.constants;
const PDF=require('./xoom-pdf-maker-v06.js');
const re=/^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/;
function valid(v,rootOK=false){
 if(typeof v!=='string')throw Error('Path must be string');
 const rel=v==='.'||v===ROOT?'':v.startsWith(ROOT+'/')?v.slice(ROOT.length+1):v;
 const parts=rel?rel.split('/'):[];
 if((!rootOK&&!parts.length)||parts.length>4||parts.some(s=>!re.test(s)||s==='..'))throw Error('Only paths within scratch, max four components');
 return {rel:parts.join('/'),parts,full:path.join(ROOT,...parts)};
}
async function isDir(full){
 const st=await fsp.lstat(full);
 if(!st.isDirectory()||st.uid!==UID||st.gid!==UID||(st.mode&0o777)!==0o700)throw Error('Unsafe directory (expected uid/gid2000 mode0700; no symlinks)');
}
async function check(v,rootOK=false){
 const p=valid(v,rootOK);
 await isDir(ROOT);
 for(let j=1;j<p.parts.length;j++)await isDir(path.join(ROOT,...p.parts.slice(0,j)));
 return p;
}
function fileOK(st){
 if(!st.isFile()||st.uid!==UID||st.gid!==UID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>MAX)throw Error('Only private single-link regular files up to 32KiB');
}
function utf(buf){if(buf.includes(0))throw Error('Binary file');return new TextDecoder('utf-8',{fatal:true}).decode(buf)}
async function read(v){
 const p=await check(v);
 if(/\.(pdf|png|jpg|jpeg|gif|webp|zip|elf|gz)$/i.test(p.rel))throw Error('Binary file type is not a UTF-8 text document');
 const h=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
 try{
  fileOK(await h.stat());
  const b=Buffer.alloc(MAX+1);let i=0;
  while(i<b.length){let n=await h.read(b,i,b.length-i,i);if(!n.bytesRead)break;i+=n.bytesRead}
  if(i>MAX)throw Error('File grew above size limit');
  return utf(b.subarray(0,i));
 }finally{await h.close()}
}
async function write(v,data,mode='rewrite',explicitMode=false){
 const p=await check(v);
 if(mode!=='rewrite'&&mode!=='append')throw Error('mode must be rewrite or append');
 if(typeof data!=='string'||Buffer.byteLength(data)>MAX||data.includes('\0')||utf(Buffer.from(data,'utf8'))!==data)throw Error('Invalid UTF8 or length');
 let priorSt=null;
 try{priorSt=await fsp.lstat(p.full);fileOK(priorSt)}catch(e){if(e.code!=='ENOENT')throw e}
 if(priorSt&&priorSt.size>0&&!explicitMode)throw Error('Existing nonempty file requires explicit rewrite or append mode');
 if(mode==='append'&&priorSt)data=(await read(v))+data;
 if(Buffer.byteLength(data)>MAX)throw Error('Append would exceed 32KiB cap');
 const tmp=path.join(path.dirname(p.full),'.v04-'+crypto.randomBytes(10).toString('hex'));
 const h=await fsp.open(tmp,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{await h.writeFile(data,'utf8');await h.sync()}finally{await h.close()}
 try{await fsp.rename(tmp,p.full)}catch(e){await fsp.unlink(tmp).catch(()=>{});throw e}
 return {file:p.rel,bytes:Buffer.byteLength(data),mode,existingFile:!!priorSt};
}
async function makeDir(v){
 const p=await check(v);
 if(p.parts.length>3)throw Error('Maximum 3 nested directories');
 let created=false;
 try{await isDir(p.full)}catch(e){
  if(e.code!=='ENOENT')throw e;
  await fsp.mkdir(p.full,{mode:0o700});created=true;
 }
 await isDir(p.full);
 return {directory:p.rel,created};
}
async function move(src,dst){
 const a=await check(src),b=await check(dst);
 if(a.full===b.full)throw Error('Source equals target');
 const st=await fsp.lstat(a.full),folder=st.isDirectory();
 if(st.uid!==UID||st.gid!==UID||!(folder?(st.mode&0o777)===0o700:st.isFile()&&st.nlink===1&&(st.mode&0o777)===0o600))throw Error('Only owned regular files or directories; links rejected');
 try{await fsp.lstat(b.full);throw Error('Destination already exists')}catch(e){if(e.code!=='ENOENT')throw e}
 if(folder&&b.full.startsWith(a.full+'/'))throw Error('Nested self move rejected');
 await fsp.rename(a.full,b.full);
 return {source:a.rel,destination:b.rel,type:folder?'directory':'file'};
}
async function list(v,depth){
 const p=await check(v||ROOT,true);await isDir(p.full);
 const result=[],max=Math.min(3,Math.max(1,Number.isInteger(depth)?depth:2));
 async function walk(full,rel,d){
  if(result.length>=150)return;
  const xs=(await fsp.readdir(full,{withFileTypes:true})).filter(x=>!x.name.startsWith('.')).sort((a,b)=>a.name.localeCompare(b.name));
  for(const x of xs){
   if(result.length>=150)break;
   const filename=rel?rel+'/'+x.name:x.name,st=await fsp.lstat(path.join(full,x.name)).catch(()=>null);
   if(!st)continue;
   const type=x.isSymbolicLink()?'other':st.isDirectory()?'directory':st.isFile()?'file':'other';
   result.push({name:filename,type});
   if(type==='directory'&&d>1&&st.uid===UID&&st.gid===UID&&(st.mode&0o777)===0o700)await walk(path.join(full,x.name),filename,d-1);
  }
 }
 await walk(p.full,'',max);
 return {root:p.full,entries:result,truncated:result.length>=150};
}
function escapeRe(s){return s.replace(/[.*+?^$()|[\]{}\\]/g,'\\$&')}
function matcher(s,literal,ignoreCase){
 if(typeof s!=='string'||!s||s.length>128)throw Error('Search pattern must be 1–128 chars');
 let src=literal?escapeRe(s):s;
 if(!literal&&s.startsWith('*.'))src='^.*\\.'+escapeRe(s.slice(2))+'$';
 return new RegExp(src,ignoreCase?'i':'');
}
function filter(s){
 if(s===undefined||s==='')return ()=>true;
 if(typeof s!=='string'||s.length>120)throw Error('Bad filePattern');
 const arr=s.split('|').slice(0,8).map(p=>new RegExp('^'+p.split('*').map(escapeRe).join('.*')+'$','i'));
 return n=>arr.some(r=>r.test(n));
}
async function search(a){
 const base=await check(a.path||ROOT,true);await isDir(base.full);
 const type=a.searchType||'files';if(type!=='files'&&type!=='content')throw Error('Unknown searchType');
 const re=matcher(a.pattern,a.literalSearch===true,a.ignoreCase!==false),allowed=filter(a.filePattern);
 const cap=Math.min(120,Math.max(1,Number.isInteger(a.maxResults)&&a.maxResults>0?a.maxResults:120));
 const ctx=Math.min(2,Math.max(0,Number.isInteger(a.contextLines)?a.contextLines:1));
 let scanned=0,truncated=false;const results=[];
 async function walk(full,rel,depth){
  if(depth>4||results.length>=cap||scanned>=300){truncated=true;return}
  const entries=(await fsp.readdir(full,{withFileTypes:true})).sort((a,b)=>a.name.localeCompare(b.name));
  for(const e of entries){
   if(results.length>=cap||scanned>=300){truncated=true;break}
   if(e.name.startsWith('.'))continue;
   const r=rel?rel+'/'+e.name:e.name,fullPath=path.join(full,e.name);
   const st=await fsp.lstat(fullPath).catch(()=>null);if(!st)continue;
   scanned++;
   if(e.isSymbolicLink())continue;
   if(st.isDirectory()){
    if(depth<4&&st.uid===UID&&st.gid===UID&&(st.mode&0o777)===0o700)await walk(fullPath,r,depth+1);
    continue;
   }
   if(!st.isFile()||st.uid!==UID||st.gid!==UID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>MAX||!allowed(e.name))continue;
   if(type==='files'){
    if(re.test(e.name))results.push({type:'file',file:fullPath,relativePath:r});
   }else{
    let body;try{body=await read(r)}catch{continue}
    const lines=body.split('\n');
    for(let j=0;j<lines.length&&results.length<cap;j++)if(re.test(lines[j])){
     results.push({type:'content',file:fullPath,relativePath:r,line:j+1,match:lines[j].slice(0,240),context:lines.slice(Math.max(0,j-ctx),j+ctx+1).map(z=>z.slice(0,240)).join('\n')});
    }
   }
  }
 }
 await walk(base.full,base.rel,0);
 return {searchType:type,pattern:a.pattern,results,scanned,truncated,complete:true};
}

const MAX_LARGE=262144,MAX_IMAGE=61440,MAX_PAGE=16384;
function imageMime(rel,b){
 const n=rel.toLowerCase();
 if(n.endsWith('.png')&&b.length>=24&&b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&b.toString('ascii',12,16)==='IHDR'&&b.includes(Buffer.from('IEND')))return 'image/png';
 if((n.endsWith('.jpg')||n.endsWith('.jpeg'))&&b.length>=4&&b[0]===255&&b[1]===216&&b[b.length-2]===255&&b[b.length-1]===217)return 'image/jpeg';
 if(n.endsWith('.gif')&&b.length>=14&&/^GIF8[79]a$/.test(b.toString('ascii',0,6))&&b[b.length-1]===0x3b)return 'image/gif';
 if(n.endsWith('.webp')&&b.length>=20&&b.toString('ascii',0,4)==='RIFF'&&b.toString('ascii',8,12)==='WEBP'&&b.readUInt32LE(4)===b.length-8)return 'image/webp';
 throw Error('Unsupported, mismatched, or malformed image content');
}
async function openPrivate(v,max=MAX_LARGE){
 const p=await check(v),h=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
 try{
  const st=await h.stat();
  if(!st.isFile()||st.uid!==UID||st.gid!==UID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>max)throw Error('Private file ownership/mode/link/size requirement failed');
  return {p,h,st};
 }catch(e){await h.close();throw e}
}
async function readWide(v,max=MAX_LARGE){
 const x=await openPrivate(v,max);
 try{
  const b=Buffer.alloc(x.st.size+1);
  let at=0;
  while(at<b.length){
   const n=await x.h.read(b,at,b.length-at,at);
   if(!n.bytesRead)break;
   at+=n.bytesRead;
  }
  if(at>max)throw Error('File grew above limit while reading');
  return {p:x.p,b:b.subarray(0,at),st:x.st};
 }finally{await x.h.close()}
}
function decodeWide(buf){
 if(buf.includes(0))throw Error('NUL/binary data cannot be read as text');
 return new TextDecoder('utf-8',{fatal:true}).decode(buf);
}
function textExtension(rel){
 if(/\.(png|jpe?g|gif|webp|pdf|zip|gz|elf|bin|so|exe|db|sqlite)$/i.test(rel))throw Error('Binary file type not allowed in text operations');
}
async function readTextPage(a){
 const x=await readWide(a.path),rel=x.p.rel;
 textExtension(rel);
 const t=decodeWide(x.b),lines=t.split('\n');
 let off=a.offset===undefined?0:a.offset;
 const len=a.length===undefined?100:a.length;
 if(!Number.isInteger(off)||!Number.isInteger(len)||len<0||len>200)throw Error('Offset integer, length 0..200 lines required');
 if(off<0)off=Math.max(0,lines.length+off);
 const selected=lines.slice(off,off+len).join('\n');
 if(Buffer.byteLength(selected)>MAX_PAGE)throw Error('Read page exceeds 16KiB; request fewer lines');
 return {file:rel,totalLines:lines.length,text:selected,offset:off,length:len,fileBytes:x.b.length,sourceLimitBytes:MAX_LARGE};
}
async function writeTextChunk(a){
 const p=await check(a.path);
 textExtension(p.rel);
 const mode=a.mode===undefined?'rewrite':a.mode;
 if(mode!=='rewrite'&&mode!=='append')throw Error('mode must be rewrite or append');
 if(typeof a.content!=='string'||Buffer.byteLength(a.content,'utf8')>MAX||a.content.includes('\0'))throw Error('Each chunk must be valid UTF-8 without NUL and at most 32KiB');
 const part=Buffer.from(a.content,'utf8');
 if(decodeWide(part)!==a.content)throw Error('Invalid Unicode text input');
 let prior=null,old=Buffer.alloc(0);
 try{
  const h=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
  try{
   const st=await h.stat();
   if(!st.isFile()||st.uid!==UID||st.gid!==UID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>MAX_LARGE)throw Error('Existing target is not an owned private single-link text file');
   prior=st;
  }finally{await h.close()}
  if(mode==='append'&&prior){
   const x=await readWide(a.path);
   old=x.b;
   textExtension(x.p.rel);
   decodeWide(old);
  }
 }catch(e){if(e.code!=='ENOENT')throw e}
 if(prior&&prior.size>0&&a.mode===undefined)throw Error('Nonempty file requires explicit rewrite or append mode');
 const total=(mode==='append'?old.length:0)+part.length;
 if(total>MAX_LARGE)throw Error('Total file would exceed 256KiB');
 const tmp=path.join(path.dirname(p.full),'.v09-'+crypto.randomBytes(12).toString('hex'));
 const h=await fsp.open(tmp,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{
  if(mode==='append'&&old.length)await h.writeFile(old);
  await h.writeFile(part);
  await h.sync();
 }finally{await h.close()}
 try{await fsp.rename(tmp,p.full)}catch(e){await fsp.unlink(tmp).catch(()=>{});throw e}
 return {file:p.rel,bytes:total,chunkBytes:part.length,mode,existingFile:!!prior,limitBytes:MAX_LARGE};
}
function dimensionsForImage(mime,b){
 let width=0,height=0;
 if(mime==='image/png'){
  if(b.length<33||b.readUInt32BE(8)!==13)throw Error('Invalid PNG IHDR');
  width=b.readUInt32BE(16);height=b.readUInt32BE(20);
 }else if(mime==='image/gif'){
  width=b.readUInt16LE(6);height=b.readUInt16LE(8);
 }else if(mime==='image/jpeg'){
  let p=2;
  while(p<b.length){
   if(b[p++]!==255)throw Error('Invalid JPEG marker');
   while(p<b.length&&b[p]===255)p++;
   const marker=b[p++];
   if(marker===217||marker===218)break;
   if(p+2>b.length)throw Error('Truncated JPEG marker');
   const n=b.readUInt16BE(p);
   if(n<2||p+n>b.length)throw Error('Invalid JPEG marker length');
   if([192,193,194,195,198,199,201,202,203,205,206,207].includes(marker)){
    if(n<7)throw Error('Invalid JPEG SOF');
    height=b.readUInt16BE(p+3);width=b.readUInt16BE(p+5);break;
   }
   p+=n;
  }
 }else if(mime==='image/webp'){
  const tag=b.toString('ascii',12,16);
  if(tag==='VP8X'&&b.length>=30){
   width=b.readUIntLE(24,3)+1;height=b.readUIntLE(27,3)+1;
  }else if(tag==='VP8L'&&b.length>=25&&b[20]===47){
   width=1+((b[21])|((b[22]&63)<<8));
   height=1+((b[22]>>6)|(b[23]<<2)|((b[24]&15)<<10));
  }else if(tag==='VP8 '&&b.length>=30&&b[23]===157&&b[24]===1&&b[25]===42){
   width=b.readUInt16LE(26)&0x3fff;height=b.readUInt16LE(28)&0x3fff;
  }
 }
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width>4096||height>4096||width*height>4194304)
  throw Error('Missing, malformed, or oversized image dimensions');
 return {width,height};
}

async function readImage(a){
 const x=await readWide(a.path,MAX_IMAGE);
 const mime=imageMime(x.p.rel,x.b);
 const dimension=dimensionsForImage(mime,x.b);
 return {file:x.p.rel,mimeType:mime,bytes:x.b.length,...dimension,base64:x.b.toString('base64')};
}
async function wideInfo(a){
 const x=await openPrivate(a.path,MAX_LARGE);
 try{return {file:x.p.rel,size:x.st.size,uid:x.st.uid,gid:x.st.gid,mode:(x.st.mode&0o777).toString(8),mtime:x.st.mtime.toISOString(),largeTextLimitBytes:MAX_LARGE}}
 finally{await x.h.close()}
}

async function main(){
 let raw='';
 for await(const b of process.stdin){raw+=b;if(raw.length>50000)throw Error('Request too long')}
 const m=JSON.parse(raw),a=m.args||{};let r;
 switch(m.op){
 case 'read_text_page':r=await readTextPage(a);break;
 case 'write_text_chunk':r=await writeTextChunk(a);break;
 case 'read_image':r=await readImage(a);break;
 case 'wide_file_info':r=await wideInfo(a);break;
 case 'create_directory':r=await makeDir(a.path);break;
 case 'move_file':r=await move(a.source,a.destination);break;
 case 'list_directory':r=await list(a.path,a.depth);break;
 case 'read_complete_file':r={content:await read(a.path)};break;
 case 'write_pdf':r=await PDF.make(a,check);break;
 case 'read_file':{let v=await read(a.path),ls=v.split('\n'),i=Number.isInteger(a.offset)?a.offset:0;i=i<0?Math.max(0,ls.length+i):i;r={file:valid(a.path).rel,totalLines:ls.length,text:ls.slice(i,i+Math.min(200,Math.max(0,Number.isInteger(a.length)?a.length:100))).join('\n')};break;}
 case 'write_file':r=await write(a.path,a.content,a.mode||'rewrite',a.mode!==undefined);break;
 case 'edit_block':{if(typeof a.old_string!=='string'||!a.old_string||typeof a.new_string!=='string')throw Error('Invalid edit');const s=await read(a.file_path),count=s.split(a.old_string).length-1,n=a.expected_replacements===undefined?1:a.expected_replacements;if(!Number.isInteger(n)||n<1||n>5||n!==count)throw Error('Exact match count mismatch');r={updated:await write(a.file_path,s.split(a.old_string).join(a.new_string),'rewrite',true),replacements:count};break;}
 case 'get_file_info':{const p=await check(a.path),st=await fsp.lstat(p.full);fileOK(st);r={file:p.rel,size:st.size,uid:st.uid,gid:st.gid,mode:(st.mode&0o777).toString(8),mtime:st.mtime.toISOString()};break;}
 case 'start_search':r=await search(a);break;
 case 'read_for_snapshot':r={source:await read(a.path),file:valid(a.path).rel};break;
 default:throw Error('Unsupported worker op');
 }
 process.stdout.write(JSON.stringify({ok:true,result:r})+'\n');
}
main().catch(e=>{process.stdout.write(JSON.stringify({ok:false,error:String(e.message||e)})+'\n');process.exitCode=1});