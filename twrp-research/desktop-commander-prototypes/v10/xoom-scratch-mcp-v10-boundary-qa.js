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
 let r;const fn='v10-upper-bound.js';let full='';
 for(let k=0;k<8;k++){
  const p=Array.from({length:300},(_,i)=>'// SAFE_PRIVATE_SOURCE_'+k+'_'+i+'_'+ 'X'.repeat(72)+'\n').join('');
  eq(Buffer.byteLength(p,'utf8')<=32768,'V10_STRESS_CHUNK_FITS_'+k);
  full+=p;
  r=await tool('write_file',{path:fn,content:p,mode:k?'append':'rewrite'});
  eq(!r.isError,'V10_STRESS_APPEND_'+k);
 }
 const size=Buffer.byteLength(full,'utf8');
 console.log('V10_STRESS_SOURCE_BYTES',size);
 eq(size>=230000&&size<=262144,'V10_STRESS_NEAR_256K');
 r=await tool('write_file',{path:fn,content:'//OVER_LIMIT\n'+'Y'.repeat(30000),mode:'append'});
 eq(r.isError,'V10_256K_HARD_LIMIT_REJECTED');
 r=await tool('get_file_info',{path:fn});
 eq(!r.isError&&r.value.size===size,'V10_REJECTED_APPEND_PRESERVES_BYTES');
 r=await tool('start_process',{command:'dev check '+fn});
 console.log('V10_STRESS_CHECK_STARTED',JSON.stringify(r));
 eq(!r.isError&&r.value.profile==='check','V10_STRESS_CHECK_LAUNCHED');
 const digest=require('node:crypto').createHash('sha256').update(full).digest('hex');
 eq(r.value.sourceSha256===digest,'V10_STRESS_HASHED_IMMUTABLE_SNAPSHOT');
 let o;
 for(let i=0;i<80;i++){await new Promise(v=>setTimeout(v,140));o=await tool('read_process_output',{pid:r.value.pid,offset:-20,length:20});if(!o.value.running)break;}
 console.log('V10_STRESS_CHECK_RESULT',JSON.stringify(o));
 eq(!o.isError&&!o.value.running&&o.value.exitCode===0,'V10_NEAR_LIMIT_NODE_SYNTAX_PASS');
 console.log('XOOM_V10_256K_BOUNDARY_HARDWARE_PASS');
})().catch(e=>{console.error('XOOM_V10_BOUNDARY_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});