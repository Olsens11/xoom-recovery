'use strict';
process.umask(0o077); // All agent descendants create private files by default.
// Xoom Desktop Commander v0.4 RAM-only local candidate: standard search and project filesystem tools
// Explicitly limited to /tmp/xoom-dc-runtime-qa/dc-scratch.
const fs=require('node:fs');
const fsp=fs.promises;
const path=require('node:path');
const crypto=require('node:crypto');
const readline=require('node:readline');
const {spawn}=require('node:child_process');
const ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const UID=2000, GID=2000, MAX_FILE=32768, MAX_OUT=16384, MAX_SESSIONS=2, MAX_HISTORY=8, MAX_RUNTIME=9000;
const D='/tmp/xoom-dc-runtime-qa/debian24';
const UNPRIV_LOADER=D+'/uid-exec-test/ld-linux-armhf.so.3';
const DEBIAN_LIB=D+'/usr/lib/arm-linux-gnueabihf';
const NODE_BIN=D+'/usr/bin/node';
const DEV_LIMITS=Object.freeze({legacy:9000,run:90000,check:15000,repl:120000});
const SNAP_ROOT=D+'/execution-snapshots';
const stats={started:Date.now(),total:0,failed:0,counts:Object.create(null),history:[]};
function trackTool(name,ok,elapsedMs){
 const n=/^[a-z][a-z0-9_]{0,63}$/.test(name||'')?name:'unknown';
 stats.total++;if(!ok)stats.failed++;stats.counts[n]=(stats.counts[n]||0)+1;
 stats.history.push({name:n,status:ok?'success':'error',at:Date.now(),durationMs:Math.max(0,Math.min(600000,elapsedMs|0))});
 if(stats.history.length>32)stats.history.shift();
}
function owned(pid){if(!Number.isInteger(pid)||pid<=0||!sessions.has(pid))throw Error('Unknown or unowned process');return sessions.get(pid)}
function listManagedProcesses(){return {scope:'agent-owned-only',systemProcessEnumeration:false,processes:[...sessions.values()].slice(-16).map(x=>({pid:x.pid,command:x.command,uid:x.isScript?UID:0,running:x.running,interactive:x.isScript&&x.profile!=='check',profile:x.profile,elapsedMs:Date.now()-x.start,exitCode:x.exitCode,signal:x.signal}))}}
async function processInput(a){
 const x=owned(a.pid);
 if(!x.isScript)throw Error('Cannot send stdin to fixed root diagnostics');
 if(!x.running||!x.child?.stdin?.writable)throw Error('Owned process is not accepting stdin');
 if(typeof a.input!=='string'||Buffer.byteLength(a.input,'utf8')>4096||a.input.includes('\0')||Buffer.from(a.input,'utf8').toString('utf8')!==a.input||/[\x01-\x08\x0B-\x0C\x0E-\x1F\x7F]/.test(a.input))throw Error('Only bounded valid UTF-8 input (max 4096 bytes), no terminal controls');
 if(a.timeout_ms!==undefined&&(!Number.isInteger(a.timeout_ms)||a.timeout_ms<0||a.timeout_ms>3000))throw Error('timeout_ms must be 0–3000');
 await new Promise((resolve,reject)=>x.child.stdin.write(a.input,'utf8',e=>e?reject(Error('stdin write failed')):resolve()));
 return {pid:x.pid,stdinBytes:Buffer.byteLength(a.input,'utf8'),running:x.running,promptDetection:false,note:'Input sent only to agent-owned UID2000 Node script; use read_process_output for output'};
}
function killManaged(a){
 const x=owned(a.pid);
 if(!x.isScript)throw Error('kill_process restricted to UID2000 script sessions');
 const was=x.running,requested=was?killOwned(x,'SIGTERM'):false;
 return {pid:x.pid,terminationRequested:requested,alreadyExited:!was,signal:'SIGTERM',scope:'agent-owned-uid2000-only'};
}

const WORKER=D+'/xoom-scratch-fs-worker-v09.js';
const PDF_MODULE=D+'/xoom-pdf-maker-v06.js';
const config={telemetryEnabled:false,fileReadLineLimit:100,fileWriteLineLimit:50};
const uiCounters=Object.create(null);
const feedbackURL='https://tally.so/r/mKqoKg';
function updateConfig(a){
 if(!a||typeof a.key!=='string')throw Error('key is required');
 let next=a.value;
 switch(a.key){
  case 'telemetryEnabled':
   if(typeof next!=='boolean')throw Error('telemetryEnabled requires boolean');
   break;
  case 'fileReadLineLimit':
   if(!Number.isInteger(next)||next<1||next>200)throw Error('fileReadLineLimit range 1..200');
   break;
  case 'fileWriteLineLimit':
   if(!Number.isInteger(next)||next<1||next>100)throw Error('fileWriteLineLimit range 1..100');
   break;
  default:throw Error('Configuration key not supported in RAM-only recovery experiment; allowedDirectories, shell and blockedCommands are immutable');
 }
 config[a.key]=next;
 return {key:a.key,value:next,scope:'RAM-only',persistent:false};
}
function trackUi(a){
 if(!a||typeof a.event!=='string'||!/^[a-zA-Z][a-zA-Z0-9_.:-]{0,79}$/.test(a.event))throw Error('event must be a bounded identifier');
 if(a.component!==undefined&&(typeof a.component!=='string'||a.component.length>64||!/^[-_.a-zA-Z0-9]+$/.test(a.component)))throw Error('component must be a bounded identifier');
 if(a.params!==undefined){
  if(!a.params||typeof a.params!=='object'||Array.isArray(a.params)||Object.keys(a.params).length>10)throw Error('Invalid params');
  for(const [k,v] of Object.entries(a.params))
   if(k.length>40||!/^[-_.a-zA-Z0-9]+$/.test(k)||!(v===null||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v)||typeof v==='string'&&v.length<=80))throw Error('Invalid event param');
 }
 if(!config.telemetryEnabled)return {event:a.event,recorded:false,reason:'telemetry disabled; nothing sent'};
 uiCounters[a.event]=(uiCounters[a.event]||0)+1;
 return {event:a.event,recorded:true,scope:'local memory only',externalTelemetry:false};
}

const searches=new Map();
const MAX_SEARCHES=6;
function nested(v){return typeof v==='string'&&v.replace(ROOT+'/','').includes('/')}
async function workerJob(op,args={},onChild){
 const cmd=['--library-path',DEBIAN_LIB,NODE_BIN,'--max-old-space-size=48',
  '--permission','--allow-fs-read='+ROOT,'--allow-fs-read='+WORKER,'--allow-fs-read='+PDF_MODULE,'--allow-fs-write='+ROOT,WORKER];
 const child=spawn(UNPRIV_LOADER,cmd,{cwd:ROOT,uid:UID,gid:GID,detached:false,
  env:{HOME:ROOT,TMPDIR:ROOT,PATH:'/sbin:/bin'},stdio:['pipe','pipe','pipe']});
 if(onChild)onChild(child);
 return await new Promise((resolve,reject)=>{
  let stdout='',stderr='',complete=false;
  const done=(err,val)=>{if(complete)return;complete=true;clearTimeout(timer);err?reject(err):resolve(val)};
  const timer=setTimeout(()=>{child.kill('SIGKILL');done(Error('Worker timeout'))},6000);
  child.on('error',e=>done(e));
  child.stdout.on('data',buf=>{stdout+=buf.toString();if(stdout.length>110000){child.kill('SIGKILL');done(Error('Worker response exceeded cap'))}});
  child.stderr.on('data',buf=>{stderr=(stderr+buf.toString()).slice(-1500)});
  child.on('close',()=>{
   if(complete)return;
   try{let data=JSON.parse(stdout.trim());if(data.ok)done(null,data.result);
    else done(Error(data.error||'Worker rejected call'))}
   catch(e){done(Error('Worker failed: '+String(e.message||e)+' '+stderr.slice(0,180)))}
  });
  child.stdin.on('error',()=>{});
  child.stdin.end(JSON.stringify({op,args}));
 });
}

const sessions=new Map();
const F=fs.constants;
function rpc(id,result){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,result})+'\n')}
function error(id,code,message){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,error:{code,message}})+'\n')}
function textResult(value,isError=false){
 return {content:[{type:'text',text:typeof value==='string'?value:JSON.stringify(value)}],isError};
}
function filename(value){
 if(typeof value!=='string')throw Error('File path must be a string');
 let rel=value.startsWith(ROOT+'/')?value.slice(ROOT.length+1):value;
 if(!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/.test(rel) || rel==='..')throw Error('Only simple filenames within scratch directory are allowed');
 return {name:rel,full:path.join(ROOT,rel)};
}
async function readBoundedFileHandle(fh){
 const buf=Buffer.alloc(MAX_FILE+1);
 let bytes=0;
 while(bytes<buf.length){
  const n=await fh.read(buf,bytes,buf.length-bytes,bytes);
  if(n.bytesRead===0)break;
  bytes+=n.bytesRead;
 }
 if(bytes>MAX_FILE)throw Error('File exceeded 32 KiB limit while reading');
 return buf.subarray(0,bytes);
}
function decodeText(buf){
 if(buf.includes(0))throw Error('Binary or NUL file rejected');
 return new TextDecoder('utf-8',{fatal:true}).decode(buf);
}
async function safeRead(value){
 const p=filename(value);
 const fh=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
 try{
  let st=await fh.stat();if(!st.isFile()||st.uid!==UID||st.gid!==GID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>MAX_FILE)throw Error('Only private owned regular text files up to 32 KiB are supported');
  const buffer=await readBoundedFileHandle(fh);
  return decodeText(buffer);
 }finally{await fh.close()}
}
async function safeWrite(value,content){
 let p=filename(value);if(typeof content!=='string'||Buffer.byteLength(content)>MAX_FILE||content.includes('\0')||decodeText(Buffer.from(content,'utf8'))!==content)throw Error('Text content must be valid UTF-8 without NUL, at most 32 KiB');
 // No symlink targets; atomic rename replaces a single file or symlink rather than following it.
 try{const prev=await fsp.lstat(p.full);if(!prev.isFile()||prev.uid!==UID||prev.gid!==GID||(prev.mode&0o777)!==0o600||prev.nlink!==1)throw Error('Target must be single-link UID2000 mode0600 regular file')}catch(e){if(e.code!=='ENOENT')throw e}
 const temp=path.join(ROOT,'.tmp-'+crypto.randomBytes(8).toString('hex'));
 let fh=await fsp.open(temp,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{
  await fh.writeFile(content,'utf8');
  await fh.chown(UID,GID);
  await fh.sync();
 }finally{await fh.close()}
 try{await fsp.rename(temp,p.full)}catch(e){await fsp.unlink(temp).catch(()=>{});throw e}
 return {file:p.name,bytes:Buffer.byteLength(content)};
}
function killOwned(session,signal='SIGTERM'){
 if(!session.running)return false;
 // All permitted commands are direct, fixed BusyBox applets; there are no shell children.
 return session.child.kill(signal);
}
function trimHistory(){
 const completed=[...sessions.values()].filter(s=>!s.running);
 while(completed.length>MAX_HISTORY){
  const oldest=completed.shift();
  sessions.delete(oldest.pid);
 }
}
async function stageScript(name){
 let source;
 if(nested(name)){source=(await workerJob('read_for_snapshot',{path:name})).source;}
 else{
 const p=filename(name);
 const fh=await fsp.open(p.full,F.O_RDONLY|F.O_NOFOLLOW);
 try {
  const st=await fh.stat();
  if(!st.isFile()||st.uid!==UID||st.gid!==GID||(st.mode&0o777)!==0o600||st.nlink!==1||st.size>MAX_FILE)
   throw Error('Script requires a single-link regular file, uid/gid 2000, mode 0600, <=32 KiB');
  const buf=await readBoundedFileHandle(fh);
  source=decodeText(buf);
 }finally{await fh.close()}
 }
 try {await fsp.mkdir(SNAP_ROOT,{mode:0o755})}catch(e){if(e.code!=='EEXIST')throw e}
 const rootSt=await fsp.lstat(SNAP_ROOT);
 if(!rootSt.isDirectory()||rootSt.uid!==0||(rootSt.mode&0o777)!==0o755)throw Error('Execution snapshot directory needs root owner mode 0755');
 const full=path.join(SNAP_ROOT,'snapshot-'+crypto.randomBytes(16).toString('hex')+'.js');
 const out=await fsp.open(full,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{await out.writeFile(source,'utf8');await out.chown(0,GID);await out.chmod(0o640);await out.sync()}catch(e){await fsp.unlink(full).catch(()=>{});throw e}finally{await out.close()}
 return {full,sourceHash:crypto.createHash('sha256').update(source).digest('hex')};
}
function launch(command,script=null,profile='legacy'){
 if([...sessions.values()].filter(s=>s.running).length>=MAX_SESSIONS)throw Error('At most two active owned sessions allowed');
 if(typeof command!=='string')throw Error('A command is required');
 if(!Object.hasOwn(DEV_LIMITS,profile))throw Error('Unknown execution profile');
 const allowed={'diag date':['date','-u'],'diag uptime':['uptime'],'diag identity':['id'],'diag memory':['free','-m'],'diag wait':['sleep','8']};
 const repl=profile==='repl',check=profile==='check';
 const isScript=script!==null||repl;
 if(!isScript&&!Object.hasOwn(allowed,command))throw Error('Only owned Node development profiles or fixed diagnostics supported; no root shell');
 if(isScript&&profile==='legacy'&&repl)throw Error('Invalid profile');
 const exe=isScript?UNPRIV_LOADER:'/sbin/busybox';
 const argv=isScript?[
  '--library-path',DEBIAN_LIB,NODE_BIN,'--max-old-space-size='+ (profile==='legacy'?48:64),
  '--permission','--allow-fs-read='+ROOT,
  ...(script?['--allow-fs-read='+script.full]:[]),
  ...(check?[]:['--allow-fs-write='+ROOT]),
  ...(repl?['--interactive']:(check?['--check',script.full]:[script.full]))
 ]:allowed[command];
 const options={cwd:ROOT,detached:true,
  env:{PATH:'/sbin:/bin:/system/bin',HOME:ROOT,TMPDIR:ROOT,TERM:'dumb',NO_COLOR:'1'},stdio:['pipe','pipe','pipe']};
 if(isScript){options.uid=UID;options.gid=GID;}
 const child=spawn(exe,argv,options);
 const s={pid:child.pid,command,profile,output:'',exitCode:null,signal:null,running:true,start:Date.now(),child,timedOut:false,outputTruncated:false,sourceHash:script?.sourceHash,isScript,readCursor:0,outputBaseLine:0};
 if(!Number.isInteger(s.pid)||s.pid<=0){child.on('error',()=>{});if(script)fsp.unlink(script.full).catch(()=>{});throw Error('Could not spawn');
 }
 sessions.set(s.pid,s);
 const capture=b=>{
  s.output+=b.toString('utf8');
  if(s.output.length>MAX_OUT){
   s.outputTruncated=true;
   const minCut=s.output.length-MAX_OUT;
   const boundary=s.output.indexOf('\n',minCut);
   if(boundary>=0){
    const removed=s.output.slice(0,boundary+1);
    s.outputBaseLine+=(removed.match(/\n/g)||[]).length;
    s.output=s.output.slice(boundary+1);
   }else{s.output=s.output.slice(-MAX_OUT);s.outputBaseLine++}
   s.readCursor=Math.max(s.readCursor,s.outputBaseLine);
  }
 };
 child.stdout.on('data',capture);child.stderr.on('data',capture);
 child.on('error',e=>{capture('spawn failure: '+e.message);s.running=false});
 child.on('close',(code,signal)=>{
  s.running=false;s.exitCode=code;s.signal=signal;
  clearTimeout(s.timer);clearTimeout(s.killTimer);
  if(script)fsp.unlink(script.full).catch(()=>{});
  trimHistory();
 });
 const runtimeMs= isScript?DEV_LIMITS[profile]:MAX_RUNTIME;
 s.timer=setTimeout(()=>{if(s.running){
  s.timedOut=true;capture('\n['+runtimeMs+'ms '+profile+' command limit reached]\n');
  killOwned(s,'SIGTERM');
  s.killTimer=setTimeout(()=>{if(s.running)killOwned(s,'SIGKILL')},1000);
 }},runtimeMs);
 return {pid:s.pid,command,profile,uid:isScript?UID:0,gid:isScript?GID:0,sourceSha256:script?.sourceHash,
  limitMs:runtimeMs,interactive:repl,policy:isScript?'UID2000, Node permission-bound scratch, no child processes or native shell':'Fixed root read-only BusyBox diagnostic',
  note:repl?'Node REPL (not OS shell), accepts bounded stdin via interact_with_process':check?'Immutable source syntax check':isScript?'Unprivileged immutable source snapshot':'Fixed diagnostic'};
}
const definitions=[
 ['get_config','Read experiment tool policy and scratch directory',{type:'object',properties:{}}],
 ['set_config_value','Update only three bounded RAM-only configuration preferences; filesystem and shell policy immutable',{type:'object',properties:{key:{type:'string'},value:{}},required:['key','value']}],
 ['write_pdf','Create a private ASCII Markdown PDF in scratch; new-PDF creation only, ≤8 pages',{type:'object',properties:{path:{type:'string'},content:{type:'string'},outputPath:{type:'string'},options:{type:'object'}},required:['path','content']}],
 ['give_feedback_to_desktop_commander','Return the official Desktop Commander feedback URL for user to open; cannot open browser in TWRP',{type:'object',properties:{}}],
 ['track_ui_event','Validate UI event; default disabled, opt-in RAM-only aggregate counters',{type:'object',properties:{event:{type:'string'},component:{type:'string'},params:{type:'object'}},required:['event']}],
 ['read_multiple_files','Read up to eight private scratch UTF-8 files independently',{type:'object',properties:{paths:{type:'array',items:{type:'string'},minItems:1,maxItems:8}},required:['paths']}],
 ['interact_with_process','Send bounded text to agent-owned UID2000 script stdin only, no shell',{type:'object',properties:{pid:{type:'integer'},input:{type:'string'},timeout_ms:{type:'integer'},wait_for_prompt:{type:'boolean'},verbose_timing:{type:'boolean'}},required:['pid','input']}],
 ['list_processes','List only processes started and owned by this experimental agent',{type:'object',properties:{}}],
 ['kill_process','Terminate only agent-owned UID2000 scripts (not root diagnostics or OS processes)',{type:'object',properties:{pid:{type:'integer'}},required:['pid']}],
 ['get_usage_stats','RAM-only aggregate tool usage counts, no user data',{type:'object',properties:{}}],
 ['get_recent_tool_calls','RAM-only bounded names/status history; no arguments or command content',{type:'object',properties:{maxResults:{type:'integer'},toolName:{type:'string'},since:{type:'string'}}}],
 ['create_directory','Create bounded nested scratch project directory (UID2000 worker)',{type:'object',properties:{path:{type:'string'}},required:['path']}],
 ['move_file','Rename/move owned scratch files or directories; no overwrite',{type:'object',properties:{source:{type:'string'},destination:{type:'string'}},required:['source','destination']}],
 ['start_search','Start standard filename or content search, bounded to scratch',{type:'object',properties:{path:{type:'string'},pattern:{type:'string'},searchType:{type:'string',enum:['files','content']},filePattern:{type:'string'},ignoreCase:{type:'boolean'},maxResults:{type:'integer'},contextLines:{type:'integer'},literalSearch:{type:'boolean'},includeHidden:{type:'boolean'},timeout_ms:{type:'integer'},earlyTermination:{type:'boolean'}},required:['path','pattern']}],
 ['get_more_search_results','Read search results by session ID with pagination',{type:'object',properties:{sessionId:{type:'string'},offset:{type:'integer'},length:{type:'integer'}},required:['sessionId']}],
 ['stop_search','Cancel owned search session',{type:'object',properties:{sessionId:{type:'string'}},required:['sessionId']}],
 ['list_searches','List bounded search sessions',{type:'object',properties:{}}],
 ['list_directory','List only the bounded RAM scratch directory',{type:'object',properties:{path:{type:'string'},depth:{type:'integer',minimum:1,maximum:3}}}],
 ['get_file_info','Read metadata for a scratch regular file',{type:'object',properties:{path:{type:'string'}},required:['path']}],
 ['read_file','Page private UTF-8 source files up to 256KiB (16KiB/200 lines each) or return verified PNG/JPEG/GIF/WebP as native MCP image blocks',{type:'object',properties:{path:{type:'string'},offset:{type:'integer'},length:{type:'integer'}},required:['path']}],
 ['write_file','Atomically write/append 32KiB UTF-8 chunks in private files up to 256KiB total; existing nonempty files require explicit mode',{type:'object',properties:{path:{type:'string'},content:{type:'string'},mode:{type:'string',enum:['rewrite','append']}},required:['path','content']}],
 ['edit_block','Replace an exact unique string in a scratch file',{type:'object',properties:{file_path:{type:'string'},old_string:{type:'string'},new_string:{type:'string'},expected_replacements:{type:'integer'}},required:['file_path','old_string','new_string']}],
 ['start_process','Run fixed diagnostics, legacy JS, dev run/check JS, or bounded UID2000 dev repl; no native shell',{type:'object',properties:{command:{type:'string'},timeout_ms:{type:'integer'}},required:['command']}],
 ['read_process_output','Read line-paginated owned process output; offset=0 incremental, positive absolute, negative tail',{type:'object',properties:{pid:{type:'integer'},offset:{type:'integer'},length:{type:'integer'},timeout_ms:{type:'integer'}},required:['pid']}],
 ['list_sessions','Show only agent-launched diagnostic sessions',{type:'object',properties:{}}],
 ['force_terminate','Terminate only a matching owned scratch test session',{type:'object',properties:{pid:{type:'integer'}},required:['pid']}]
].map(([name,description,inputSchema])=>{
 const readOnly=new Set(['get_config','read_file','read_multiple_files','list_directory','get_file_info','start_search','get_more_search_results','list_searches','read_process_output','list_sessions','list_processes','get_usage_stats','get_recent_tool_calls']);
 const destructive=new Set(['set_config_value','write_file','write_pdf','move_file','edit_block','start_process','interact_with_process','force_terminate','kill_process']);
 const openWorld=new Set(['read_file','start_process','interact_with_process','give_feedback_to_desktop_commander']);
 return {name,description,inputSchema,annotations:{
  title:name.replaceAll('_',' '),
  readOnlyHint:readOnly.has(name),
  destructiveHint:destructive.has(name),
  openWorldHint:openWorld.has(name)
 }};
});
async function call(name,arg={}){
 switch(name){
  case 'get_config':return {version:'xoom-scratch-dev-v0.9-LOCAL-ONLY',root:ROOT,allowedDirectories:[ROOT],tools:definitions.map(x=>x.name),scratchFileOwnerUid:UID,commands:'diag date | diag uptime | diag identity | diag memory | diag wait | run NAME.js (legacy 9s) | dev check NAME.js (15s) | dev run NAME.js (90s) | dev repl (120s, interactive UID2000 Node, not a native shell)',maxFileBytes:MAX_FILE,maxOutputChars:MAX_OUT,maxRuntimeMs:MAX_RUNTIME,extendedTextLimitBytes:262144,writeChunkLimitBytes:32768,imageReadLimitBytes:61440,supportsMcpImageBlocks:true,developmentProfiles:{runMs:DEV_LIMITS.run,checkMs:DEV_LIMITS.check,replMs:DEV_LIMITS.repl,uid:UID,nodePermissionMode:true,rootShell:false},nestedProjectDepth:3,searchCap:120,managedProcessOnly:true,toolTelemetryMemoryOnly:true,preferences:{...config},feedbackURL,externalTelemetry:false,rootShellDisabled:true,networkRestricted:false,securityNote:'Node permissions are defense in depth, not an OS sandbox; outbound networking is not restricted',persistent:false};
  case 'set_config_value':return updateConfig(arg);
  case 'write_pdf':return workerJob('write_pdf',arg);
  case 'give_feedback_to_desktop_commander':return {url:feedbackURL,openedBrowser:false,message:'Open this official feedback URL in your own browser; recovery has no browser'};
  case 'track_ui_event':return trackUi(arg);
  case 'read_multiple_files':{
   if(!Array.isArray(arg.paths)||arg.paths.length<1||arg.paths.length>8||arg.paths.some(p=>typeof p!=='string'))throw Error('paths must have 1–8 strings');
   const results=[];let bytes=0;
   for(const p of arg.paths){
    try{
     const response=await workerJob('read_complete_file',{path:p});
     const body=response.content;
     if(typeof body!=='string')throw Error('Non-UTF8 file');
     const count=Buffer.byteLength(body,'utf8');
     if(bytes+count>65536){results.push({path:p,ok:false,error:'AGGREGATE_LIMIT'});continue}
     bytes+=count;results.push({path:p,ok:true,bytes:count,content:body});
    }catch(e){results.push({path:p,ok:false,error:'READ_DENIED_OR_FAILED'})}
   }
   return {files:results,requested:arg.paths.length,succeeded:results.filter(x=>x.ok).length,failed:results.filter(x=>!x.ok).length,totalBytes:bytes};
  }
  case 'interact_with_process':return processInput(arg);
  case 'list_processes':return listManagedProcesses();
  case 'kill_process':return killManaged(arg);
  case 'get_usage_stats':return {scope:'RAM-only experimental agent',since:stats.started,totalToolCalls:stats.total,successfulCalls:stats.total-stats.failed,failedCalls:stats.failed,toolCounts:{...stats.counts},historyLimit:32,uiEventCounts:{...uiCounters},externalTelemetry:false};
  case 'get_recent_tool_calls':{
   const max=arg.maxResults===undefined?20:arg.maxResults;
   if(!Number.isInteger(max)||max<1||max>1000)throw Error('maxResults must be integer 1..1000');
   const calls=stats.history.filter(x=>(!arg.toolName||x.name===arg.toolName)&&(!arg.since||new Date(x.at)>=new Date(arg.since))).slice(-Math.min(32,max)).reverse();
   return {calls,count:calls.length,recordsExcludeArguments:true};
  }
  case 'list_directory':return workerJob('list_directory',arg);
  case 'create_directory':return workerJob('create_directory',arg);
  case 'move_file':return workerJob('move_file',arg);
  case 'start_search':{
   if(arg.includeHidden===true)throw Error('Search of hidden files is not supported in bounded v0.4');
   if(arg.earlyTermination===true)throw Error('Early termination on filename match is not implemented in v0.4');
   if(typeof arg.pattern!=='string'||!arg.pattern||arg.pattern.length>128)throw Error('Pattern must be 1-128 chars');
   if(searches.size>=MAX_SEARCHES){
    const done=[...searches.values()].find(x=>!x.running);
    if(!done)throw Error('Too many search sessions'); searches.delete(done.sessionId);
   }
   const sessionId=crypto.randomUUID(),s={sessionId,searchType:arg.searchType||'files',pattern:arg.pattern,running:true,complete:false,results:[],scanned:0,truncated:false,error:null,started:Date.now(),child:null};
   searches.set(sessionId,s);
   workerJob('start_search',arg,c=>s.child=c).then(v=>{
    s.results=v.results;s.scanned=v.scanned;s.truncated=v.truncated;
   }).catch(e=>{if(!s.stopped)s.error=e.message}).finally(()=>{s.running=false;s.complete=true});
   return {sessionId,searchType:s.searchType,pattern:s.pattern,status:'running',root:ROOT};
  }
  case 'get_more_search_results':{
   const s=searches.get(arg.sessionId);if(!s)throw Error('Unknown search session');
   const len=Math.min(100,Math.max(1,Number.isInteger(arg.length)?arg.length:100));
   let off=Number.isInteger(arg.offset)?arg.offset:0;
   if(off<0)off=Math.max(0,s.results.length+off);
   return {sessionId:s.sessionId,status:s.running?'running':s.stopped?'stopped':s.error?'error':'completed',complete:s.complete,results:s.results.slice(off,off+len),offset:off,totalResults:s.results.length,scanned:s.scanned,truncated:s.truncated,error:s.error};
  }
  case 'stop_search':{
   const s=searches.get(arg.sessionId);if(!s)throw Error('Unknown search session');
   const was=s.running;
   if(was){s.stopped=true;if(s.child)s.child.kill('SIGTERM')}
   return {sessionId:s.sessionId,terminationRequested:was,status:was?'stopped':s.error?'error':'completed'};
  }
  case 'list_searches':return {searches:[...searches.values()].map(s=>({sessionId:s.sessionId,searchType:s.searchType,pattern:s.pattern,running:s.running,complete:s.complete,totalResults:s.results.length,elapsedMs:Date.now()-s.started,error:s.error}))};
  case 'read_file':{
   const requestedLength=arg.length===undefined?config.fileReadLineLimit:arg.length;
   if(!Number.isInteger(requestedLength)||requestedLength<0||requestedLength>200)throw Error('Read length requires 0..200 lines');
   if(/\.(png|jpe?g|gif|webp)$/i.test(arg.path||'')){
    const image=await workerJob('read_image',{path:arg.path});
    return {__mcpImage:true,...image};
   }
   return workerJob('read_text_page',{path:arg.path,offset:arg.offset,length:requestedLength});
  }
  case 'get_file_info':return workerJob('wide_file_info',arg);
  case 'write_file':{
   if(arg.mode!==undefined&&!['rewrite','append'].includes(arg.mode))throw Error('mode must be rewrite or append');
   if(typeof arg.content!=='string')throw Error('Text content required');
   const result=await workerJob('write_text_chunk',arg);
   const lines=arg.content.split('\n').length;
   return {...result,writeLineCount:lines,writeLineLimit:config.fileWriteLineLimit,overWriteLineLimit:lines>config.fileWriteLineLimit};
  }
  case 'edit_block':{
   if(nested(arg.file_path))return workerJob('edit_block',arg);
   if(typeof arg.old_string!=='string'||arg.old_string.length===0||typeof arg.new_string!=='string')throw Error('Invalid replacement');
   let data=await safeRead(arg.file_path);
   const count=data.split(arg.old_string).length-1;
   const expect=arg.expected_replacements===undefined?1:arg.expected_replacements;
   if(!Number.isInteger(expect)||expect<1||expect>5||count!==expect)throw Error('Exact match count mismatch: found '+count+' expected '+expect);
   return {updated:await safeWrite(arg.file_path,data.split(arg.old_string).join(arg.new_string)),replacements:count};
  }
  case 'start_process':{
   if(arg.command==='dev repl')return launch(arg.command,null,'repl');
   if(typeof arg.command==='string'&&/^(dev run |dev check )/.test(arg.command)){
    const check=arg.command.startsWith('dev check ');
    const name=arg.command.slice(check?10:8);
    if(!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,59}(\/[A-Za-z0-9][A-Za-z0-9_.-]{0,59}){0,3}\.js$/.test(name))
     throw Error('Development profile requires a bounded scratch .js file path');
    const script=await stageScript(name);
    try{return launch(arg.command,script,check?'check':'run')}
    catch(e){await fsp.unlink(script.full).catch(()=>{});throw e}
   }
   if(typeof arg.command==='string'&&arg.command.startsWith('run ')){
    const scriptName=arg.command.slice(4);
    if(!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,59}(\/[A-Za-z0-9][A-Za-z0-9_.-]{0,59}){0,3}\.js$/.test(scriptName))throw Error('Only bounded scratch NAME.js or project/NAME.js is supported');
    const script=await stageScript(scriptName);
    try{return launch(arg.command,script)}catch(e){await fsp.unlink(script.full).catch(()=>{});throw e}
   }
   return launch(arg.command);
  }
  case 'read_process_output':{
   const s=owned(arg.pid);
   const offset=arg.offset===undefined?0:arg.offset;
   const length=arg.length===undefined?config.fileReadLineLimit:arg.length;
   const wait=arg.timeout_ms===undefined?0:arg.timeout_ms;
   if(!Number.isInteger(offset)||!Number.isInteger(length)||length<1||length>200||!Number.isInteger(wait)||wait<0||wait>3000)
    throw Error('offset integer; length 1–200 lines; timeout_ms 0–3000');
   function contents(){
    let lines=s.output.split(/\r?\n/);
    if(s.output.endsWith('\n')||s.running)lines.pop();
    if(!s.output)lines=[];
    return lines;
   }
   if(offset===0&&wait>0&&s.running){
    const until=Date.now()+wait;
    while(s.running&&s.outputBaseLine+contents().length<=s.readCursor&&Date.now()<until)
     await new Promise(resolve=>setTimeout(resolve,Math.min(50,until-Date.now())));
   }
   const lines=contents();
   const total=s.outputBaseLine+lines.length;
   const from=offset===0?Math.max(s.readCursor,s.outputBaseLine):offset<0?Math.max(s.outputBaseLine,total+offset):Math.max(s.outputBaseLine,offset);
   const relative=Math.max(0,from-s.outputBaseLine);
   const selected=lines.slice(relative,relative+length);
   const next=from+selected.length;
   if(offset===0)s.readCursor=Math.max(s.readCursor,next);
   return {pid:s.pid,running:s.running,exitCode:s.exitCode,signal:s.signal,timedOut:s.timedOut,outputTruncated:s.outputTruncated,
    output:selected.join('\n'),fromLine:from,totalLines:total,nextLine:next,remainingLines:Math.max(0,total-next),incremental:offset===0,
    profile:s.profile,waitingForInput:s.profile==='repl'&&s.running&&/>\s*$/.test(s.output),
    promptPreview:s.profile==='repl'&&s.running?s.output.slice(-60).replace(/[\x00-\x08\x0b-\x1f\x7f]/g,''):undefined};
  }
  case 'list_sessions':return {sessions:[...sessions.values()].map(s=>({pid:s.pid,running:s.running,command:s.command,profile:s.profile,interactive:s.profile==='repl',elapsedMs:Date.now()-s.start,exitCode:s.exitCode,timedOut:s.timedOut}))};
  case 'force_terminate':{
   const s=sessions.get(arg.pid);if(!s)throw Error('Unknown or unowned session');
   if(s.running)killOwned(s,'SIGTERM');
   return {pid:s.pid,terminationRequested:s.running};
  }
  default:throw Error('Unknown tool '+name)
 }
}
(async()=>{
 const st=await fsp.lstat(ROOT);
 if(!st.isDirectory()||st.uid!==UID||st.gid!==GID||(st.mode&0o777)!==0o700)throw Error('Scratch directory must be owned by uid/gid 2000 with mode 0700');
 console.error('XOOM_SCRATCH_MCP_READY',ROOT);
 const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
 rl.on('line',async line=>{
  let req;try{req=JSON.parse(line)}catch{error(null,-32700,'Malformed JSON');return}
  if(!req||req.jsonrpc!=='2.0'){error(req?.id??null,-32600,'Invalid request');return}
  if(!Object.hasOwn(req,'id'))return;
  try{
   if(req.method==='initialize'){rpc(req.id,{protocolVersion:req.params?.protocolVersion||'2025-06-18',capabilities:{tools:{listChanged:false}},serverInfo:{name:'xoom-scratch-dev',version:'0.9.0-local'}});return}
   if(req.method==='ping'){rpc(req.id,{});return}
   if(req.method==='tools/list'){rpc(req.id,{tools:definitions});return}
   if(req.method!=='tools/call'){error(req.id,-32601,'Method not found');return}
   const start=Date.now(),toolName=req.params?.name;
   try{
    const data=await call(toolName,req.params?.arguments||{});
    trackTool(toolName,true,Date.now()-start);
    const reply=data?.__mcpImage?{
      content:[
       {type:'text',text:'Image file: '+data.file+' ('+data.mimeType+', '+data.bytes+' bytes)'},
       {type:'image',data:data.base64,mimeType:data.mimeType}
      ],
      isError:false,
      structuredContent:{fileName:data.file,filePath:ROOT+'/'+data.file,fileType:'image',mimeType:data.mimeType,bytes:data.bytes,width:data.width,height:data.height}
    }:textResult(data);
    if(toolName==='get_config')reply.structuredContent={
     config:data,
     entries:Object.entries(config).map(([key,value])=>({key,value,valueType:typeof value,editable:true})),
     uiHints:{availableShells:[]}
    };
    rpc(req.id,reply);
   }catch(e){trackTool(toolName,false,Date.now()-start);throw e}
  }catch(e){
   rpc(req.id,textResult({error:String(e?.message||e)},true));
  }
 });
 rl.on('close',()=>{
  for(const s of sessions.values())if(s.running)killOwned(s,'SIGTERM');
 });
})().catch(e=>{console.error('BOOT_FAIL',e.stack);process.exitCode=1});