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
 const init=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(init.result.serverInfo.version==='0.15.0-local','CONTRACT_V15_VERSION');
 const list=await request('tools/list',{});
 eq(list.result.tools.length===27,'CONTRACT_TOOLS_27');
 const byName=Object.fromEntries(list.result.tools.map(v=>[v.name,v]));
 eq(byName.read_file.annotations.readOnlyHint===true,'CONTRACT_READ_ONLY_HINT');
 eq(byName.write_file.annotations.destructiveHint===true,'CONTRACT_WRITE_DESTRUCTIVE_HINT');
 eq(byName.start_process.annotations.openWorldHint===true,'CONTRACT_PROCESS_OPEN_WORLD_HINT');
 eq(byName.read_process_output.annotations.readOnlyHint===true,'CONTRACT_OUTPUT_READ_ONLY_HINT');
 eq(byName.list_directory.inputSchema.properties.depth.maximum===3,'CONTRACT_DIRECTORY_DEPTH_ADVERTISED');
 eq(byName.privileged_action.annotations.destructiveHint===true&&byName.privileged_action.inputSchema.properties.phase.enum.includes('preflight'),'CONTRACT_PRIVILEGED_EXTENSION_DECLARED');
 const c=await request('tools/call',{name:'get_config',arguments:{}});
 const meta=c.result.structuredContent;
 eq(!!meta&&meta.config.version==='xoom-scratch-dev-v0.15-LOCAL-ONLY'&&meta.entries.length===3,'CONTRACT_STRUCTURED_CONFIG');
 eq(c.result.content?.[0]?.text?.includes('xoom-scratch-dev-v0.15-LOCAL-ONLY'),'CONTRACT_TEXT_CONFIG_PRESERVED');
 console.log('XOOM_V15_MCP_METADATA_CONTRACT_PASS');
})().catch(e=>{console.error('V15_META_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});