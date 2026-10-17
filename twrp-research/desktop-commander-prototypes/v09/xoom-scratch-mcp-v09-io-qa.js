'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v09-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const init=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(init.result?.serverInfo?.version==='0.9.0-local','V09_SERVER_IDENTITY');
 const list=await request('tools/list',{});
 eq(list.result.tools.length===26,'V09_TOOL_COUNT_26');
 let r=await tool('get_config',{});
 eq(!r.isError&&r.value.extendedTextLimitBytes===262144&&r.value.imageReadLimitBytes===61440&&r.value.supportsMcpImageBlocks,'V09_CONFIG_LIMITS');
 const name='v09largefile.js';
 let expected='';
 for(let segment=0;segment<6;segment++){
  const text=Array.from({length:400},(_,i)=>{
   const line=segment*400+i;
   return 'SOURCE_LINE_'+String(line).padStart(5,'0')+'_FRAMEBUFFER_PREVIEW_COMPONENT_ALPHA\n';
  }).join('');
  expected+=text;
  r=await tool('write_file',{path:name,content:text,mode:segment?'append':'rewrite'});
  eq(!r.isError&&r.value.chunkBytes>10000,'V09_CHUNK_APPEND_'+segment);
 }
 const count=Buffer.byteLength(expected,'utf8');
 eq(count>32768&&count<262144,'V09_SOURCE_EXCEEDS_OLD_LIMIT');
 r=await tool('get_file_info',{path:name});
 eq(!r.isError&&r.value.size===count,'V09_EXTENDED_FILE_INFO');
 r=await tool('read_file',{path:name,offset:2180,length:5});
 eq(!r.isError&&r.value.text.includes('SOURCE_LINE_02180_')&&r.value.text.includes('SOURCE_LINE_02184_')&&r.value.fileBytes===count,'V09_PAGED_DEEP_SOURCE_READ');
 r=await tool('read_file',{path:name,offset:-1,length:1});
 eq(!r.isError&&r.value.text===''&&r.value.totalLines===2401,'V09_TAIL_PAGINATION');
 r=await tool('read_file',{path:name,length:200});
 eq(!r.isError&&r.value.text.startsWith('SOURCE_LINE_00000_'),'V09_FRONT_PAGING');
 r=await tool('write_file',{path:name,content:'ACCIDENTAL_TRUNCATE'});
 eq(r.isError,'V09_EXPLICIT_OVERWRITE_SAFETY');
 r=await tool('get_file_info',{path:name});
 eq(!r.isError&&r.value.size===count,'V09_ORIGINAL_AFTER_DENIAL');
 r=await tool('write_file',{path:'v09overlong.txt',content:'X'.repeat(20000),mode:'rewrite'});
 eq(!r.isError,'V09_LONG_LINE_FIXTURE');
 r=await tool('read_file',{path:'v09overlong.txt',length:1});
 eq(r.isError,'V09_PER_RESPONSE_16K_CAP_ENFORCED');
 r=await tool('write_file',{path:'v09oversized.txt',content:'x'.repeat(32769)});
 eq(r.isError,'V09_SINGLE_CHUNK_BOUND');
 let raw=await request('tools/call',{name:'read_file',arguments:{path:'v09-display-fixture.png'}});
 const m=raw.result;
 console.log('V09_IMAGE_MCP_META',JSON.stringify({types:m?.content?.map(x=>x.type),mime:m?.content?.[1]?.mimeType,meta:m?.structuredContent,bytes:m?.content?.[1]?.data?.length}));
 eq(!m?.isError&&m.content.length===2&&m.content[0].type==='text'&&m.content[1].type==='image','V09_NATIVE_MCP_IMAGE_BLOCK');
 eq(m.content[1].mimeType==='image/png'&&Buffer.from(m.content[1].data,'base64').subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])),'V09_PNG_FORMAT_VERIFIED');
 eq(m.structuredContent?.fileType==='image'&&m.structuredContent.bytes===377&&m.structuredContent.width===16&&m.structuredContent.height===16,'V09_IMAGE_STRUCTURED_METADATA');
 raw=await request('tools/call',{name:'read_file',arguments:{path:'v09-oversized-canvas.png'}});
 eq(raw.result?.isError===true,'V09_IMAGE_DIMENSION_BOMB_DENIED');
 raw=await request('tools/call',{name:'read_file',arguments:{path:'v09-spoofed-image.jpg'}});
 eq(raw.result?.isError===true,'V09_REJECT_MISMATCHED_IMAGE_MAGIC');
 raw=await request('tools/call',{name:'read_file',arguments:{path:'../../etc/shadow'}});
 eq(raw.result?.isError===true,'V09_REJECT_PATH_ESCAPE');
 r=await tool('read_file',{path:name,length:0});
 eq(!r.isError&&r.value.text===''&&r.value.totalLines===2401,'V09_ZERO_LENGTH_METADATA_QUERY');
 console.log('XOOM_V09_LARGE_TEXT_AND_NATIVE_IMAGE_HARDWARE_PASS');
})().catch(e=>{console.error('V09_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});