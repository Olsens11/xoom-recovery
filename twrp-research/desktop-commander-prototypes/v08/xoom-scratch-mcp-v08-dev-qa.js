'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v08-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const init=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(init.result.serverInfo.version==='0.8.0-local','V08_SERVER_VERSION');
 const defs=await request('tools/list',{});
 eq(defs.result.tools.length===26,'V08_TOOLS_26');
 let r=await tool('get_config',{});
 eq(r.value.developmentProfiles.runMs===90000&&r.value.developmentProfiles.replMs===120000&&r.value.developmentProfiles.uid===2000&&!r.value.developmentProfiles.rootShell,'V08_DEVELOPMENT_PROFILES');
 const source="console.log('DEV_EXTENDED_START',process.getuid());"+
 "const fs=require('node:fs');"+
 "try{fs.readFileSync('/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v08-candidate.js');console.log('DEV_OUTSIDE_UNEXPECTED')}catch(e){console.log('DEV_OUTSIDE_DENIED',e.code)}"+
 "try{require('node:child_process').execSync('id');console.log('DEV_SPAWN_UNEXPECTED')}catch(e){console.log('DEV_SPAWN_DENIED',e.code)}"+
 "setTimeout(()=>console.log('DEV_EXTENDED_OK'),11500);";
 r=await tool('write_file',{path:'v08-dev-long.js',content:source,mode:'rewrite'});
 eq(!r.isError,'V08_SOURCE_STAGED');
 r=await tool('start_process',{command:'dev check v08-dev-long.js'});
 eq(!r.isError&&r.value.profile==='check'&&r.value.uid===2000&&r.value.limitMs===15000,'V08_SYNTAX_CHECK_STARTED');
 let checkResult;for(let i=0;i<24;i++){
  await new Promise(resolve=>setTimeout(resolve,125));
  checkResult=await tool('read_process_output',{pid:r.value.pid,offset:-20});
  if(!checkResult.value.running)break;
 }
 eq(!checkResult.value.running&&checkResult.value.exitCode===0&&!checkResult.value.output.includes('DEV_EXTENDED_START'),'V08_SYNTAX_CHECK_NO_EXECUTE');
 const bad="const broken = ;";
 r=await tool('write_file',{path:'v08-dev-invalid.js',content:bad});
 eq(!r.isError,'V08_INVALID_SOURCE_STAGED');
 r=await tool('start_process',{command:'dev check v08-dev-invalid.js'});
 eq(!r.isError&&r.value.uid===2000,'V08_INVALID_CHECK_STARTED');
 let badResult;for(let i=0;i<22;i++){
  await new Promise(resolve=>setTimeout(resolve,125));
  badResult=await tool('read_process_output',{pid:r.value.pid,offset:-35});
  if(!badResult.value.running)break;
 }
 console.log('CHECK_INVALID',JSON.stringify(badResult));
 eq(badResult.value.exitCode!==0&&badResult.value.output.includes('SyntaxError'),'V08_SYNTAX_CHECK_INVALID_REPORTS_ERROR');
 r=await tool('start_process',{command:'dev run v08-dev-long.js'});
 eq(!r.isError&&r.value.profile==='run'&&r.value.uid===2000&&r.value.limitMs===90000,'V08_EXTENDED_RUN_LAUNCH');
 const pid=r.value.pid;
 let out;let aggregate='';
 for(let i=0;i<90;i++){
  await new Promise(resolve=>setTimeout(resolve,175));
  out=await tool('read_process_output',{pid,offset:0,length:50});
  aggregate+=out.value.output+'\n';
  if(!out.value.running)break;
 }
 console.log('EXTENDED_OUTPUT',JSON.stringify({pid,output:aggregate,exit:out.value.exitCode,elapsed:out.value.timedOut}));
 eq(!out.value.running&&out.value.exitCode===0&&aggregate.includes('DEV_EXTENDED_OK'),'V08_EXTENDED_RUN_OVER_NINE_SECONDS');
 eq(aggregate.includes('DEV_EXTENDED_START 2000'),'V08_UID2000_PROCESS');
 eq(aggregate.includes('DEV_OUTSIDE_DENIED ERR_ACCESS_DENIED'),'V08_READ_BOUNDARY_DENIED');
 eq(aggregate.includes('DEV_SPAWN_DENIED ERR_ACCESS_DENIED'),'V08_SUBPROCESS_DENIED');
 r=await tool('start_process',{command:'dev repl'});
 console.log('REPL_LAUNCH',JSON.stringify(r));
 eq(!r.isError&&r.value.profile==='repl'&&r.value.uid===2000&&r.value.interactive&&r.value.limitMs===120000,'V08_REPL_LAUNCH');
 const replPid=r.value.pid;
 let initial;
 for(let i=0;i<25;i++){
  await new Promise(resolve=>setTimeout(resolve,140));
  initial=await tool('read_process_output',{pid:replPid,offset:-20});
  if(initial.value.waitingForInput)break;
 }
 console.log('REPL_INITIAL',JSON.stringify(initial));
 eq(initial.value.running,'V08_REPL_INITIAL_ALIVE');
 r=await tool('interact_with_process',{pid:replPid,input:"console.log('REPL_RESULT',process.getuid(),2+3)\n"});
 eq(!r.isError,'V08_REPL_STDIN_DELIVERED');
 let replObs='',pr;
 for(let i=0;i<28;i++){
  await new Promise(resolve=>setTimeout(resolve,160));
  pr=await tool('read_process_output',{pid:replPid,offset:-35});
  replObs=pr.value.output;
  if(replObs.includes('REPL_RESULT 2000 5'))break;
 }
 console.log('REPL_OUTPUT',JSON.stringify(pr));
 eq(replObs.includes('REPL_RESULT 2000 5'),'V08_INTERACTIVE_REPL_ROUND_TRIP');
 r=await tool('interact_with_process',{pid:replPid,input:"require('node:fs').readFileSync('/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v08-candidate.js')\n"});
 eq(!r.isError,'V08_REPL_RESTRICTED_PROBE_SENT');
 let fsObs='';
 for(let i=0;i<27;i++){
  await new Promise(resolve=>setTimeout(resolve,160));
  pr=await tool('read_process_output',{pid:replPid,offset:-55});
  fsObs=pr.value.output;
  if(fsObs.includes('ERR_ACCESS_DENIED'))break;
 }
 console.log('REPL_DENIAL',JSON.stringify(fsObs.slice(-500)));
 eq(fsObs.includes('ERR_ACCESS_DENIED'),'V08_REPL_OUTSIDE_READ_DENIED');
 r=await tool('start_process',{command:'dev repl;id'});eq(r.isError,'V08_SHELL_INJECTION_REJECTED');
 r=await tool('start_process',{command:'dev run ../../etc/passwd'});eq(r.isError,'V08_TRAVERSAL_COMMAND_REJECTED');
 r=await tool('start_process',{command:'/sbin/sh'});eq(r.isError,'V08_ROOT_SHELL_REJECTED');
 r=await tool('kill_process',{pid:replPid});
 eq(!r.isError&&r.value.terminationRequested,'V08_REPL_TERMINATION_REQUESTED');
 let last;
 for(let i=0;i<32;i++){await new Promise(resolve=>setTimeout(resolve,130));last=await tool('read_process_output',{pid:replPid,offset:-20});if(!last.value.running)break}
 eq(!last.value.running&&last.value.signal==='SIGTERM','V08_REPL_TERMINATED');
 console.log('XOOM_V08_DEVELOPMENT_EXECUTION_QA_PASS');
})().catch(e=>{console.error('XOOM_V08_DEVELOPMENT_EXECUTION_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});