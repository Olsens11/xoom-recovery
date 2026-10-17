'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v12-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const init=await request('initialize',{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'xoom-hardware-qa',version:'1.0'}});
 eq(init.result.serverInfo.name==='xoom-scratch-dev','MCP_INITIALIZE');
 const listed=await request('tools/list',{});eq(listed.result.tools.length===26,'TOOLS_LIST_22');
 let r=await tool('get_config',{});eq(r.value.rootShellDisabled&&r.value.commands.includes('diag date'),'CONFIG_SCOPE');
 r=await tool('list_directory',{path:ROOT});eq(Array.isArray(r.value.entries),'DIRECTORY_LIST');
 r=await tool('write_file',{mode:'rewrite',path:'smoke.txt',content:'Original test value\n'});eq(!r.isError,'WRITE_FILE');
 r=await tool('get_file_info',{path:'smoke.txt'});eq(r.value.uid===2000&&r.value.mode==='600','FILE_INFO_OWNERSHIP');
 r=await tool('read_file',{path:'smoke.txt'});eq(r.value.text.includes('Original'),'READ_FILE');
 r=await tool('edit_block',{file_path:'smoke.txt',old_string:'Original',new_string:'Edited on actual Xoom'});
 eq(!r.isError&&r.value.replacements===1,'EDIT_BLOCK');
 r=await tool('read_file',{path:'smoke.txt'});eq(r.value.text.includes('Edited on actual Xoom'),'READ_AFTER_EDIT');
 r=await tool('read_file',{path:'/etc/passwd'});eq(r.isError,'OUTSIDE_SCRATCH_REJECTED');
 r=await tool('start_process',{command:'run smoke.sh'});eq(r.isError,'ARBITRARY_SCRIPT_REJECTED');
 r=await tool('start_process',{command:'diag identity'});eq(!r.isError&&r.value.command==='diag identity','STATIC_DIAGNOSTIC_SPAWN');
 let pid=r.value.pid;
 for(let i=0;i<14;i++){
  await new Promise(r=>setTimeout(r,350));
  r=await tool('read_process_output',{pid});
  if(r.value.output.includes('uid=0(root)')||!r.value.running)break;
 }
 console.log('DIAGNOSTIC_RAW_RESULT',JSON.stringify(r));
 eq(r.value.output.includes('uid=0(root)'),'STATIC_DIAGNOSTIC_OUTPUT');
 r=await tool('list_sessions',{});eq(r.value.sessions.some(a=>a.pid===pid),'SESSION_LIST');
 r=await tool('force_terminate',{pid:987654});eq(r.isError,'UNOWNED_PID_REJECTED');
 r=await tool('start_process',{command:'diag wait'});
 eq(!r.isError&&Number.isInteger(r.value.pid),'LONG_TEST_STARTED');
 const waitPid=r.value.pid;
 r=await tool('force_terminate',{pid:waitPid});
 eq(!r.isError&&r.value.terminationRequested,'OWNED_TERMINATE_REQUESTED');
 for(let i=0;i<16;i++){
  await new Promise(resolve=>setTimeout(resolve,250));
  r=await tool('read_process_output',{pid:waitPid});
  if(!r.value.running)break;
 }
 console.log('TERMINATE_RESULT',JSON.stringify(r.value));
 eq(!r.value.running && r.value.signal==='SIGTERM','OWNED_TERMINATE_CONFIRMED');
 for(let i=0;i<4;i++){
  r=await tool('start_process',{command:'diag uptime'});
  eq(!r.isError,'NEXT_TEST_LAUNCH_'+i);
  const probe=r.value.pid;
  for(let j=0;j<12;j++){
   await new Promise(resolve=>setTimeout(resolve,220));
   r=await tool('read_process_output',{pid:probe});
   if(!r.value.running)break;
  }
  eq(r.value.exitCode===0,'NEXT_TEST_EXIT_'+i);
 }
 r=await tool('list_sessions',{});
 eq(r.value.sessions.length<=8,'SESSION_HISTORY_BOUNDED');
 console.log('XOOM_V03_REGRESSION_V02_FEATURES_PASS');

 eq((await tool('start_process',{command:'run ../outside.js'})).isError,'V03_TRAVERSAL_REJECTED');
 const scriptSrc="'use strict';\nconst fs=require('node:fs');\nconst cp=require('node:child_process');\nconst root='/tmp/xoom-dc-runtime-qa/dc-scratch';\nconst phase='PHASE_ALPHA';\nfunction verdict(fn){try{fn();return 'UNEXPECTED_ACCESS';}catch(e){return e.code||e.name;}}\nconst outside=verdict(()=>fs.readFileSync('/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v01.js'));\nconst subprocess=verdict(()=>cp.spawnSync('/sbin/busybox',['id']));\nfs.writeFileSync(root+'/v08-script-output.txt',phase+'\\n');\nconsole.log('V03_CHILD_RESULT',JSON.stringify({phase,uid:process.getuid(),gid:process.getgid(),groups:process.getgroups(),outside,subprocess}));";
 r=await tool('write_file',{mode:'rewrite',path:'v03-scratch-run.js',content:scriptSrc});
 eq(!r.isError,'V03_SCRIPT_WRITTEN_VIA_MCP');
 r=await tool('get_file_info',{path:'v03-scratch-run.js'});
 eq(r.value.uid===2000&&r.value.gid===2000&&r.value.mode==='600','V03_SCRIPT_OWNER_MODE');
 async function runScript(command,waits=25,interval=300){
  let k=await tool('start_process',{command});
  eq(!k.isError&&k.value.uid===2000&&k.value.gid===2000,'V03_UNPRIV_START');
  const p=k.value.pid;
  for(let i=0;i<waits;i++){
   await new Promise(resolve=>setTimeout(resolve,interval));
   k=await tool('read_process_output',{pid:p});
   if(!k.value.running)break;
  }
  return k.value;
 }
 let sr=await runScript('run v03-scratch-run.js');
 console.log('V03_SCRIPT_FIRST_RESULT',JSON.stringify(sr));
 eq(sr.exitCode===0&&sr.output.includes('V03_CHILD_RESULT'),'V03_SCRIPT_OUTPUT_EXIT');
 eq(sr.output.includes('"uid":2000')&&sr.output.includes('"gid":2000')&&sr.output.includes('"groups":[2000]'),'V03_UNPRIV_IDENTITY');
 eq(sr.output.includes('"outside":"ERR_ACCESS_DENIED"')&&sr.output.includes('"subprocess":"ERR_ACCESS_DENIED"'),'V03_NODE_PERMISSION_ENFORCED');
 r=await tool('read_file',{path:'v08-script-output.txt'});
 eq(r.value.text.includes('PHASE_ALPHA'),'V03_SCRIPT_CREATED_RESULT_FILE');
 r=await tool('edit_block',{file_path:'v03-scratch-run.js',old_string:'PHASE_ALPHA',new_string:'PHASE_BETA'});
 eq(!r.isError&&r.value.replacements===1,'V03_SCRIPT_EDIT_VIA_MCP');
 sr=await runScript('run v03-scratch-run.js');
 eq(sr.exitCode===0&&sr.output.includes('PHASE_BETA'),'V03_EDITED_SCRIPT_REEXEC');
 r=await tool('read_file',{path:'v08-script-output.txt'});
 eq(r.value.text.includes('PHASE_BETA'),'V03_SCRIPT_RESULT_AFTER_EDIT');
 r=await tool('write_file',{mode:'rewrite',path:'v03-idle.js',content:"setInterval(()=>{},1000);"});
 eq(!r.isError,'V03_TIMEOUT_SCRIPT_WRITTEN');
 sr=await runScript('run v03-idle.js',44,300);
 console.log('V03_TIMEOUT_RESULT',JSON.stringify(sr));
 eq(!sr.running&&sr.timedOut&&sr.signal==='SIGTERM','V03_RUNTIME_WATCHDOG');
 console.log('XOOM_V03_UNPRIVILEGED_SELF_HOSTED_LOOP_PASS');

 r=await tool('get_config',{});
 eq(r.value.networkRestricted===false,'V031_NETWORK_LIMIT_HONEST');
 r=await tool('start_process',{command:'run v031-symlink.js'});eq(r.isError,'V031_SYMLINK_DENIED');
 r=await tool('start_process',{command:'run v031-hardlink.js'});eq(r.isError,'V031_HARDLINK_DENIED');
 r=await tool('start_process',{command:'run v031-rootowned.js'});eq(r.isError,'V031_WRONG_OWNER_DENIED');
 r=await tool('start_process',{command:'run v031-invalidutf8.js'});eq(r.isError,'V031_INVALID_UTF8_DENIED');
 r=await tool('read_file',{path:'v031-invalidutf8.js'});eq(r.isError,'V031_INVALID_UTF8_READ_DENIED');
 r=await tool('write_file',{mode:'rewrite',path:'v031-nul.txt',content:'x\u0000y'});eq(r.isError,'V031_NUL_TEXT_WRITE_DENIED');
 r=await tool('write_file',{mode:'rewrite',path:'v031-lonesurrogate.txt',content:'bad\uD800'});eq(r.isError,'V031_SURROGATE_TEXT_WRITE_DENIED');
 r=await tool('write_file',{mode:'rewrite',path:'v031-too-large.txt',content:'x'.repeat(32769)});eq(r.isError,'V031_OVERSIZE_WRITE_DENIED');
 const immutableV1="setTimeout(()=>console.log('IMMUTABLE_SNAPSHOT_ALPHA'),1300);";
 r=await tool('write_file',{mode:'rewrite',path:'v031-immutability.js',content:immutableV1});eq(!r.isError,'V031_SNAPSHOT_SOURCE_WRITTEN');
 let sp=await tool('start_process',{command:'run v031-immutability.js'});
 eq(!sp.isError&&sp.value.uid===2000,'V031_SNAPSHOT_PROCESS_STARTED');
 const crypto=require('node:crypto');
 const expectedHash=crypto.createHash('sha256').update(immutableV1).digest('hex');
 eq(sp.value.sourceSha256===expectedHash,'V031_SNAPSHOT_SOURCE_HASH');
 const immutablePid=sp.value.pid;
 const snapDir=D+'/execution-snapshots',nodefs=require('node:fs');
 const files=nodefs.readdirSync(snapDir);
 const currentSnapshot=files.find(n=>n.startsWith('snapshot-')&&nodefs.readFileSync(snapDir+'/'+n,'utf8')===immutableV1);
 eq(Boolean(currentSnapshot),'V031_SNAPSHOT_ROOT_STAGED');
 const snapshotStat=nodefs.statSync(snapDir+'/'+currentSnapshot);
 eq(snapshotStat.uid===0&&snapshotStat.gid===2000&&(snapshotStat.mode&0o777)===0o640,'V031_SNAPSHOT_ROOT_OWNED_GROUP_READ_ONLY');
 r=await tool('edit_block',{file_path:'v031-immutability.js',old_string:'IMMUTABLE_SNAPSHOT_ALPHA',new_string:'IMMUTABLE_SNAPSHOT_BETA'});
 eq(!r.isError,'V031_MUTABLE_ORIGINAL_CHANGED');
 let out;
 for(let i=0;i<22;i++){await new Promise(done=>setTimeout(done,250));out=await tool('read_process_output',{pid:immutablePid,offset:-30});if(!out.value.running)break;}
 console.log('V031_SNAPSHOT_RUN_OUTPUT',JSON.stringify(out.value));
 eq(out.value.exitCode===0&&out.value.output.includes('IMMUTABLE_SNAPSHOT_ALPHA')&&!out.value.output.includes('IMMUTABLE_SNAPSHOT_BETA'),'V031_SNAPSHOT_IMMUTABLE_WHILE_SOURCE_EDITED');
 eq(!nodefs.existsSync(snapDir+'/'+currentSnapshot),'V031_SNAPSHOT_CLEANED_ON_PROCESS_EXIT');
 r=await tool('write_file',{mode:'rewrite',path:'v031-flood.js',content:"process.stdout.write('X'.repeat(60000));"});
 eq(!r.isError,'V031_FLOOD_SCRIPT_WRITTEN');
 let flood=await tool('start_process',{command:'run v031-flood.js'});eq(!flood.isError,'V031_FLOOD_LAUNCHED');
 for(let i=0;i<25;i++){await new Promise(done=>setTimeout(done,230));out=await tool('read_process_output',{pid:flood.value.pid,offset:-40});if(!out.value.running)break;}
 eq(out.value.exitCode===0&&out.value.outputTruncated&&out.value.output.length<=16384,'V031_FLOOD_OUTPUT_BOUNDED');
 r=await tool('write_file',{mode:'rewrite',path:'v031-loopback.js',content:"const net=require('node:net');const x=net.connect({host:'127.0.0.1',port:1});x.on('error',e=>console.log('LOOPBACK_RESULT',e.code));x.on('connect',()=>{console.log('LOOPBACK_RESULT CONNECTED');x.end()});"});
 eq(!r.isError,'V031_LOOPBACK_SCRIPT_WRITTEN');
 let netRun=await tool('start_process',{command:'run v031-loopback.js'});eq(!netRun.isError,'V031_LOOPBACK_LAUNCHED');
 for(let i=0;i<25;i++){await new Promise(done=>setTimeout(done,220));out=await tool('read_process_output',{pid:netRun.value.pid,offset:-30});if(!out.value.running)break;}
 console.log('V031_LOOPBACK_OUTPUT',JSON.stringify(out.value));
 eq(out.value.exitCode===0&&out.value.output.includes('LOOPBACK_RESULT EACCES'),'V031_AF_INET_SOCKET_DENIED');
 console.log('XOOM_V031_SECURITY_NEGATIVE_QA_PASS');

 // v0.4 standard filesystem and search tool regression, direct MCP stdio on actual ARM hardware.
 r=await tool('get_config',{});eq(r.value.version==='xoom-scratch-dev-v0.12-LOCAL-ONLY','V12_VERSION_AND_TOOLSET');
 eq(listed.result.tools.some(x=>x.name==='start_search')&&listed.result.tools.some(x=>x.name==='create_directory'),'V12_OFFICIAL_TOOL_NAMES');
 const project='v12finalproj',childProject='v12finalproj/src',sourceName=childProject+'/worker.js';
 r=await tool('create_directory',{path:project});eq(!r.isError,'V12_CREATE_ROOT_PROJECT');
 r=await tool('create_directory',{path:childProject});eq(!r.isError,'V12_CREATE_SRC_SUBDIRECTORY');
 r=await tool('write_file',{mode:'rewrite',path:sourceName,content:"// UNIQUE_DEVICE_SYMBOL_V12\nconsole.log('PROJECT_ALPHA');\n"});
 eq(!r.isError,'V12_NESTED_WRITE');
 r=await tool('get_file_info',{path:sourceName});eq(!r.isError&&r.value.uid===2000&&r.value.mode==='600','V12_NESTED_OWNER');
 r=await tool('read_file',{path:sourceName});eq(!r.isError&&r.value.text.includes('UNIQUE_DEVICE_SYMBOL_V12'),'V12_NESTED_READ');
 r=await tool('edit_block',{file_path:sourceName,old_string:'PROJECT_ALPHA',new_string:'PROJECT_BETA'});
 eq(!r.isError,'V12_NESTED_EDIT');
 r=await tool('read_file',{path:sourceName});eq(r.value.text.includes('PROJECT_BETA'),'V12_NESTED_EDIT_READBACK');
 r=await tool('list_directory',{path:project,depth:3});
 eq(!r.isError&&r.value.entries.some(e=>e.name==='src/worker.js'),'V12_NESTED_LIST');
 const searchF=await tool('start_search',{path:ROOT,pattern:'worker.js',searchType:'files',literalSearch:true});
 eq(!searchF.isError&&searchF.value.sessionId,'V12_SEARCH_FILES_STARTED');
 async function pollSearch(sessionId){
  let state;
  for(let j=0;j<36;j++){state=await tool('get_more_search_results',{sessionId,offset:0,length:100});if(!state.value.status||state.value.complete)break;await new Promise(resolve=>setTimeout(resolve,250));}
  return state;
 }
 const fileFound=await pollSearch(searchF.value.sessionId);
 console.log('V12_SEARCH_FILENAME_RESULT',JSON.stringify(fileFound.value));
 eq(!fileFound.isError&&fileFound.value.status==='completed'&&fileFound.value.results.some(x=>x.relativePath==='v12finalproj/src/worker.js'),'V12_SEARCH_FILES_MATCH');
 const searchC=await tool('start_search',{path:ROOT,pattern:'UNIQUE_DEVICE_SYMBOL_V12',searchType:'content',filePattern:'*.js',literalSearch:true,contextLines:1});
 eq(!searchC.isError&&searchC.value.sessionId,'V12_SEARCH_CONTENT_STARTED');
 const codeFound=await pollSearch(searchC.value.sessionId);
 console.log('V12_SEARCH_CONTENT_RESULT',JSON.stringify(codeFound.value));
 eq(!codeFound.isError&&codeFound.value.status==='completed'&&codeFound.value.results.some(x=>x.relativePath==='v12finalproj/src/worker.js'&&x.line===1),'V12_SEARCH_CONTENT_WITH_LINE');
 const neg=await tool('start_search',{path:ROOT,pattern:'DOES_NOT_MATCH_THIS_FILE',searchType:'files',literalSearch:true});
 const empty=await pollSearch(neg.value.sessionId);
 eq(empty.value.status==='completed'&&empty.value.results.length===0,'V12_EMPTY_SEARCH');
 r=await tool('list_searches',{});eq(!r.isError&&r.value.searches.length>=2,'V12_LIST_SEARCHES');
 r=await tool('stop_search',{sessionId:searchC.value.sessionId});eq(!r.isError,'V12_STOP_COMPLETED_SEARCH_SAFE');
 r=await tool('move_file',{source:sourceName,destination:'v12finalproj/src/renamed.js'});eq(!r.isError,'V12_MOVE_FILE');
 r=await tool('get_file_info',{path:sourceName});eq(r.isError,'V12_MOVED_OLD_PATH_GONE');
 r=await tool('get_file_info',{path:'v12finalproj/src/renamed.js'});eq(!r.isError,'V12_MOVED_FILE_PRESENT');
 r=await tool('start_process',{command:'run v12finalproj/src/renamed.js'});
 eq(!r.isError&&r.value.uid===2000,'V12_NESTED_SCRIPT_STARTED');
 let nestedRun;for(let j=0;j<25;j++){await new Promise(resolve=>setTimeout(resolve,220));nestedRun=await tool('read_process_output',{pid:r.value.pid});if(!nestedRun.value.running)break;}
 console.log('V12_NESTED_RUN',JSON.stringify(nestedRun.value));
 eq(nestedRun.value.exitCode===0&&nestedRun.value.output.includes('PROJECT_BETA'),'V12_NESTED_JS_EXECUTION');
 r=await tool('create_directory',{path:'../outside'});eq(r.isError,'V12_CREATE_TRAVERSAL_REJECTED');
 r=await tool('write_file',{mode:'rewrite',path:'v12finalproj/../esc.txt',content:'bad'});eq(r.isError,'V12_NESTED_TRAVERSAL_REJECTED');
 r=await tool('move_file',{source:'v12finalproj/src/renamed.js',destination:'v12finalproj/src/../../outside.js'});eq(r.isError,'V12_MOVE_TRAVERSAL_REJECTED');
 r=await tool('move_file',{source:'v12finalproj/src/renamed.js',destination:'v12finalproj/src/renamed.js'});eq(r.isError,'V12_MOVE_SAME_PATH_REJECTED');
 const resultName='v12finalproj/src/renamed.js';
 r=await tool('move_file',{source:resultName,destination:'v12finalproj/renamed.js'});eq(!r.isError,'V12_MOVE_ACROSS_PROJECT_DIRS');
 r=await tool('list_directory',{path:'v12finalproj',depth:3});eq(!r.isError&&r.value.entries.some(x=>x.name==='renamed.js'),'V12_PROJECT_RECURSIVE_LIST');
 console.log('XOOM_V12_STANDARD_SEARCH_PROJECT_TOOLS_PASS');

 const cfg05=await tool('get_config',{});
 eq(!cfg05.isError&&cfg05.value.version==='xoom-scratch-dev-v0.12-LOCAL-ONLY'&&cfg05.value.tools.length===26,'V12_CONFIG_22');
 r=await tool('read_multiple_files',{paths:['smoke.txt','v12finalproj/renamed.js','missing-v06.txt','../outside.txt']});
 console.log('V12_MULTI_READ',JSON.stringify({requested:r.value.requested,ok:r.value.files.map(x=>x.ok),bytes:r.value.totalBytes}));
 eq(!r.isError&&r.value.requested===4&&r.value.succeeded===2&&r.value.failed===2,'V12_MULTI_READ_PARTIAL_FAILURES');
 eq(r.value.files[1].content.includes('PROJECT_BETA'),'V12_MULTI_READ_COMPLETE_TEXT');
 r=await tool('read_multiple_files',{paths:Array(9).fill('x.txt')});
 eq(r.isError,'V12_MULTI_READ_CAP_ENFORCED');
 const liveJs="process.stdin.setEncoding('utf8');process.stdin.on('data',x=>{console.log('STANDALONE_STDIN_ECHO:'+x.trim())});setTimeout(()=>{},7000);";
 r=await tool('write_file',{mode:'rewrite',path:'v06-interactive.js',content:liveJs});
 eq(!r.isError,'V12_INTERACTIVE_SCRIPT_STAGED');
 r=await tool('start_process',{command:'run v06-interactive.js'});
 eq(!r.isError&&r.value.uid===2000,'V12_INTERACTIVE_LAUNCH');
 const pid05=r.value.pid;
 let pr=await tool('list_processes',{});
 eq(!pr.isError&&pr.value.scope==='agent-owned-only'&&pr.value.processes.some(x=>x.pid===pid05&&x.interactive),'V12_OWNED_PROCESS_LIST');
 r=await tool('interact_with_process',{pid:pid05,input:'PING_FROM_V12\n',wait_for_prompt:false,timeout_ms:0});
 eq(!r.isError&&r.value.stdinBytes===14,'V12_STDIN_SENT');
 let seen;
 for(let j=0;j<25;j++){
  await new Promise(resolve=>setTimeout(resolve,150));
  seen=await tool('read_process_output',{pid:pid05});
  if(seen.value.output.includes('STANDALONE_STDIN_ECHO:PING_FROM_V12'))break;
 }
 console.log('V12_INTERACTIVE_OUTPUT',JSON.stringify(seen.value));
 eq(seen.value.output.includes('STANDALONE_STDIN_ECHO:PING_FROM_V12'),'V12_STDIN_ROUND_TRIP');
 r=await tool('interact_with_process',{pid:pid05,input:'\u0000'});
 eq(r.isError,'V12_STDIN_NUL_REJECTED');
 r=await tool('interact_with_process',{pid:987654,input:'ANYTHING'});
 eq(r.isError,'V12_UNOWNED_STDIN_REJECTED');
 r=await tool('kill_process',{pid:987654});
 eq(r.isError,'V12_UNOWNED_KILL_REJECTED');
 r=await tool('kill_process',{pid:pid05});
 eq(!r.isError&&r.value.terminationRequested,'V12_UID2000_TERMINATION_REQUESTED');
 for(let j=0;j<25;j++){
  await new Promise(resolve=>setTimeout(resolve,160));
  seen=await tool('read_process_output',{pid:pid05});
  if(!seen.value.running)break;
 }
 eq(!seen.value.running&&seen.value.signal==='SIGTERM','V12_UID2000_TERMINATED');
 r=await tool('start_process',{command:'diag wait'});
 eq(!r.isError,'V12_ROOT_DIAG_STAGED');
 const rootPid=r.value.pid;
 r=await tool('interact_with_process',{pid:rootPid,input:'SHOULD_NOT_EXECUTE'});
 eq(r.isError,'V12_ROOT_DIAG_STDIN_DENIED');
 r=await tool('kill_process',{pid:rootPid});
 eq(r.isError,'V12_ROOT_DIAG_KILL_DENIED');
 r=await tool('force_terminate',{pid:rootPid});
 eq(!r.isError,'V12_LEGACY_ROOT_DIAG_TERMINATION');
 r=await tool('get_usage_stats',{});
 eq(!r.isError&&r.value.totalToolCalls>=10&&r.value.failedCalls>=4&&r.value.toolCounts.interact_with_process>=3,'V12_PRIVACY_SAFE_STATS');
 r=await tool('get_recent_tool_calls',{maxResults:8});
 eq(!r.isError&&r.value.calls.length<=8&&r.value.recordsExcludeArguments,'V12_BOUNDED_CALL_HISTORY');
 eq(!JSON.stringify(r.value).includes('SHOULD_NOT_EXECUTE'),'V12_HISTORY_ARGUMENT_OMISSION');
 const checkStop=await tool('start_search',{path:ROOT,pattern:'v06-interactive.js',searchType:'files',literalSearch:true});
 const finishStop=await pollSearch(checkStop.value.sessionId);
 eq(finishStop.value.status==='completed','V12_LAST_SEARCH_COMPLETED');
 r=await tool('stop_search',{sessionId:checkStop.value.sessionId});
 eq(!r.isError&&r.value.terminationRequested===false&&r.value.status==='completed','V12_COMPLETED_SEARCH_STOP_IS_NOOP');
 console.log('XOOM_V12_26_TOOL_REGRESSION_QA_PASS');


})().catch(e=>{console.log('XOOM_SCOPED_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});