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
 const r=await tool('start_search',{path:'v11-progress-fixtures',pattern:'V11_INCREMENTAL_SEARCH_MARKER_92E',searchType:'content',literalSearch:true,maxResults:120,filePattern:'v11scan-*.txt'});
 eq(!r.isError,'STREAM_RETRY_START');
 let live=false,final;
 for(let i=0;i<90;i++){
  await new Promise(x=>setTimeout(x,100));
  const x=await tool('get_more_search_results',{sessionId:r.value.sessionId,offset:0,length:100});
  if(x.isError)throw Error('Poll failed');
  if(x.value.status==='running'&&x.value.results.length)live=true;
  if(x.value.complete){final=x.value;break}
 }
 console.log('STREAM_RETRY_RESULT',JSON.stringify({live,status:final?.status,total:final?.totalResults,scanned:final?.scanned,first:final?.firstResultAt,end:final?.completedAt,error:final?.error}));
 eq(!!final&&final.status==='completed'&&final.totalResults===96,'STREAM_RETRY_ALL_FILES');
 eq(live||final.firstResultAt<final.completedAt,'STREAM_RETRY_TRULY_INCREMENTAL');
 console.log('V11_STREAM_RETRY_PASS');
})().catch(e=>{console.error('V11_STREAM_RETRY_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});