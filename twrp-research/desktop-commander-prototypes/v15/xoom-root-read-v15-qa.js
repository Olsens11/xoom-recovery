'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v15-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const fixture=D+'/v15-protected-inspection.txt', symlink=D+'/v15-symbolic-fixture.txt',secret=D+'/v15-root-secret-token.txt';
for(const p of [fixture,symlink,secret])try{fs.unlinkSync(p)}catch{}
const txt='XOOM_V15_ROOT_READ_TEST\nTEST-LINE-TWO\n';
fs.writeFileSync(fixture,txt,{mode:0o600});fs.chownSync(fixture,0,0);fs.chmodSync(fixture,0o600);
fs.writeFileSync(secret,'SECRET_DO_NOT_EXPOSE\n',{mode:0o600});
fs.symlinkSync(fixture,symlink);
const hash=crypto.createHash('sha256').update(txt).digest('hex');
function check(v,label){eq(v,label)}
async function start(command){
 const t=await tool('start_process',{command});
 if(t.isError)throw Error('START_FAILED '+command+': '+JSON.stringify(t.value));
 check(t.value.profile==='rootread'&&t.value.uid===0&&t.value.limitMs===12000&&t.value.readOnlyRoot===true,'V15_ROOT_PROFILE_DISPATCH');
 const pid=t.value.pid;
 let x;
 for(let i=0;i<30;i++){
  await new Promise(r=>setTimeout(r,60));
  x=await tool('read_process_output',{pid,offset:-90,length:90});
  if(x.isError)throw Error('output read failure '+JSON.stringify(x.value));
  if(!x.value.running)break;
 }
 check(!x.value.running&&x.value.exitCode===0,'V15_ROOT_COMMAND_EXIT0');
 return x.value.output;
}
async function denied(command,label){let r=await tool('start_process',{command});check(r.isError,label);console.log(label+'_ERR',String(r.value.error||'').slice(0,130))}
try{
 let init=await request('initialize',{protocolVersion:'2025-06-18'});
 check(init.result.serverInfo.version==='0.15.0-local','V15_VERSION');
 let list=await request('tools/list',{});
 check(list.result.tools.length===27,'V15_TOOL_COUNT_COMPAT');
 const conf=await tool('get_config',{});
 check(conf.value.readOnlyRootDevelopment.enabled===true&&conf.value.privilegedOneShotGate.enabled===false,'V15_ROOT_READ_NO_SIGNED_WRITE');
 let out=await start('root id');check(out.includes('uid=0(root)'),'V15_DIRECT_ROOT_ID');
 out=await start('root sha256sum '+fixture);check(out.includes(hash),'V15_PROTECTED_ROOT_SHA256');
 out=await start('root cat '+fixture);check(out.includes('XOOM_V15_ROOT_READ_TEST'),'V15_PROTECTED_ROOT_FILE_READ');
 out=await start('root stat '+fixture);check(out.includes('Size:')||out.includes('File:'),'V15_ROOT_STAT');
 out=await start('root ls -l '+fixture);check(out.includes('v15-protected-inspection.txt'),'V15_ROOT_LS');
 out=await start('root head -n 1 '+fixture);check(out.includes('XOOM_V15_ROOT_READ_TEST'),'V15_ROOT_HEAD');
 out=await start('root grep -n TEST-LINE-TWO '+fixture);check(out.includes('TEST-LINE-TWO'),'V15_ROOT_GREP');
 out=await start('root uname -a');check(out.includes('Linux'),'V15_ROOT_KERNEL_DIAGNOSTIC');
 out=await start('root mount');check(out.length>10,'V15_ROOT_MOUNT_READONLY');
 await denied('root rm '+fixture,'V15_MODIFY_COMMAND_DENIED');
 await denied('root sh -c id','V15_SHELL_FLAG_DENIED');
 await denied('root id;rm','V15_CHAINING_DENIED');
 await denied('root cat /dev/zero','V15_SPECIAL_DEVICE_DENIED');
 await denied('root cat '+symlink,'V15_SYMLINK_DENIED');
 await denied('root cat '+secret,'V15_SECRET_DENIED');
 await denied('root cat /proc/uptime','V15_PROC_STREAM_DENIED');
 await denied('root ls -R '+D,'V15_RECURSIVE_SCAN_DENIED');
 await denied('root sha256sum /dev/block/mmcblk0','V15_BLOCK_DEVICE_DENIED');
 const t=fs.readFileSync(fixture,'utf8');check(t===txt,'V15_READONLY_TARGET_UNCHANGED');
 console.log('XOOM_V15_ROOT_READ_DEVELOPMENT_PHYSICAL_QA_PASS');
}finally{
 for(const p of [symlink,secret,fixture])try{fs.unlinkSync(p)}catch{}
}
})().catch(e=>{console.error('V15_ROOT_READ_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});