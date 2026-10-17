'use strict';
const {spawn}=require('node:child_process'), readline=require('node:readline');
const D='/tmp/xoom-dc-runtime-qa/debian24',ROOT='/tmp/xoom-dc-runtime-qa/dc-scratch';
const child=spawn(D+'/ld-linux-armhf.so.3',['--library-path',D+'/usr/lib/arm-linux-gnueabihf',D+'/usr/bin/node','--max-old-space-size=64',D+'/xoom-scratch-mcp-v14-candidate.js'],{stdio:['pipe','pipe','pipe']});
let seq=0;const pending=new Map();
readline.createInterface({input:child.stdout}).on('line',l=>{try{let a=JSON.parse(l);const p=pending.get(a.id);if(p){pending.delete(a.id);p(a)}}catch(e){console.log('BAD_REPLY',e.message)}});
child.stderr.on('data',b=>console.log('SERVER_LOG',b.toString().trim()));
child.on('error',e=>console.log('CHILD_ERROR',e.message));
function request(method,params){return new Promise((resolve,reject)=>{let id=++seq;let timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout '+method))},5000);pending.set(id,msg=>{clearTimeout(timer);resolve(msg)});child.stdin.write(JSON.stringify({jsonrpc:'2.0',id,method,params})+'\n')})}
async function tool(name,args){let r=await request('tools/call',{name,arguments:args});if(r.error)throw Error(JSON.stringify(r.error));return {value:JSON.parse(r.result.content[0].text),isError:r.result.isError}}
const eq=(cond,label)=>{if(!cond)throw Error('FAIL '+label);console.log(label+'_PASS')};
(async()=>{
 const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
 const keyFile=D+'/privileged-host-approval.pub';
 if(fs.existsSync(keyFile))throw Error('QA requires no preinstalled signer');
 let a=await request('initialize',{protocolVersion:'2025-06-18'});
 eq(a.result.serverInfo.version==='0.14.0-local','V14_CONTROLLER_ID');
 a=await request('tools/list',{});
 eq(a.result.tools.length===27,'V14_26_UPSTREAM_NAMES_PLUS_ONE_EXTENSION');
 eq(a.result.tools.find(t=>t.name==='privileged_action')?.annotations.destructiveHint===true,'V14_PRIVILEGED_TOOL_DECLARED_DESTRUCTIVE');
 let status=await tool('privileged_action',{phase:'status'});
 eq(!status.isError&&!status.value.approvalAvailable&&status.value.allowlistedActions.length===1&&!status.value.genericRootShell,'V14_CLOSED_WITHOUT_TRUST_ANCHOR');
 let p=await tool('privileged_action',{phase:'propose',action:'arbitrary_shell',reason:'Need exact fixed root action',alternatives:['ordinary scratch tool failed']});
 eq(p.isError,'V14_UNALLOWLISTED_ACTION_DENIED');
 p=await tool('privileged_action',{phase:'propose',action:'verify_controller_integrity',reason:'Need to hash the protected controller source after UID2000 read was denied',alternatives:[]});
 eq(p.isError,'V14_REQUIRE_EVIDENCE_OF_ALTERNATIVES');
 const args={phase:'propose',action:'verify_controller_integrity',
   reason:'Verify pinned root-owned controller binary integrity after unprivileged read access was denied',
   alternatives:['UID2000 scratch read cannot access root-owned runtime controller','Normal unprivileged get_file_info is intentionally scratch-only']};
 p=await tool('privileged_action',args);
 console.log('V14_PROPOSAL',JSON.stringify(p.value));
 eq(!p.isError&&p.value.status==='awaiting_verified_user_approval'&&p.value.operation.effectiveUid===0&&p.value.operation.sideEffects.startsWith('none'),'V14_REVIEWABLE_FIXED_COMMAND');
 eq(p.value.operation.argv.length===2&&p.value.operation.executable==='/sbin/busybox'&&p.value.operation.argv[0]==='sha256sum','V14_FIXED_HASH_ONLY');
 const proposal=p.value;
 let deny=await tool('privileged_action',{phase:'execute',proposalId:proposal.proposalId,ticket:{anything:'user says yes'}});
 eq(deny.isError&&deny.value.error.includes('TRUSTED_CHAT_APPROVAL_BRIDGE_UNAVAILABLE'),'V14_CHAT_TEXT_NOT_AUTHORIZATION');
 const pair=crypto.generateKeyPairSync('ed25519');
 fs.writeFileSync(keyFile,pair.publicKey.export({type:'spki',format:'pem'}),{mode:0o600});
 fs.chownSync(keyFile,0,0);fs.chmodSync(keyFile,0o600);
 const ticket={
   proposalId:proposal.proposalId,proposalDigest:proposal.proposalDigest,
   nonce:proposal.nonce,approvedUser:'qa_user_only',
   approvalSession:'local_hardware_test',issuedAt:Date.now(),
   expiresAt:Math.min(proposal.expiresAt,Date.now()+30000)
 };
 // The QA signer exists only transiently for signature verification; it never enables an actual root execution.
 const msg=k=>Buffer.from(JSON.stringify({proposalId:k.proposalId,proposalDigest:k.proposalDigest,nonce:k.nonce,
   approvedUser:k.approvedUser,approvalSession:k.approvalSession,issuedAt:k.issuedAt,expiresAt:k.expiresAt}));
 ticket.signature=crypto.sign(null,msg(ticket),pair.privateKey).toString('base64');
 const malformed={...ticket,nonce:'0'.repeat(32)};
 deny=await tool('privileged_action',{phase:'preflight',proposalId:proposal.proposalId,ticket:malformed});
 eq(deny.isError&&deny.value.error.includes('APPROVAL_NOT_BOUND'),'V14_CROSS_BOUND_TICKET_REJECTED');
 const valid=await tool('privileged_action',{phase:'preflight',proposalId:proposal.proposalId,ticket});
 eq(!valid.isError&&valid.value.status==='signed_approval_preflight_passed'&&valid.value.executionPerformed===false,'V14_SIGNED_MOCK_TICKET_PREFLIGHT');
 deny=await tool('privileged_action',{phase:'preflight',proposalId:proposal.proposalId,ticket:{...ticket,approvalSession:'forged_context'}});
 eq(deny.isError&&deny.value.error.includes('APPROVAL_SIGNATURE_REJECTED'),'V14_SIGNATURE_TAMPER_REJECTED');
 const cancellation=await tool('privileged_action',{phase:'cancel',proposalId:proposal.proposalId});
 eq(!cancellation.isError&&cancellation.value.cancelled,'V14_PENDING_REVOKED');
 deny=await tool('privileged_action',{phase:'preflight',proposalId:proposal.proposalId,ticket});
 eq(deny.isError,'V14_CANCELLED_GRANT_NOT_REPLAYABLE');
 console.log('XOOM_V14_GATE_PREFLIGHT_ONLY_HARDWARE_PASS');
})().catch(e=>{console.error('V14_QA_FAIL',e.stack);process.exitCode=1}).finally(()=>{
 try{require('node:fs').unlinkSync(D+'/privileged-host-approval.pub')}catch{}
 child.stdin.end();setTimeout(()=>child.kill(),250).unref()
});