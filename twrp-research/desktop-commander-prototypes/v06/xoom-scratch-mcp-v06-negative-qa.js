'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v06-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const init=await request('initialize',{protocolVersion:'2025-06-18'});eq(init.result.serverInfo.version==='0.6.0-local','NEGATIVE_V06_VERSION');
 const tools=await request('tools/list',{});eq(tools.result.tools.length===26,'NEGATIVE_V06_TOOLS');
 let a;
 a=await tool('create_directory',{path:'v06proj/badlink/new'});eq(a.isError,'NEGATIVE_SYMLINK_CREATE');
 a=await tool('read_file',{path:'v06proj/badlink/passwd'});eq(a.isError,'NEGATIVE_SYMLINK_READ');
 a=await tool('write_file',{path:'v06proj/badlink/new.txt',content:'NEVER_TOUCH_OUTSIDE'});eq(a.isError,'NEGATIVE_SYMLINK_WRITE');
 a=await tool('start_search',{path:'v06proj/badlink',pattern:'passwd',searchType:'files'});eq(a.isError||!!a.value.sessionId,'NEGATIVE_SYMLINK_SEARCH_REQUEST');
 if(!a.isError){const sid=a.value.sessionId;for(let j=0;j<25;j++){await new Promise(q=>setTimeout(q,230));a=await tool('get_more_search_results',{sessionId:sid});if(a.value.complete)break;}eq(a.value.status==='error'&&a.value.totalResults===0,'NEGATIVE_SYMLINK_SEARCH_FAILED');}
 a=await tool('move_file',{source:'v06proj/badlink',destination:'v06proj/moved-link'});eq(a.isError,'NEGATIVE_SYMLINK_MOVE');

 a=await tool('read_multiple_files',{paths:['v06proj/badlink/passwd','v06proj/renamed.js']});
 eq(!a.isError&&a.value.requested===2&&!a.value.files[0].ok&&a.value.files[1].ok&&a.value.files[1].content.includes('PROJECT_BETA'),'NEGATIVE_V06_MULTI_SYMLINK_READ_REJECTED');
 a=await tool('write_pdf',{path:'v06proj/badlink/fake.pdf',content:'# Should never escape'});eq(a.isError,'NEGATIVE_V06_PDF_SYMLINK_CREATE_REJECTED');
 a=await tool('write_pdf',{path:'v06proj/../bad.pdf',content:'bad'});eq(a.isError,'NEGATIVE_V06_PDF_TRAVERSAL_REJECTED');
 a=await tool('create_directory',{path:'v06proj/../outside'});eq(a.isError,'NEGATIVE_TRAVERSAL_CREATE');
 a=await tool('start_search',{path:ROOT,pattern:'secret',includeHidden:true});eq(a.isError,'NEGATIVE_UNSUPPORTED_HIDDEN_EXPLICIT');
 a=await tool('start_search',{path:ROOT,pattern:'file',earlyTermination:true});eq(a.isError,'NEGATIVE_UNSUPPORTED_EARLY_EXIT_EXPLICIT');
 a=await tool('move_file',{source:'v06proj/renamed.js',destination:'v06proj/src/renamed.js'});eq(!a.isError,'NEGATIVE_MOVE_FIRST');
 a=await tool('move_file',{source:'v06proj/src/renamed.js',destination:'v06proj/src/renamed.js'});eq(a.isError,'NEGATIVE_MOVE_SELF');
 a=await tool('move_file',{source:'v06proj/src/renamed.js',destination:'v06proj/src/renamed.js'});eq(a.isError,'NEGATIVE_NO_OVERWRITE');
 a=await tool('move_file',{source:'v06proj/src/renamed.js',destination:'v06proj/renamed.js'});eq(!a.isError,'NEGATIVE_MOVE_RESTORE');
 console.log('XOOM_V06_DIRECTORY_SECURITY_NEGATIVE_PASS');
})().catch(e=>{console.error('XOOM_V06_DIRECTORY_SECURITY_NEGATIVE_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});