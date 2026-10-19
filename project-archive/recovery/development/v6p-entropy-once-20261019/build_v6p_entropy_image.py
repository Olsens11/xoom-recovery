#!/usr/bin/env python3
"""Build v6P offline entropy one-shot image from exact physically installed v6O."""
from pathlib import Path
from dataclasses import replace
import importlib.util, sys, gzip, struct, hashlib, stat, json, subprocess

P = Path("/home/ps2/xoom-phase1")
D = P/"private/network-foundation-next/development/v6p-entropy-once-20261019"
B = P/"private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img"
OUT = D/"R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img"
AUDIT = D/"V6P-ENTROPY-ONCE-IMAGE-AUDIT.json"
sha = lambda b: hashlib.sha256(b).hexdigest()
PIN = "86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d"
BINPIN = "31bee415d5bfbec648b02179106e6930be6a7448607c818d1ae66c2f6a40bf25"
assert not OUT.exists() and not AUDIT.exists(), "Never overwrite existing candidate"
image0 = B.read_bytes()
assert sha(image0) == PIN, "Wrong base image"
binpath = D/"xoom_entropy_once"
binary = binpath.read_bytes()
assert sha(binary) == BINPIN and len(binary) == 30300
assert binary[:5] == b"\x7fELF\x01" and struct.unpack_from("<H", binary, 18)[0] == 40
assert b"/sbin/linker\0" in binary

spec = importlib.util.spec_from_file_location("cp", P/"build-phase1b.py")
cp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cp
spec.loader.exec_module(cp)
ks,ka,rs,ra,ss,sa,ta,page,d,u = struct.unpack_from("<10I", image0,8)
assert page == 2048 and ss == 0
offset = page + cp.align(ks,page)
original = cp.decode(gzip.decompress(image0[offset:offset+rs]))
assert len(original) == 475 and len(set(x.name for x in original)) == 475
old = {x.name:x for x in original}

rcname = b"init.recovery.service.rc"
mgrname = b"sbin/xoom-toolkit-manager"
newname = b"sbin/xoom_entropy_once"
assert newname not in old and rcname in old and mgrname in old

oldrc = old[rcname].payload
assert oldrc.count(b"on boot\n") == 1
newrc = oldrc.replace(b"on boot\n",b"on boot\n    start xoomentropyonce\n",1)
anchor = b"service recovery /sbin/recovery\n"
assert newrc.count(anchor) == 1
svc = (b"\n# v6P one-shot CPU-jitter bootstrap, independent of packages or SD.\n"
       b"service xoomentropyonce /sbin/xoom_entropy_once --ensure\n"
       b"    class core\n"
       b"    disabled\n"
       b"    oneshot\n"
       b"    user root\n"
       b"    group root\n")
newrc = newrc.replace(anchor,anchor+svc,1)

oldmgr = old[mgrname].payload
needle = b"  dc_phase PREPARING_RUNTIME\n"
assert oldmgr.count(needle) == 1
guard = (b"  # Every DC Start can independently recover low boot-time entropy.\n"
         b"  /sbin/xoom_entropy_once --ensure >/tmp/xoom-toolkit/entropy-last-start.log 2>&1 ||\n"
         b"    { note \"$1\" ENTROPY_NOT_READY;return 14; }\n")
newmgr = oldmgr.replace(needle,guard+needle,1)
assert subprocess.run(["/bin/sh","-n"],input=newmgr,capture_output=True).returncode == 0
assert b"xoomentropyonce" in newrc and b"ENTROPY_NOT_READY" in newmgr

ino = max(x.fields[0] for x in original)+1
fields = [ino, stat.S_IFREG|0o755, 0,0,1,0,len(binary),0,0,0,0,len(newname)+1,0]
newentry = cp.Entry(b"070701",fields,newname,binary)
updated = []
for e in original[:-1]:
    if e.name == rcname:updated.append(replace(e,payload=newrc))
    elif e.name == mgrname:updated.append(replace(e,payload=newmgr))
    else:updated.append(e)
updated.extend([newentry,original[-1]])
raw = b"".join(x.encode() for x in updated)
raw += b"\0"*(cp.align(len(raw),512)-len(raw))
gz = gzip.compress(raw,compresslevel=9,mtime=0)
head = bytearray(image0[:page])
struct.pack_into("<I",head,16,len(gz))
kernel = image0[page:page+ks]
head[576:596] = cp.bootid(kernel,gz)
head[596:608] = b"\0"*12
candidate = bytes(head)+kernel
candidate += b"\0"*(cp.align(len(candidate),page)-len(candidate))
candidate += gz
candidate += b"\0"*(cp.align(len(candidate),page)-len(candidate))
assert len(candidate) <= 12582912

other = cp.decode(gzip.decompress(candidate[offset:offset+len(gz)]))
assert len(other) == 476 and len(set(x.name for x in other)) == 476
expected_changes = {rcname,mgrname,newname}
for e in other:
    if e.name == newname:
        assert e.payload == binary and e.fields == fields
    elif e.name == rcname:
        assert e.fields[:6]+e.fields[7:] == old[rcname].fields[:6]+old[rcname].fields[7:]
    elif e.name == mgrname:
        assert e.payload == newmgr
        assert e.fields[:6]+e.fields[7:] == old[mgrname].fields[:6]+old[mgrname].fields[7:]
    else:
        assert e.payload == old[e.name].payload and e.fields == old[e.name].fields, e.name
assert candidate[page:page+ks] == kernel
for name in (b"sbin/linker",b"sbin/libc++.so",b"sbin/libdl.so",b"sbin/libc.so",b"sbin/libm.so"):
    assert name in old
OUT.write_bytes(candidate)
audit = {
 "status":"OFFLINE_BUILT_NOT_FLASHED","parent_version":"v6O","parent_sha256":sha(image0),
 "candidate_sha256":sha(candidate),"candidate_bytes":len(candidate),"partition_bytes":12582912,
 "old_members":475,"new_members":476,"changed_existing":["init.recovery.service.rc","sbin/xoom-toolkit-manager"],
 "added_member":"sbin/xoom_entropy_once","binary_sha256":sha(binary),"binary_bytes":len(binary),
 "boot_action":"on boot: start xoomentropyonce",
 "boot_service":"disabled explicit one-shot; no daemon; no SD seed",
 "desktop_start_guard":"--ensure; fails closed if failed; no effect on package load",
 "unchanged_old_members":473,"kernel_exact":True,"trust_verifier_unmodified":True,
 "upstream_jitterentropy":"v3.6.3 / c90ff465dcdb6a6949542c72a26a8ab496daa8cb",
 "probe_hardware":"PASS --probe no kernel credit; Xoom USB ADB 2026-10-19",
 "boot_hardware":"NOT TESTED","flash":"NOT AUTHORIZED/NOT DONE"
}
AUDIT.write_text(json.dumps(audit,indent=2)+"\n")
print("V6P_OFFLINE_BUILT",len(candidate),sha(candidate))
