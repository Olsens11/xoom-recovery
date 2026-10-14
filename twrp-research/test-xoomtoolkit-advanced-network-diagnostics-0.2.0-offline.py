#!/usr/bin/env python3
"""Simulated recovery network states, bounded tests, and privacy.
No real Wi-Fi, packets, Android properties, or SD writes.
"""
from pathlib import Path
import os,subprocess,tempfile

SRC=Path(__file__).with_name("xoom-toolkit-advanced-network-diagnostics-0.2.0.sh").read_text()
with tempfile.TemporaryDirectory(prefix="xoom-adv-net-") as d:
    r=Path(d)
    root=r/"work";network=r/"network";sd=r/"sd";network.mkdir();sd.mkdir()
    mounts=r/"mounts";sdtype=r/"sd_type";mmctype=r/"mmc_type"
    routes=r/"route";resolv=r/"resolv";opstate=r/"operstate"
    bb=r/"busybox";getprop=r/"getprop";probe=r/"probe"
    trace=r/"trace"
    bb.write_text('''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
cmd=a[0]
if cmd=="ifconfig":
 if os.environ.get("IF_IP"):
  print("wlan0  Link encap:Ethernet")
  print("inet addr:"+os.environ["IF_IP"]+"  Bcast:192.168.0.255  Mask:255.255.255.0")
elif cmd=="--list":
 print("nslookup" if os.environ.get("NSLOOKUP_SUPPORTED","1")=="1" else "ping")
elif cmd=="timeout":
 # No actual subprocess or network probe. Confirm bounded invocation.
 assert a[1]=="-t" and int(a[2])<=7
 operation=a[4]
 with open(os.environ["TRACE"],"a") as f:f.write(operation+" "+str(a)+"\\n")
 if operation=="ping":
  sys.exit(0 if os.environ.get("ICMP_OK","1")=="1" else 1)
 if operation=="nslookup":
  assert a[-2:]==["example.com",os.environ.get("DNS_IP","192.168.0.1")]
  sys.exit(0 if os.environ.get("DNS_OK","1")=="1" else 1)
 sys.exit(21)
else:
 os.execvp(cmd,a)
''')
    getprop.write_text('''#!/bin/sh
case "$1" in
 xoom.n2.wifi.status) echo "${WIFI_STATE:-NOT_STARTED}" ;;
 net.dns1) echo "${DNS_IP:-192.168.0.1}" ;;
 init.svc.xoomdns) echo "${DNS_SERVICE:-running}" ;;
 init.svc.xoomwifiworker) echo stopped ;;
 init.svc.adbd) echo running ;;
 *) echo UNEXPECTED_PROP ;;
esac
''')
    probe.write_text('''#!/bin/sh
echo "wpa_state=${WPA_STATE:-DISCONNECTED}"
echo 'key_mgmt=SECRET_WIFI_DO_NOT_INCLUDE'
''')
    for f in (bb,getprop,probe):f.chmod(0o755)
    routes.write_text("Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\n"
                      "wlan0 00000000 0100A8C0 0003 0 0 0 00000000 0 0 0\n")
    resolv.write_text("nameserver 192.168.0.1\n")
    opstate.write_text("up\n")
    sdtype.write_text("SD\n");mmctype.write_text("MMC\n")
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat ro,relatime 0 0\n")
    swaps={
      "BB=/sbin/busybox":"BB="+str(bb),
      "GETPROP=/sbin/getprop":"GETPROP="+str(getprop),
      "PROBE=/system/bin/xoom_wpa_probe":"PROBE="+str(probe),
      "ROOT=/tmp/xoom-toolkit/network-diagnostics":"ROOT="+str(root),
      "NETWORK=/tmp/xoom-network":"NETWORK="+str(network),
      "ROUTES=/proc/net/route":"ROUTES="+str(routes),
      "RESOLV=/etc/resolv.conf":"RESOLV="+str(resolv),
      "OPSTATE=/sys/class/net/wlan0/operstate":"OPSTATE="+str(opstate),
      "SD=/external_sd/XoomToolkit":"SD="+str(sd),
      "MOUNTS=/proc/mounts":"MOUNTS="+str(mounts),
      "SDTYPE=/sys/block/mmcblk0/device/type":"SDTYPE="+str(sdtype),
      "MMCTYPE=/sys/block/mmcblk1/device/type":"MMCTYPE="+str(mmctype),
    }
    for a,b in swaps.items():
        assert a in SRC,a
        SRC=SRC.replace(a,b)
    test=r/"diag.sh";test.write_text(SRC)
    subprocess.run(["sh","-n",str(test)],check=True)
    env={**os.environ,"TRACE":str(trace)}
    def run(name,act,expected=0,**override):
        trace.unlink(missing_ok=True)
        e={**env,**{k:str(v) for k,v in override.items()}}
        p=subprocess.run(["sh",str(test),act],capture_output=True,text=True,
                         env=e,timeout=20)
        assert p.returncode==expected,(name,p.returncode,p.stdout,p.stderr)
        report=(root/"report.txt").read_text() if (root/"report.txt").exists() else ""
        calls=trace.read_text() if trace.exists() else ""
        assert "SECRET_WIFI" not in p.stdout+report
        print("PASS",name)
        return p,report,calls
    assert run("initial_status","status")[0].stdout.strip()=="NEVER_RUN"
    run("invalid_operation","connect",expected=2)
    run("refuse_export_without_report","export",expected=1)
    _,report,calls=run("passive_offline","inspect",WIFI_STATE="NOT_STARTED")
    assert "active_tests=NOT_REQUESTED" in report and not calls
    assert "wpa_authentication=NOT_COMPLETED" in report
    assert "verified_wifi_ready=NO" in report
    run("manual_tests_skipped_offline","test",WIFI_STATE="NOT_STARTED")
    assert "test_gateway_icmp=SKIPPED_NETWORK_NOT_READY" in (root/"report.txt").read_text()
    (network/".wifi-ready").touch()
    _,report,calls=run("stale_ready_marker","test",WIFI_STATE="WIFI_READY",
                       WPA_STATE="ASSOCIATED",IF_IP="192.168.0.3")
    assert "test_dns_a=SKIPPED_NETWORK_NOT_READY" in report and not calls
    _,report,calls=run("no_dhcp_ip_skips_all_probes","test",WIFI_STATE="WIFI_READY",
                       WPA_STATE="COMPLETED")
    assert "verified_wifi_ready=NO" in report and not calls
    ready={"WIFI_STATE":"WIFI_READY","WPA_STATE":"COMPLETED","IF_IP":"192.168.0.3"}
    _,report,calls=run("connected_passive_only","inspect",**ready)
    assert "wpa_authentication=COMPLETED" in report and "verified_wifi_ready=YES" in report
    assert "default_gateway=192.168.0.1" in report,report
    assert "wlan_ipv4=192.168.0.3" in report and "dns_ipv4_server=192.168.0.1" in report
    assert "recovery_dns_proxy_service=running" in report and not calls
    _,report,calls=run("active_connectivity_success","test",**ready)
    assert "test_gateway_icmp=REPLIED" in report
    assert "test_public_ipv4_icmp=REPLIED" in report
    assert "test_dns_a=ANSWER_RECEIVED" in report
    assert calls.count("ping ")==2 and calls.count("nslookup ")==1,calls
    _,report,calls=run("icmp_and_dns_blocked","test",ICMP_OK="0",DNS_OK="0",**ready)
    assert report.count("NO_REPLY_OR_BLOCKED")==2
    assert "test_dns_a=NO_ANSWER_OR_BLOCKED" in report
    assert len(calls.splitlines())==3
    _,report,calls=run("nslookup_missing_is_not_dns_failure","test",
                       NSLOOKUP_SUPPORTED="0",**ready)
    assert "test_dns_a=NOT_SUPPORTED_BUSYBOX" in report and "nslookup " not in calls
    _,report,calls=run("untrusted_prop_suppressed","inspect",
                       **{**ready,"WIFI_STATE":"SSID_PRIVATE_PASSWORD","DNS_IP":"bad;secret"})
    assert "SSID_PRIVATE_PASSWORD" not in report and "wifi_state=UNKNOWN" in report
    run("readonly_sd_refuses_export","export",expected=1)
    assert not (sd/"reports").exists()
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat rw,relatime 0 0\n")
    path=Path(run("explicit_writable_sd_export","export")[0].stdout.strip())
    assert path.parent==sd/"reports" and path.read_text()==(root/"report.txt").read_text()
    sdtype.write_text("MMC\n")
    run("wrong_sd_card_identity_refused","export",expected=1)
    print("ADVANCED_NETWORK_DIAGNOSTICS_SANDBOX_PASS")
