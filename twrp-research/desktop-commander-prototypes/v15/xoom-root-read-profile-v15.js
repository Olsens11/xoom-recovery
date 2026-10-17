'use strict';
// Experimental v0.15 read-only root development profile.
// Direct argv execution: no shell, arbitrary programs, scripts or mutation.
const fs=require('node:fs');
const path=require('node:path');
const DEFAULT_DIR='/tmp/xoom-dc-runtime-qa/debian24';
const ALLOWED_BASES=['/tmp','/etc','/proc','/sys','/sbin','/system','/vendor','/mnt','/cache','/data','/external_sd','/storage'];
const SENSITIVE=/(?:shadow|password|passwd\.bak|private[_-]?key|credential|secret|token|adb_keys|authorized_keys|id_ed25519|id_rsa|device\.json|\.pem(?:$|\/)|\.p12(?:$|\/)|\.pfx(?:$|\/)|\.key(?:$|\/)|\/\.ssh\/|\/\.desktop-commander-device\/)/i;
const READ_CAP=65536,HASH_CAP=33554432;
function deny(msg){throw Error('ROOT_READ_POLICY_DENIED: '+msg)}
function tokens(command){
 if(typeof command!=='string'||!command.startsWith('root ')||command.length>400)deny('Command must start with root, max 400 characters');
 const body=command.slice(5).trim();
 if(!body||/[\x00-\x1f\x7f]/.test(body)||body.includes(String.fromCharCode(96))||
    /[;&|<>$\\'"(){}!*?[\]~]/.test(body))deny('No control characters, quotes, shell syntax, globbing or substitutions');
 const a=body.split(/ +/);
 if(a.length>7||a.some(x=>!x||x.length>220))deny('Too many or invalid arguments');
 return a;
}
function safePath(p,{type='any',maxBytes=0,follow=false}={}){
 if(typeof p!=='string'||!p.startsWith('/')||p==='/'||p.includes('//')||
    p.split('/').some(x=>x==='..'||x==='.'))deny('Path must be absolute, canonical and non-root');
 const resolved=path.posix.normalize(p);
 if(resolved!==p||!ALLOWED_BASES.some(b=>p===b||p.startsWith(b+'/')))deny('Path is outside known recovery paths');
 const parts=p.split('/').filter(Boolean);
 let check='';
 for(const part of parts){
  check+='/'+part;
  let st;
  try{st=fs.lstatSync(check)}catch(e){deny('Path missing or inaccessible')}
  if(st.isSymbolicLink()&&!(follow&&check===p))deny('Symbol links or symlink parent refused');
 }
 const st=fs.lstatSync(p);
 if(type==='file'&&!st.isFile())deny('Only regular files may be read as content');
 if(type==='dir'&&!st.isDirectory())deny('Expected directory');
 if(type==='symlink'&&!st.isSymbolicLink())deny('Expected symlink');
 if(maxBytes&&st.size>maxBytes)deny('File is larger than the read-only profile limit');
 if(type==='file'&&SENSITIVE.test(p))deny('Credential/sensitive file requires separate reviewed action');
 if(st.isBlockDevice()||st.isCharacterDevice()||st.isFIFO()||st.isSocket())deny('Device or special file content prohibited');
 return p;
}
function expect(args,allow){if(!allow.includes(args.join(' ')))deny('Arguments not on read-only list')}
function exactEmpty(a){if(a.length!==0)deny('Unexpected flags or arguments')}
function parseOnePath(a,opts={}){if(a.length!==1)deny('One absolute target path required');return safePath(a[0],opts)}
function createRootReadPlan(command){
 const [name,...a]=tokens(command);
 const exe='/sbin/busybox';
 let argv,expected='read-only',target=null,category='read-only root diagnostic',binary=exe;
 switch(name){
  case 'id':case 'uptime':case 'dmesg':case 'mount':case 'ps':
   exactEmpty(a);argv=[name];break;
  case 'uname':expect(a,['','-a','-r','-m','-s']);argv=[name,...a];break;
  case 'date':expect(a,['','-u']);argv=[name,...a];break;
  case 'free':expect(a,['','-m']);argv=[name,...a];break;
  case 'df':expect(a,['','-h']);argv=[name,...a];break;
  case 'ls':{
   let flags=[];
   if(a[0]?.startsWith('-'))flags.push(a.shift());
   if(flags.length&&!['-l','-a','-la','-al','-ld','-dl','-d','-lh','-hl'].includes(flags[0]))deny('Disallowed ls flags');
   target=a.length===0?DEFAULT_DIR:parseOnePath(a);
   argv=['ls',...flags,target];break;
  }
  case 'stat':case 'sha256sum':case 'cat':case 'readlink':{
   let opts=name==='sha256sum'?{type:'file',maxBytes:HASH_CAP}:
    name==='cat'?{type:'file',maxBytes:READ_CAP}:
    name==='readlink'?{type:'symlink',follow:true}:{};
   target=parseOnePath(a,opts);
   if(name==='cat'&&target.startsWith('/proc/'))deny('No pseudo-file streaming from procfs');
   if(name==='sha256sum'&&(target.startsWith('/proc/')||target.startsWith('/sys/')))deny('No unbounded pseudo-file hashing');
   argv=[name,target];break;
  }
  case 'head':case 'tail':{
   let n='40';
   if(a.length===3&&a[0]==='-n'){
    n=a[1];
    if(!/^[1-9][0-9]{0,2}$/.test(n)||Number(n)>120)deny('Maximum 120 output lines');
    a.splice(0,2);
   }
   target=parseOnePath(a,{type:'file',maxBytes:READ_CAP});
   if(target.startsWith('/proc/'))deny('No pseudo-file streaming from procfs');
   argv=[name,'-n',n,target];break;
  }
  case 'grep':{
   let flags=[];
   while(a[0]?.startsWith('-')&&flags.length<2){
    let f=a.shift();
    if(!['-n','-F','-i'].includes(f)||flags.includes(f))deny('Unsupported grep option');
    flags.push(f);
   }
   if(a.length!==2||a[0].length>100)deny('grep requires one pattern and one file');
   const pattern=a[0];
   if(pattern.startsWith('-')||!(/^[A-Za-z0-9_.,:+\-\/]+$/).test(pattern))deny('Use bounded literal search pattern');
   target=safePath(a[1],{type:'file',maxBytes:READ_CAP});
   if(target.startsWith('/proc/'))deny('No procfs content search');
   argv=['grep',...flags,'-F',pattern,target];break;
  }
  case 'getprop':{
   if(a.length>1||a.length===1&&!/^[A-Za-z0-9_.-]{1,100}$/.test(a[0]))deny('getprop expects optional property name');
   binary='/system/bin/getprop';
   const st=fs.lstatSync(binary);
   if(!st.isFile()||st.uid!==0||(st.mode&0o022)!==0)deny('Cannot trust system getprop executable');
   argv=a;break;
  }
  default:deny('Unknown or modifying root command; no shell or executable fallback');
 }
 return Object.freeze({executable:binary,argv:Object.freeze(argv),profile:'rootread',
  uid:0,gid:0,readOnly:true,timeoutMs:12000,target,
  audit:{command,action:name,category,expectedEffects:expected,
  note:'No shell; fixed binaries and validated argv. Not a complete kernel sandbox.'}});
}
module.exports={createRootReadPlan};