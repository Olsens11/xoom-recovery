'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v10-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const init=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(init.result.serverInfo.version==='0.10.0-local','V10_SERVER_IDENTITY');
 const names=await request('tools/list',{});
 eq(names.result.tools.length===26,'V10_26_TOOLS');
 let r=await tool('get_config',{});
 eq(!r.isError&&r.value.largeScriptLimitBytes===262144&&r.value.mixedMultiFileReads===true&&r.value.largeSourceSearch===true,'V10_CAPABILITY_DISCLOSURE');
 const fn='v10-deep-source.js';
 const marker='UNIQUE_DEEP_SEARCH_V10_7F3AC';
 let source='';
 for(let part=0;part<6;part++){
  let piece='';
  for(let i=0;i<270;i++){
   const n=part*270+i;
   const v=n===1550?marker:'standard private source fixture';
   piece+='// source_line_'+String(n).padStart(5,'0')+' '+v+' word word word word word word\n';
  }
  if(part===5)piece+="console.log('V10_LARGE_SCRIPT_OK',process.getuid());\n";
  source+=piece;
  r=await tool('write_file',{path:fn,content:piece,mode:part?'append':'rewrite'});
  eq(!r.isError&&r.value.chunkBytes<=32768,'V10_LARGE_SCRIPT_CHUNK_'+part);
 }
 const bytes=Buffer.byteLength(source,'utf8');
 eq(bytes>100000&&bytes<262144,'V10_LARGE_SOURCE_OVER_100K');
 r=await tool('get_file_info',{path:fn});
 eq(!r.isError&&r.value.size===bytes,'V10_SOURCE_METADATA_SIZE');
 r=await tool('start_process',{command:'dev check '+fn});
 console.log('V10_DEV_CHECK_START',JSON.stringify(r));
 eq(!r.isError&&r.value.profile==='check'&&r.value.uid===2000,'V10_LARGE_SOURCE_CHECK_LAUNCH');
 const hash=require('node:crypto').createHash('sha256').update(source).digest('hex');
 eq(r.value.sourceSha256===hash,'V10_IMMUTABLE_SNAPSHOT_SOURCE_HASH');
 let checked;
 for(let k=0;k<55;k++){
  await new Promise(resolve=>setTimeout(resolve,160));
  checked=await tool('read_process_output',{pid:r.value.pid,offset:-18,length:18});
  if(!checked.value.running)break;
 }
 console.log('V10_CHECK_OUTCOME',JSON.stringify(checked));
 eq(!checked.value.running&&checked.value.exitCode===0,'V10_LARGE_SOURCE_SYNTAX_PASS');
 r=await tool('start_process',{command:'dev run '+fn});
 eq(!r.isError&&r.value.profile==='run'&&r.value.uid===2000&&r.value.sourceSha256===hash,'V10_LARGE_SOURCE_EXEC_LAUNCH');
 let executed;
 for(let k=0;k<80;k++){
  await new Promise(resolve=>setTimeout(resolve,170));
  executed=await tool('read_process_output',{pid:r.value.pid,offset:-25,length:25});
  if(!executed.value.running)break;
 }
 console.log('V10_RUN_OUTCOME',JSON.stringify(executed));
 eq(!executed.value.running&&executed.value.exitCode===0&&executed.value.output.includes('V10_LARGE_SCRIPT_OK 2000'),'V10_LARGE_SCRIPT_EXEC_UID2000');
 let raw=await request('tools/call',{name:'read_multiple_files',arguments:{paths:[fn,'v09-display-fixture.png','v10-not-found.txt']}});
 eq(!raw.result?.isError&&raw.result?.content?.length===2,'V10_MULTI_TEXT_IMAGE_BLOCKS');
 const summary=JSON.parse(raw.result.content[0].text);
 console.log('V10_MULTI_SUMMARY',JSON.stringify({files:summary.files.map(x=>({path:x.path,ok:x.ok,type:x.type,bytes:x.bytes,fileBytes:x.fileBytes,truncated:x.truncated,imageBlockIndex:x.imageBlockIndex})),totalBytes:summary.totalBytes}));
 eq(summary.requested===3&&summary.succeeded===2&&summary.failed===1,'V10_MULTI_PARTIAL_FAILURE_ISOLATED');
 eq(summary.files[0].type==='text'&&summary.files[0].truncated&&summary.files[0].fileBytes===bytes,'V10_MULTI_LARGE_FILE_PAGE_METADATA');
 eq(summary.files[1].type==='image'&&summary.files[1].imageBlockIndex===1&&raw.result.content[1].mimeType==='image/png','V10_MULTI_NATIVE_IMAGE_BLOCK');
 eq(raw.result.structuredContent.files[1].mimeType==='image/png'&&!raw.result.content[0].text.includes('iVBORw0KGgo'),'V10_MULTI_IMAGE_NOT_JSON_BASE64');
 r=await tool('start_search',{path:ROOT,pattern:marker,searchType:'content',filePattern:fn,literalSearch:true});
 eq(!r.isError&&!!r.value.sessionId,'V10_LARGE_SOURCE_SEARCH_START');
 let results;
 for(let k=0;k<55;k++){
  await new Promise(resolve=>setTimeout(resolve,180));
  results=await tool('get_more_search_results',{sessionId:r.value.sessionId});
  if(results.value.complete)break;
 }
 console.log('V10_DEEP_SEARCH',JSON.stringify(results?.value));
 eq(!results.isError&&results.value.complete&&!results.value.error,'V10_SEARCH_COMPLETED');
 eq(results.value.results.some(x=>x.relativePath===fn&&x.line===1551&&x.match.includes(marker)),'V10_DEEP_MATCH_AFTER_32K');
 const bad=await tool('start_process',{command:'dev run ../../bad.js'});
 eq(bad.isError,'V10_SCRIPT_TRAVERSAL_COMMAND_REJECTED');
 console.log('XOOM_V10_LARGE_EXEC_MULTI_MEDIA_SEARCH_HARDWARE_PASS');
})().catch(e=>{console.error('XOOM_V10_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});