from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
s=(p/"audit-n2-r17-recovery-tools.py").read_text()
needle='libpaths=defaultdict(list)'
assert needle in s
s=s.replace(needle,'''# Simulate isolated legacy crypto for the original twrpdec only.
base=(root/"private/xoom-twrp311-network-n2-r13-native-wifi-UNFLASHED.img").read_bytes()
bk,bka,br,bra,bs,bsa,bt,bpage,bd,bu=struct.unpack_from("<10I",base,8)
old=b.decode(gzip.decompress(base[bpage+b.align(bk,bpage):bpage+b.align(bk,bpage)+br]))
legacy={e.name.decode():e.payload for e in old}
assert "sbin/libcrypto.so" in legacy
files["sbin/libcrypto.so"]=legacy["sbin/libcrypto.so"]
'''+needle)
needle="results=[]"
s=s.replace(needle,'roots=["sbin/twrpdec"]\n'+needle)
s=s.replace("xoom-n2-r17-recovery-tools-audit.json","xoom-n2-r17-twrpdec-oldcrypto-audit.json")
out=p/"audit-n2-r17-oldcrypto-simulation.py"
assert not out.exists()
out.write_text(s)
print(out)
