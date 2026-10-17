'use strict';
// Motorola Xoom R22d4q v0.14 privileged action gate — RAM-only experimental.
// Host approval public key must be root-owned and externally provisioned.
// No general shell, arbitrary executable, path or flag support.
const fs=require('node:fs');
const crypto=require('node:crypto');
const {spawn}=require('node:child_process');
const path=require('node:path');
const MAX_PENDING=4,PROPOSAL_LIFETIME_MS=120000,MAX_ACTION_MS=4000;
function createGate({sourcePath,trustKeyPath}){
 if(typeof sourcePath!=='string'||!sourcePath.endsWith('/xoom-scratch-mcp-v15-candidate.js'))
  throw Error('Privileged gate requires pinned v0.14 controller');
 if(typeof trustKeyPath!=='string'||!trustKeyPath.endsWith('/privileged-host-approval.pub'))
  throw Error('Privileged gate requires fixed trust anchor');
 const pending=new Map();
 const consumed=new Set();
 const fixedExecutable='/sbin/busybox';
 const ACTION='verify_controller_integrity';
 function regularRootFile(p,size){
  const st=fs.lstatSync(p);
  if(!st.isFile()||st.uid!==0||st.gid!==0||st.nlink!==1||(st.mode&0o022)!==0||st.size>size||st.size<1)
   throw Error('PINNED_ROOT_FILE_INTEGRITY_DENIED');
  return st;
 }
 function executableDigest(){
  regularRootFile(fixedExecutable,2097152);
  return crypto.createHash('sha256').update(fs.readFileSync(fixedExecutable)).digest('hex');
 }
 function targetDigest(){
  regularRootFile(sourcePath,1048576);
  return crypto.createHash('sha256').update(fs.readFileSync(sourcePath)).digest('hex');
 }
 function operationRecord(){
  const sha256=targetDigest();
  return {action:ACTION,executable:fixedExecutable,executableSha256:executableDigest(),
    argv:['sha256sum',sourcePath],cwd:'/',effectiveUid:0,effectiveGid:0,
    target:sourcePath,targetSha256:sha256,sideEffects:'none expected (read-only)',
    risk:'low — protected file contents hashed locally; digest returned; root binary execution limited to one fixed executable',
    maximumRuntimeMs:MAX_ACTION_MS,maximumOutputBytes:1024,
    rollback:'not applicable: operation is read-only'};
 }
 function propose({action,reason,alternatives}={}){
  if(action!==ACTION)throw Error('PRIVILEGED_ACTION_NOT_ALLOWLISTED');
  if(typeof reason!=='string'||reason.trim().length<12||reason.length>500)throw Error('SPECIFIC_NEED_REQUIRED');
  if(!Array.isArray(alternatives)||alternatives.length<1||alternatives.length>5||
     alternatives.some(x=>typeof x!=='string'||x.trim().length<5||x.length>220))
   throw Error('UNPRIVILEGED_ALTERNATIVE_EVIDENCE_REQUIRED');
  for(const [id,item] of pending)if(item.expiry<Date.now())pending.delete(id);
  if(pending.size>=MAX_PENDING)throw Error('TOO_MANY_PENDING_PROPOSALS');
  const operation=operationRecord();
  const proposalId=crypto.randomUUID(),nonce=crypto.randomBytes(16).toString('hex');
  const expiry=Date.now()+PROPOSAL_LIFETIME_MS;
  const digest=crypto.createHash('sha256').update(JSON.stringify({proposalId,nonce,expiry,operation})).digest('hex');
  pending.set(proposalId,{proposalId,nonce,expiry,digest,operation,reason,alternatives,executing:false});
  return {status:'awaiting_verified_user_approval',proposalId,proposalDigest:digest,nonce,expiresAt:expiry,
    operation,reason,alternatives,
    approval:'Must be verifiably signed by the configured trusted external approver; conversation text alone does not authorize execution',
    approvalAvailable:trustedKeyStatus().available};
 }
 function trustedKeyStatus(){
  try{
   regularRootFile(trustKeyPath,2048);
   const k=crypto.createPublicKey(fs.readFileSync(trustKeyPath));
   if(k.asymmetricKeyType!=='ed25519')throw Error('Wrong key type');
   return {available:true,type:'Ed25519'};
  }catch{return {available:false,type:null}}
 }
 function approvalBytes(ticket){
  return Buffer.from(JSON.stringify({
   proposalId:ticket.proposalId,proposalDigest:ticket.proposalDigest,
   nonce:ticket.nonce,approvedUser:ticket.approvedUser,
   approvalSession:ticket.approvalSession,issuedAt:ticket.issuedAt,
   expiresAt:ticket.expiresAt
  }),'utf8');
 }
 function verifyTicket(p,ticket){
  if(!ticket||typeof ticket!=='object'||Array.isArray(ticket))throw Error('NO_VERIFIED_APPROVAL');
  for(const k of ['proposalId','proposalDigest','nonce','approvedUser','approvalSession','signature']){
   if(typeof ticket[k]!=='string'||ticket[k].length>256||!ticket[k].length)throw Error('INVALID_APPROVAL_FIELDS');
  }
  if(!Number.isSafeInteger(ticket.issuedAt)||!Number.isSafeInteger(ticket.expiresAt)||
     ticket.expiresAt<=Date.now()||ticket.expiresAt>p.expiry||ticket.issuedAt>Date.now()+10000||
     ticket.issuedAt<p.expiry-PROPOSAL_LIFETIME_MS-10000)throw Error('APPROVAL_EXPIRED_OR_INVALID');
  if(ticket.proposalId!==p.proposalId||ticket.proposalDigest!==p.digest||ticket.nonce!==p.nonce)
   throw Error('APPROVAL_NOT_BOUND_TO_PROPOSAL');
  if(!/^[a-zA-Z0-9_-]{3,100}$/.test(ticket.approvedUser)||!/^[a-zA-Z0-9_-]{3,100}$/.test(ticket.approvalSession))
   throw Error('INVALID_APPROVAL_IDENTITY');
  if(!/^[A-Za-z0-9+/]+={0,2}$/.test(ticket.signature)||ticket.signature.length>200)
   throw Error('INVALID_APPROVAL_SIGNATURE');
  regularRootFile(trustKeyPath,2048);
  const key=crypto.createPublicKey(fs.readFileSync(trustKeyPath));
  if(key.asymmetricKeyType!=='ed25519')throw Error('INVALID_TRUST_ANCHOR');
  if(!crypto.verify(null,approvalBytes(ticket),key,Buffer.from(ticket.signature,'base64')))
   throw Error('APPROVAL_SIGNATURE_REJECTED');
 }
 function preflight({proposalId,ticket}={}){
  if(typeof proposalId!=='string'||!pending.has(proposalId))throw Error('UNKNOWN_OR_CONSUMED_PROPOSAL');
  const p=pending.get(proposalId);
  if(Date.now()>p.expiry)throw Error('PROPOSAL_EXPIRED');
  if(!trustedKeyStatus().available)throw Error('TRUSTED_CHAT_APPROVAL_BRIDGE_UNAVAILABLE');
  verifyTicket(p,ticket);
  if(targetDigest()!==p.operation.targetSha256||executableDigest()!==p.operation.executableSha256)throw Error('PINNED_EXECUTABLE_OR_SOURCE_CHANGED');
  return {status:'signed_approval_preflight_passed',executionPerformed:false,proposalId,action:ACTION,expiresAt:p.expiry,readOnly:true};
 }
 async function execute({proposalId,ticket}={}){
  if(typeof proposalId!=='string'||!pending.has(proposalId))throw Error('UNKNOWN_OR_CONSUMED_PROPOSAL');
  const p=pending.get(proposalId);
  if(p.executing||consumed.has(proposalId))throw Error('APPROVAL_ALREADY_CONSUMED');
  if(Date.now()>p.expiry){pending.delete(proposalId);throw Error('PROPOSAL_EXPIRED')}
  if(!trustedKeyStatus().available)throw Error('TRUSTED_CHAT_APPROVAL_BRIDGE_UNAVAILABLE');
  verifyTicket(p,ticket);
  if(targetDigest()!==p.operation.targetSha256||executableDigest()!==p.operation.executableSha256)throw Error('PINNED_EXECUTABLE_OR_SOURCE_CHANGED');
  // Consume before execution: no ticket can authorize two root actions.
  p.executing=true;pending.delete(proposalId);consumed.add(proposalId);
  if(consumed.size>128)consumed.delete(consumed.values().next().value);
  const startedAt=Date.now();
  return new Promise((resolve,reject)=>{
   let stdout='',stderr='',failed=false,done=false;
   const child=spawn(fixedExecutable,p.operation.argv,{cwd:'/',env:{PATH:'/sbin:/bin',LANG:'C'},
     uid:0,gid:0,shell:false,stdio:['ignore','pipe','pipe']});
   const timer=setTimeout(()=>{failed=true;child.kill('SIGKILL')},MAX_ACTION_MS);
   const cap=(which,b)=>{
    const v=b.toString('utf8');
    if(which==='out')stdout+=v;else stderr+=v;
    if(Buffer.byteLength(stdout)+Buffer.byteLength(stderr)>1024){failed=true;child.kill('SIGKILL')}
   };
   child.stdout.on('data',b=>cap('out',b));
   child.stderr.on('data',b=>cap('err',b));
   child.on('error',e=>{failed=true;stderr=String(e.message).slice(0,150)});
   child.on('close',(code,signal)=>{
    if(done)return;done=true;clearTimeout(timer);
    const out={status:failed||code!==0?'failed':'completed',action:ACTION,proposalId,
      approvedUser:ticket.approvedUser,approvalSession:ticket.approvalSession,
      startedAt,completedAt:Date.now(),exitCode:code,signal,
      stdout:stdout.slice(0,1024),stderr:stderr.slice(0,300),readOnly:true};
    if(out.status==='completed'&&!stdout.toLowerCase().startsWith(p.operation.targetSha256+' '))
      return reject(Error('POST_EXECUTION_DIGEST_MISMATCH'));
    resolve(out);
   });
  });
 }
 function cancel({proposalId}={}){
  if(!pending.has(proposalId))throw Error('UNKNOWN_OR_CONSUMED_PROPOSAL');
  pending.delete(proposalId);return {cancelled:true,proposalId};
 }
 function status(){
  return {status:'experimental_ram_only',approvalAvailable:trustedKeyStatus().available,
   pendingProposals:pending.size,consumedGrants:consumed.size,
   allowlistedActions:[ACTION],genericRootShell:false,
   trustedApprovalPublicKeyConfigured:trustedKeyStatus().available,chatApprovalProvenanceVerifiedByBroker:false,
   note:'A local test key is not proof of ChatGPT account attestation; do not deploy signer key on Xoom'};
 }
 return {propose,execute,preflight,cancel,status,approvalBytes};
}
module.exports={createGate};