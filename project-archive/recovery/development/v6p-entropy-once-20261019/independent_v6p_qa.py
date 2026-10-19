#!/usr/bin/env python3
"""Independent compare v6P with exact pinned installed v6O (never flashes)."""
import importlib.util, sys, gzip, struct, hashlib, stat, json
from pathlib import Path
P=Path("/home/ps2/xoom-phase1")
D=P/"private/network-foundation-next/development/v6p-entropy-once-20261019"
a=(P/"private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img").read_bytes()
b=(D/"R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img").read_bytes()
hash=lambda x:hashlib.sha256(x).hexdigest()
assert hash(a)=="86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d"
assert hash(b)=="7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe"
spec=importlib.util.spec_from_file_location("cp",P/"build-phase1b.py")
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
checks={}
def test(name,condition):
    checks[name]=bool(condition)
    if not condition: raise AssertionError(name)
def unpack(x):
    ks,ka,rs,ra,ss,sa,ta,page,d,u=struct.unpack_from("<10I",x,8)
    off=page+cp.align(ks,page)
    return page,ks,rs,cp.decode(gzip.decompress(x[off:off+rs]))
page,ks,ars,aa=unpack(a)
qpage,qks,brs,bb=unpack(b)
old={x.name:x for x in aa};new={x.name:x for x in bb}
modified=[p.decode() for p in old if old[p].payload!=new[p].payload]
added=[p.decode() for p in new if p not in old]
test("base_and_candidate_exact_SHA",True)
test("unchanged_kernel",a[page:page+ks]==b[qpage:qpage+qks])
test("same_kernel_size_and_page",page==qpage==2048 and ks==qks)
test("member_set_unique",len(aa)==len(old)==475 and len(bb)==len(new)==476)
test("exact_changed_existing_members",sorted(modified)==["init.recovery.service.rc","sbin/xoom-toolkit-manager"])
test("one_new_member",added==["sbin/xoom_entropy_once"])
test("473_other_members_byte_exact",all(new[p].payload==v.payload and new[p].fields==v.fields for p,v in old.items() if p.decode() not in modified))
for p in (b"init.recovery.service.rc", b"sbin/xoom-toolkit-manager"):
    x,y=old[p],new[p]
    test("metadata_unchanged_"+p.decode(),x.fields[:6]+x.fields[7:]==y.fields[:6]+y.fields[7:])
test("boot_service_oneshot",b"service xoomentropyonce /sbin/xoom_entropy_once --ensure" in new[b"init.recovery.service.rc"].payload and b"    start xoomentropyonce" in new[b"init.recovery.service.rc"].payload)
test("start_guard_present",b"/sbin/xoom_entropy_once --ensure" in new[b"sbin/xoom-toolkit-manager"].payload and b"ENTROPY_NOT_READY" in new[b"sbin/xoom-toolkit-manager"].payload)
trust_paths=[x for x in old if b"verify" in x or b"install" in x or b"pin" in x]
test("trust_artifacts_byte_exact",len(trust_paths)>=1 and all(old[x].payload==new[x].payload and old[x].fields==new[x].fields for x in trust_paths))
test("dependency_resolver_exact",old[b"sbin/xoom-toolkit-deps"].payload==new[b"sbin/xoom-toolkit-deps"].payload)
test("binary_arm_and_linker",new[b"sbin/xoom_entropy_once"].payload.startswith(bytes.fromhex("7f454c4601")) and b"/sbin/linker"+bytes([0]) in new[b"sbin/xoom_entropy_once"].payload)
test("binary_root_0755",new[b"sbin/xoom_entropy_once"].fields[1]&0o777==0o755 and new[b"sbin/xoom_entropy_once"].fields[2]==0 and new[b"sbin/xoom_entropy_once"].fields[3]==0)
test("arm_hash_verified",hash(new[b"sbin/xoom_entropy_once"].payload)=="31bee415d5bfbec648b02179106e6930be6a7448607c818d1ae66c2f6a40bf25")
test("no_extra_boot_payload_or_overflow",len(b)<=12582912)
boff=qpage+cp.align(qks,qpage)
test("boot_id_recomputed",b[576:596]==cp.bootid(b[qpage:qpage+qks],b[boff:boff+brs]))
test("source_pinned", (D/"jitterentropy-upstream-v3.6.3/LICENSE").is_file() and (D/"xoom-entropy.c").is_file() and (D/"Android.mk").is_file())
out={"status":"INDEPENDENT_OFFLINE_IMAGE_AUDIT_PASS","count":len(checks),"checks":checks,"candidate_sha256":hash(b),"candidate_bytes":len(b),"boot_hardware_test":"NOT_PERFORMED","flash":"NOT PERFORMED"}
(D/"V6P-INDEPENDENT-OFFLINE-QA.json").write_text(json.dumps(out,indent=2)+"\n")
print("V6P_INDEPENDENT_QA_PASS",len(checks),hash(b))
