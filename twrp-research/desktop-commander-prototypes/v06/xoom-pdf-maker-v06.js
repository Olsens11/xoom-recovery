'use strict';
// RAM-only v0.6 PDF creator, dedicated to the UID/GID 2000 filesystem worker.
// No scripts, fonts, URL fetches, or external processes.
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const fsp=fs.promises,F=fs.constants,UID=2000;
function esc(t){return t.replaceAll('\\','\\\\').replaceAll('(','\\(').replaceAll(')','\\)')}
function printable(s){
 // Standard PDF Base-14 Helvetica in ASCII subset. Explicitly reject rather than corrupt Unicode.
 if(typeof s!=='string'||/[^ \n\r\t\x21-\x7e]/.test(s))throw Error('PDF v0.6 supports printable ASCII, tabs and newlines only');
 return s.replace(/\r\n?/g,'\n');
}
function linesOf(markdown){
 const content=printable(markdown);
 if(Buffer.byteLength(content,'utf8')>16384)throw Error('PDF markdown limited to 16KiB');
 const result=[];
 for(const raw of content.split('\n')){
  const h=raw.match(/^(#{1,3})\s+(.*)$/);
  let size=h?Math.max(13,19-h[1].length*2):11;
  let txt=h?h[2]:raw.replace(/^\s*[-*]\s+/,'- ').replace(/^\s*\d+\.\s+/,'1. ');
  // Plain text formatting only: cannot promise markdown engine parity.
  txt=txt.replace(/\*\*([^*]+)\*\*/g,'$1').replace(/__([^_]+)__/g,'$1').replace(/\*([^*]+)\*/g,'$1').replace(/_([^_]+)_/g,'$1');
  const width=size>11?57:88;
  if(!txt){result.push({text:'',size});continue}
  while(txt.length){
   if(txt.length<=width){result.push({text:txt,size});break}
   let at=txt.lastIndexOf(' ',width);
   if(at<10)at=width;
   result.push({text:txt.slice(0,at).trimEnd(),size});
   txt=txt.slice(at).trimStart();
  }
 }
 return result;
}
function buildPdf(markdown){
 const all=linesOf(markdown);
 const pageSize=49,groups=[];
 for(let k=0;k<all.length;k+=pageSize)groups.push(all.slice(k,k+pageSize));
 if(groups.length<1)groups.push([]);
 if(groups.length>8)throw Error('PDF limited to eight pages');
 const objs=[null];
 const add=(v)=>{objs.push(v);return objs.length-1};
 const catalog=add(null),pages=add(null),font=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
 const kids=[];
 for(const g of groups){
  let y=750,ops=['BT'];
  for(const line of g){
   const size=line.size;
   ops.push('/F1 '+size+' Tf');
   ops.push('1 0 0 1 52 '+y+' Tm');
   ops.push('('+esc(line.text)+') Tj');
   y-=size>11?23:14;
  }
  ops.push('ET');
  const stream=ops.join('\n')+'\n';
  const len=Buffer.byteLength(stream,'ascii');
  const streamId=add('<< /Length '+len+' >>\nstream\n'+stream+'endstream');
  const pageId=add('<< /Type /Page /Parent '+pages+' 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 '+font+' 0 R >> >> /Contents '+streamId+' 0 R >>');
  kids.push(pageId+' 0 R');
 }
 objs[catalog]='<< /Type /Catalog /Pages '+pages+' 0 R >>';
 objs[pages]='<< /Type /Pages /Kids ['+kids.join(' ')+'] /Count '+kids.length+' >>';
 let out='%PDF-1.4\n',offsets=[0];
 for(let i=1;i<objs.length;i++){
  offsets[i]=Buffer.byteLength(out,'ascii');
  out+=i+' 0 obj\n'+objs[i]+'\nendobj\n';
 }
 const xref=Buffer.byteLength(out,'ascii');
 out+='xref\n0 '+objs.length+'\n0000000000 65535 f \n';
 for(let i=1;i<objs.length;i++)out+=String(offsets[i]).padStart(10,'0')+' 00000 n \n';
 out+='trailer\n<< /Size '+objs.length+' /Root '+catalog+' 0 R >>\nstartxref\n'+xref+'\n%%EOF\n';
 return {bytes:Buffer.from(out,'ascii'),pages:groups.length,layout:'basic-ASCII-Markdown'};
}
async function make(arg,check){
 if(arg.outputPath!==undefined&&arg.outputPath!==arg.path)throw Error('Existing-PDF edit/outputPath not supported in v0.6');
 if(arg.options&&Object.keys(arg.options).length)throw Error('PDF options not yet implemented');
 if(typeof arg.content!=='string')throw Error('Only Markdown-to-new-PDF string content is supported');
 const p=await check(arg.path);
 if(!p.rel.toLowerCase().endsWith('.pdf'))throw Error('Destination must end .pdf');
 const pdf=buildPdf(arg.content);
 if(pdf.bytes.length>65536)throw Error('PDF output too large');
 try{
  const st=await fsp.lstat(p.full);
  if(!st.isFile()||st.uid!==UID||st.gid!==UID||st.nlink!==1||(st.mode&0o777)!==0o600)throw Error('Existing PDF not a private owned file');
 }catch(e){if(e.code!=='ENOENT')throw e}
 const tmp=path.join(path.dirname(p.full),'.pdf-'+crypto.randomBytes(8).toString('hex'));
 const fh=await fsp.open(tmp,F.O_CREAT|F.O_EXCL|F.O_WRONLY|F.O_NOFOLLOW,0o600);
 try{await fh.writeFile(pdf.bytes);await fh.sync()}finally{await fh.close()}
 try{await fsp.rename(tmp,p.full)}catch(e){await fsp.unlink(tmp).catch(()=>{});throw e}
 return {file:p.rel,bytes:pdf.bytes.length,pages:pdf.pages,layout:pdf.layout,format:'application/pdf'};
}
module.exports={buildPdf,make};