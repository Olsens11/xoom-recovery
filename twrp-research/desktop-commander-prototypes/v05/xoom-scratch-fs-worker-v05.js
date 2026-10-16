'use strict';
// Experimental Xoom v0.4 FS worker: launched under UID/GID2000, not root.
const fs=require('node:fs'), fsp=fs.promises, path=require('node:path'), crypto=require('node:crypto');
const ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch',UID=2000,MAX=32768,F=fs.constants;
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
 const p=await check(v),h=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
 try{
  fileOK(await h.stat());
  const b=Buffer.alloc(MAX+1);let i=0;
  while(i<b.length){let n=await h.read(b,i,b.length-i,i);if(!n.bytesRead)break;i+=n.bytesRead}
  if(i>MAX)throw Error('File grew above size limit');
  return utf(b.subarray(0,i));
 }finally{await h.close()}
}
async function write(v,data){
 const p=await check(v);
 if(typeof data!=='string'||Buffer.byteLength(data)>MAX||data.includes('\0')||utf(Buffer.from(data,'utf8'))!==data)throw Error('Invalid UTF8 or length');
 try{fileOK(await fsp.lstat(p.full))}catch(e){if(e.code!=='ENOENT')throw e}
 const tmp=path.join(path.dirname(p.full),'.v04-'+crypto.randomBytes(10).toString('hex'));
 const h=await fsp.open(tmp,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{await h.writeFile(data,'utf8');await h.sync()}finally{await h.close()}
 try{await fsp.rename(tmp,p.full)}catch(e){await fsp.unlink(tmp).catch(()=>{});throw e}
 return {file:p.rel,bytes:Buffer.byteLength(data)};
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
async function main(){
 let raw='';
 for await(const b of process.stdin){raw+=b;if(raw.length>50000)throw Error('Request too long')}
 const m=JSON.parse(raw),a=m.args||{};let r;
 switch(m.op){
 case 'create_directory':r=await makeDir(a.path);break;
 case 'move_file':r=await move(a.source,a.destination);break;
 case 'list_directory':r=await list(a.path,a.depth);break;
 case 'read_complete_file':r={content:await read(a.path)};break;
 case 'read_file':{let v=await read(a.path),ls=v.split('\n'),i=Number.isInteger(a.offset)?a.offset:0;i=i<0?Math.max(0,ls.length+i):i;r={file:valid(a.path).rel,totalLines:ls.length,text:ls.slice(i,i+Math.min(200,Math.max(0,Number.isInteger(a.length)?a.length:100))).join('\n')};break;}
 case 'write_file':r=await write(a.path,a.content);break;
 case 'edit_block':{if(typeof a.old_string!=='string'||!a.old_string||typeof a.new_string!=='string')throw Error('Invalid edit');const s=await read(a.file_path),count=s.split(a.old_string).length-1,n=a.expected_replacements===undefined?1:a.expected_replacements;if(!Number.isInteger(n)||n<1||n>5||n!==count)throw Error('Exact match count mismatch');r={updated:await write(a.file_path,s.split(a.old_string).join(a.new_string)),replacements:count};break;}
 case 'get_file_info':{const p=await check(a.path),st=await fsp.lstat(p.full);fileOK(st);r={file:p.rel,size:st.size,uid:st.uid,gid:st.gid,mode:(st.mode&0o777).toString(8),mtime:st.mtime.toISOString()};break;}
 case 'start_search':r=await search(a);break;
 case 'read_for_snapshot':r={source:await read(a.path),file:valid(a.path).rel};break;
 default:throw Error('Unsupported worker op');
 }
 process.stdout.write(JSON.stringify({ok:true,result:r})+'\n');
}
main().catch(e=>{process.stdout.write(JSON.stringify({ok:false,error:String(e.message||e)})+'\n');process.exitCode=1});