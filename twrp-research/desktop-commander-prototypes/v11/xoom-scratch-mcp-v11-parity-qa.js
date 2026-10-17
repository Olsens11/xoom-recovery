'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v11-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const fs=require('node:fs'),crypto=require('node:crypto');
 const init=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(init.result.serverInfo.version==='0.11.0-local','V11_SERVER_VERSION');
 const list=await request('tools/list',{});
 eq(list.result.tools.length===26,'V11_TOOLS_26');
 const config=await tool('get_config',{});
 eq(!config.isError&&config.value.largeEditLimitBytes===262144&&config.value.progressiveSearchResults===true,'V11_DECLARED_CAPABILITIES');
 const file='v11-long-edit.js',oldTag='V11_DEEP_ALPHA_56B',newTag='V11_DEEP_BETA_56B';
 let old='';
 for(let c=0;c<6;c++){
  let chunk='';
  for(let i=0;i<270;i++){
   const n=c*270+i;
   chunk+='// V11_OLD_LINE_'+String(n).padStart(5,'0')+' '+(n===1100?oldTag:'private development text')+' '+ 'Q'.repeat(49)+'\n';
  }
  if(c===5)chunk+="console.log('V11_SCRIPT_EDITED_OK',process.getuid());\n";
  old+=chunk;
  let r=await tool('write_file',{path:file,content:chunk,mode:c?'append':'rewrite'});
  eq(!r.isError,'V11_EDIT_SOURCE_CHUNK_'+c);
 }
 const initialBytes=Buffer.byteLength(old,'utf8'),initialSha=crypto.createHash('sha256').update(old).digest('hex');
 eq(initialBytes>110000&&initialBytes<=262144,'V11_EDIT_LARGE_SOURCE');
 let r=await tool('edit_block',{file_path:file,old_string:oldTag,new_string:newTag,expected_replacements:1,expected_sha256:'0'.repeat(64)});
 eq(r.isError,'V11_STALE_SHA_EDIT_REJECTED');
 r=await tool('get_file_info',{path:file});
 eq(r.value.size===initialBytes,'V11_CONFLICT_PRESERVES_LENGTH');
 r=await tool('edit_block',{file_path:file,old_string:oldTag,new_string:newTag,expected_replacements:2,expected_sha256:initialSha});
 eq(r.isError,'V11_EXPECTED_REPLACEMENTS_REJECTED');
 r=await tool('edit_block',{file_path:file,old_string:oldTag,new_string:newTag,expected_replacements:1,expected_sha256:initialSha});
 console.log('V11_EDIT_RESULT',JSON.stringify(r.value));
 eq(!r.isError&&r.value.replacements===1&&r.value.sourceSha256===initialSha,'V11_LARGE_EDIT_PASS');
 const edited=old.replace(oldTag,newTag),newSha=crypto.createHash('sha256').update(edited).digest('hex');
 eq(r.value.updatedSha256===newSha,'V11_LARGE_EDIT_NEW_DIGEST');
 r=await tool('read_file',{path:file,offset:1099,length:3});
 eq(!r.isError&&r.value.text.includes(newTag)&&!r.value.text.includes(oldTag),'V11_LARGE_DEEP_EDIT_READBACK');
 r=await tool('start_process',{command:'dev check '+file});
 eq(!r.isError&&r.value.sourceSha256===newSha,'V11_LARGE_EDIT_SNAPSHOT_SOURCE_HASH');
 let status;
 for(let i=0;i<60;i++){
  await new Promise(x=>setTimeout(x,140));
  status=await tool('read_process_output',{pid:r.value.pid,offset:-10});
  if(!status.value.running)break;
 }
 eq(!status.value.running&&status.value.exitCode===0,'V11_EDITED_150K_SCRIPT_SYNTAX_VALID');
 const directory=ROOT+'/v11-progress-fixtures';
 try{fs.mkdirSync(directory,{mode:0o700})}catch(e){if(e.code!=='EEXIST')throw e}
 fs.chownSync(directory,2000,2000);fs.chmodSync(directory,0o700);
 const marker='V11_INCREMENTAL_SEARCH_MARKER_92E';
 for(let i=0;i<96;i++){
  const f=directory+'/v11scan-'+String(i).padStart(3,'0')+'.txt';
  const filler='filler text '+String(i).padStart(3,'0')+' '+ 'K'.repeat(140)+'\n';
  const body=(i===0?marker+'\n':'')+filler.repeat(270)+(i!==0?marker+'\n':'');
  fs.writeFileSync(f,body,{mode:0o600});fs.chownSync(f,2000,2000);fs.chmodSync(f,0o600);
 }
 console.log('V11_STREAM_FIXTURES_STAGED',96);
 r=await tool('start_search',{path:'v11-progress-fixtures',pattern:marker,searchType:'content',literalSearch:true,maxResults:120,filePattern:'v11scan-*.txt'});
 eq(!r.isError&&!!r.value.sessionId,'V11_PROGRESSIVE_SEARCH_START');
 const sid=r.value.sessionId;let partial=false,seenScanned=0,final;
 for(let i=0;i<110;i++){
  await new Promise(x=>setTimeout(x,65));
  const q=await tool('get_more_search_results',{sessionId:sid,offset:0,length:100});
  if(q.isError)throw Error('Progress poll failed');
  const v=q.value;
  if(v.status==='running'&&v.results.length>0)partial=true;
  seenScanned=Math.max(seenScanned,v.scanned);
  if(v.complete){final=v;break}
 }
 if(!final)throw Error('Search never completed in bounded QA time');
 console.log('V11_STREAM_FINAL',JSON.stringify({status:final.status,count:final.totalResults,scanned:final.scanned,partial,firstResultAt:final.firstResultAt,completedAt:final.completedAt,error:final.error}));
 eq(final.status==='completed'&&final.error===null&&final.streaming===true,'V11_PROGRESS_SEARCH_COMPLETE');
 eq(final.totalResults===96&&final.results.length===96,'V11_PROGRESS_SEARCH_ALL_MATCHES');
 eq(final.scanned>=96&&seenScanned>=96,'V11_PROGRESS_SEARCH_SCANNED');
 eq(Number.isInteger(final.firstResultAt)&&Number.isInteger(final.completedAt)&&final.firstResultAt<=final.completedAt,'V11_STREAMED_BEFORE_COMPLETION');
 eq(partial||final.firstResultAt<final.completedAt,'V11_PROGRESS_PUBLICATION_DURING_SCAN');
 r=await tool('get_more_search_results',{sessionId:sid,offset:92,length:10});
 eq(!r.isError&&r.value.results.length===4&&r.value.nextOffset===96,'V11_PROGRESS_PAGINATED_TAIL');
 r=await tool('start_search',{path:'v11-progress-fixtures',pattern:marker,searchType:'content',literalSearch:true,maxResults:120,filePattern:'v11scan-*.txt'});
 eq(!r.isError,'V11_CANCELLABLE_SEARCH_LAUNCH');
 const stopId=r.value.sessionId;
 let presults=0;
 for(let i=0;i<45;i++){
  await new Promise(x=>setTimeout(x,35));
  const q=await tool('get_more_search_results',{sessionId:stopId,length:100});
  if(q.isError)throw Error('Cancel poll failed');
  presults=q.value.totalResults;
  if(q.value.running===true || (q.value.status==='running'&&presults>0))break;
  if(q.value.complete)break;
 }
 let stop=await tool('stop_search',{sessionId:stopId});
 eq(!stop.isError,'V11_STOP_SEARCH_REQUEST_HANDLED');
 let cancelled;
 for(let i=0;i<50;i++){
  await new Promise(x=>setTimeout(x,80));
  cancelled=await tool('get_more_search_results',{sessionId:stopId,length:100});
  if(cancelled.value.complete)break;
 }
 console.log('V11_STOP_RESULT',JSON.stringify({status:cancelled.value.status,total:cancelled.value.totalResults,stopped:stop.value.terminationRequested,complete:cancelled.value.complete}));
 eq(!cancelled.isError&&cancelled.value.complete&&cancelled.value.totalResults>=presults,'V11_STOP_RETAINS_SEARCH_RESULTS');
 console.log('XOOM_V11_LARGE_EDIT_PROGRESS_SEARCH_HARDWARE_PASS');
})().catch(e=>{console.error('XOOM_V11_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});