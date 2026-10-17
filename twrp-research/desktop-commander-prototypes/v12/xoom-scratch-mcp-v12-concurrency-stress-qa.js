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
 const fs=require('node:fs'),hash=require('node:crypto').createHash;
 let r=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(r.result.serverInfo.version==='0.12.0-local','V12_SERVER_VERSION');
 r=await request('tools/list',{});
 eq(r.result.tools.length===26,'V12_TOOL_COUNT');
 eq(!!r.result.tools.find(x=>x.name==='write_file').inputSchema.properties.expected_sha256,'V12_CONDITIONAL_WRITE_SCHEMA');
 r=await tool('get_config',{});
 eq(!r.isError&&r.value.cooperativeWriteLocks===true&&r.value.conditionalFileWrites===true,'V12_DISCLOSED_WRITE_LOCKS');
 const f='v12-concurrent-append.txt';
 r=await tool('write_file',{path:f,content:'BASE\n',mode:'rewrite'});
 eq(!r.isError,'V12_CONCURRENT_BASE_CREATED');
 const before=hash('sha256').update('BASE\n').digest('hex');
 r=await tool('write_file',{path:f,content:'UNAUTHORIZED\n',mode:'append',expected_sha256:'f'.repeat(64)});
 eq(r.isError,'V12_STALE_WRITE_CONFLICT_DENIED');
 r=await tool('read_file',{path:f});
 eq(r.value.text==='BASE\n','V12_SOURCE_PRESERVED_AFTER_CONFLICT');
 r=await tool('write_file',{path:f,content:'AUTHORIZED\n',mode:'append',expected_sha256:before});
 eq(!r.isError&&r.value.mode==='append','V12_CONDITIONAL_APPEND_PASS');
 let expected='BASE\nAUTHORIZED\n';
 for(let k=0;k<4;k++){
  const names=['PAIR_'+k+'_LEFT','PAIR_'+k+'_RIGHT'];
  const writes=await Promise.all(names.map(x=>tool('write_file',{path:f,content:x+'\n',mode:'append'})));
  console.log('V12_LOCK_PAIR',k,writes.map(x=>({error:x.isError,wait:x.value.lockWaitMs,code:x.value.error})));
  eq(writes.every(x=>!x.isError),'V12_PARALLEL_APPEND_PAIR_'+k);
  expected+=names.map(x=>x+'\n').join('');
 }
 r=await tool('read_file',{path:f});
 const actual=r.value.text;
 eq(!r.isError&&actual.split('\n').filter(Boolean).length===10,'V12_CONCURRENT_APPENDS_ALL_PRESENT');
 for(let k=0;k<4;k++)for(const side of ['LEFT','RIGHT']){
  const val='PAIR_'+k+'_'+side;
  eq(actual.split('\n').filter(line=>line===val).length===1,'V12_NO_LOST_UPDATE_'+k+'_'+side);
 }
 const fileInfo=await tool('get_file_info',{path:f});
 eq(!fileInfo.isError&&fileInfo.value.hashAlgorithm==='sha256'&&fileInfo.value.sha256===hash('sha256').update(actual).digest('hex'),'V12_FILE_INFO_EXPOSES_HASH');
 r=await tool('write_file',{path:f,content:'CAS_AFTER_INFO\n',mode:'append',expected_sha256:fileInfo.value.sha256});
 eq(!r.isError,'V12_WRITE_USING_INFO_HASH');
 const relative=fs.readdirSync(ROOT).filter(n=>n.startsWith('.v12-write-')&&n.endsWith('.lock'));
 eq(relative.length===0,'V12_LOCK_FILES_CLEANED');
 const edit='v12-conflict-edit.txt';
 r=await tool('write_file',{path:edit,content:'A\nTOKEN\nZ\n',mode:'rewrite'});
 eq(!r.isError,'V12_EDIT_SOURCE_CREATED');
 const editSha=hash('sha256').update('A\nTOKEN\nZ\n').digest('hex');
 const editRace=await Promise.all([
  tool('edit_block',{file_path:edit,old_string:'TOKEN',new_string:'LEFT',expected_sha256:editSha}),
  tool('edit_block',{file_path:edit,old_string:'TOKEN',new_string:'RIGHT',expected_sha256:editSha})
 ]);
 console.log('V12_EDIT_RACE',editRace.map(x=>({error:x.isError,detail:x.value.error||x.value.replacements})));
 eq(editRace.filter(x=>!x.isError).length===1,'V12_EDIT_SINGLE_WINNER');
 r=await tool('read_file',{path:edit});
 eq(r.value.text==='A\nLEFT\nZ\n'||r.value.text==='A\nRIGHT\nZ\n','V12_EDIT_SINGLE_VERSION');
 const rootList=await tool('list_directory',{path:'v11-progress-fixtures',depth:1});
 eq(!rootList.isError&&rootList.value.entries.length>=90,'V12_STRESS_FIXTURES_AVAILABLE');
 const marker='V11_INCREMENTAL_SEARCH_MARKER_92E';
 for(let round=0;round<4;round++){
  let s=await tool('start_search',{path:'v11-progress-fixtures',pattern:marker,searchType:'content',literalSearch:true,maxResults:120,filePattern:'v11scan-*.txt'});
  eq(!s.isError,'V12_STRESS_SEARCH_START_'+round);
  let sawRunning=false,finish=null;
  for(let poll=0;poll<120;poll++){
   await new Promise(resolve=>setTimeout(resolve,50));
   const q=await tool('get_more_search_results',{sessionId:s.value.sessionId,offset:0,length:100});
   if(q.isError)throw Error('Unexpected search poll error');
   if(q.value.status==='running'&&q.value.totalResults>0)sawRunning=true;
   if(q.value.complete){finish=q.value;break}
  }
  console.log('V12_STRESS_SEARCH_OUTCOME',JSON.stringify({round,status:finish?.status,count:finish?.totalResults,scanned:finish?.scanned,sawRunning,error:finish?.error}));
  eq(!!finish&&finish.status==='completed'&&finish.totalResults===96&&finish.scanned>=96&&finish.error===null,'V12_STRESS_SEARCH_COMPLETE_'+round);
  eq(sawRunning||finish.firstResultAt<finish.completedAt,'V12_STRESS_LIVE_RESULTS_'+round);
  const page=await tool('get_more_search_results',{sessionId:s.value.sessionId,offset:90,length:20});
  eq(!page.isError&&page.value.results.length===6,'V12_STRESS_PAGINATION_'+round);
 }
 for(let round=0;round<3;round++){
  let s=await tool('start_search',{path:'v11-progress-fixtures',pattern:marker,searchType:'content',literalSearch:true,maxResults:120,filePattern:'v11scan-*.txt'});
  eq(!s.isError,'V12_CANCEL_START_'+round);
  const id=s.value.sessionId;
  let partial=0,stopped;
  for(let poll=0;poll<35;poll++){
   await new Promise(resolve=>setTimeout(resolve,25));
   const q=await tool('get_more_search_results',{sessionId:id,offset:0,length:100});
   partial=q.value.totalResults;
   if(q.value.status==='running'&&partial>0)break;
   if(q.value.complete)break;
  }
  const terminate=await tool('stop_search',{sessionId:id});
  eq(!terminate.isError,'V12_CANCEL_REQUEST_'+round);
  for(let poll=0;poll<65;poll++){
   await new Promise(resolve=>setTimeout(resolve,45));
   const q=await tool('get_more_search_results',{sessionId:id,offset:0,length:100});
   if(q.value.complete){stopped=q.value;break}
  }
  console.log('V12_CANCEL_OUTCOME',JSON.stringify({round:round,status:stopped?.status,partial,retained:stopped?.totalResults}));
  eq(!!stopped&&stopped.complete&&stopped.totalResults>=partial,'V12_CANCEL_RETAINS_RESULTS_'+round);
 }
 console.log('XOOM_V12_CONCURRENT_WRITE_AND_SEARCH_STRESS_HARDWARE_PASS');
})().catch(e=>{console.error('V12_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});