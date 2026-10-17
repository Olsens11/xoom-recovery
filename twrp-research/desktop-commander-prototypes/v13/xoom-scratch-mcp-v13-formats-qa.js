'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v13-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const info=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(info.result.serverInfo.version==='0.13.0-local','V13_FILEFORMATS_VERSION');
 const cases=[
 {file:'v13-structured.csv',data:'name,count,note\n"first, row",7,"quoted ""value"""\nsecond,8,plain\n'},
 {file:'v13-structured.tsv',data:'name\tcount\nAlice\t2\nBob\t4\n'},
 {file:'v13-structured.json',data:'{"ok":true,"items":[1,2],"nested":{"value":"sample"}}\n'},
 {file:'v13-invalid.json',data:'{"broken":'}
 ];
 for(const c of cases){
  const out=await tool('write_file',{path:c.file,content:c.data,mode:'rewrite'});
  eq(!out.isError,'V13_STAGED_'+c.file);
 }
 let v=await request('tools/call',{name:'read_file',arguments:{path:'v13-structured.csv'}});
 const csv=v.result.structuredContent;
 eq(!v.result.isError&&csv.formatPreview.format==='csv'&&csv.formatPreview.headers.join(',')==='name,count,note','V13_CSV_HEADERS_STRUCTURED');
 eq(csv.formatPreview.rows[0][0]==='first, row'&&csv.formatPreview.rows[0][2]==='quoted "value"','V13_CSV_RFC4180_QUOTING');
 eq(csv.formatPreview.rows[1][0]==='second'&&v.result.content[0].text.includes('first, row'),'V13_CSV_LEGACY_TEXT_PRESERVED');
 v=await request('tools/call',{name:'read_file',arguments:{path:'v13-structured.tsv'}});
 eq(!v.result.isError&&v.result.structuredContent.formatPreview.format==='tsv'&&v.result.structuredContent.formatPreview.rows[0][1]==='2','V13_TSV_STRUCTURED');
 v=await request('tools/call',{name:'read_file',arguments:{path:'v13-structured.json'}});
 eq(!v.result.isError&&v.result.structuredContent.formatPreview.format==='json'&&v.result.structuredContent.formatPreview.value.nested.value==='sample','V13_JSON_STRUCTURED');
 v=await request('tools/call',{name:'read_file',arguments:{path:'v13-invalid.json'}});
 eq(!v.result.isError&&v.result.structuredContent.formatPreview.parseError===true,'V13_INVALID_JSON_GRACEFUL');
 v=await request('tools/call',{name:'get_file_info',arguments:{path:'v13-structured.csv'}});
 eq(!v.result.isError&&v.result.structuredContent.sha256?.length===64,'V13_STRUCTURED_FILE_HASH_RETAINED');
 console.log('XOOM_V13_STRUCTURED_FORMATS_HARDWARE_PASS');
})().catch(e=>{console.error('V13_FORMATS_FAIL',e.stack);process.exitCode=1}).finally(()=>{child.stdin.end();setTimeout(()=>child.kill(),250).unref()});