#!/usr/bin/env python3
"""Remote QA for Motorola Xoom TWRP over USB ADB.

Host-only Python stdlib. No APK, recovery partition changes, persistent network
listener, or microSD requirement. Input streams staged transiently under /tmp.
R19 adds the VolumeUp+VolumeDown RAM screenshot chord.
"""
import argparse
import hashlib
import pathlib
import os
import re
import struct
import subprocess
import sys
import tempfile
import time

DEFAULT_SERIAL = os.environ.get("XOOM_SERIAL", "")
EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
SYN_REPORT, SYN_MT_REPORT = 0, 2
KEY_VOLUMEDOWN, KEY_VOLUMEUP = 114, 115
ABS_MT_TOUCH_MAJOR, ABS_MT_POSITION_X, ABS_MT_POSITION_Y = 48, 53, 54
ABS_MT_TRACKING_ID, ABS_MT_PRESSURE = 57, 58

def adb(serial, *params, check=True):
    return subprocess.run(["adb", "-s", serial, *map(str,params)], check=check,
                          capture_output=True, text=True, timeout=35)

def verify(serial, event, identity):
    state=adb(serial, "get-state").stdout.strip()
    if state != "device":
        raise RuntimeError("ADB device not ready: "+state)
    r=adb(serial,"shell","cat /proc/bus/input/devices").stdout
    pattern=r'N: Name="'+re.escape(identity)+r'".*?H: Handlers=[^\r\n]*'+re.escape(event)+r'\b'
    if not re.search(pattern,r,flags=re.S):
        raise RuntimeError("Refusing input: expected "+identity+" at "+event+" not found")

def pack(events):
    return b"".join(struct.pack("<IIHHi",0,0,t,c,v) for t,c,v in events)

def deliver(serial, event_node, events, identity):
    event="event"+str(event_node)
    verify(serial,event,identity)
    payload=pack(events)
    with tempfile.TemporaryDirectory() as directory:
        source=pathlib.Path(directory)/"xoom-event.bin"
        source.write_bytes(payload)
        dest="/tmp/xoom-remote-event.bin"
        adb(serial,"push",str(source),dest)
        try:
            adb(serial,"shell","/sbin/busybox cat "+dest+" > /dev/input/"+event)
        finally:
            adb(serial,"shell","/sbin/busybox rm -f "+dest,check=False)
    print("Input submitted:",identity,event,"events",len(events))

def sync(serial):
    deliver(serial,6,[(EV_SYN,SYN_REPORT,0)],"qtouch-touchscreen")

def tap(serial,x,y):
    if not (0 <= x < 1280 and 0 <= y < 800):
        raise ValueError("Touch coordinates must be within 1280x800 screen")
    events=[
        (EV_ABS,ABS_MT_TRACKING_ID,1),
        (EV_ABS,ABS_MT_POSITION_X,x),
        (EV_ABS,ABS_MT_POSITION_Y,y),
        (EV_ABS,ABS_MT_TOUCH_MAJOR,8),
        (EV_ABS,ABS_MT_PRESSURE,60),
        (EV_SYN,SYN_MT_REPORT,0),
        (EV_SYN,SYN_REPORT,0),
        (EV_ABS,ABS_MT_TRACKING_ID,-1),
        (EV_SYN,SYN_MT_REPORT,0),
        (EV_SYN,SYN_REPORT,0)
    ]
    deliver(serial,6,events,"qtouch-touchscreen")

def capture(serial,output):
    # R19 only. Original screenshot hotkey is unchanged.
    chord=[
        (EV_KEY,KEY_VOLUMEUP,1),(EV_SYN,SYN_REPORT,0),
        (EV_KEY,KEY_VOLUMEDOWN,1),(EV_SYN,SYN_REPORT,0),
        (EV_KEY,KEY_VOLUMEDOWN,0),(EV_SYN,SYN_REPORT,0),
        (EV_KEY,KEY_VOLUMEUP,0),(EV_SYN,SYN_REPORT,0)
    ]
    deliver(serial,7,chord,"stingray-keypad")
    time.sleep(1)
    dest=pathlib.Path(output).resolve()
    result=adb(serial,"pull","/tmp/xoom-remote/capture.png",str(dest),check=False)
    if result.returncode:
        raise RuntimeError("No RAM screenshot found; shortcut requires offline R19 or newer. "+result.stderr)
    print("Screenshot:",dest, "bytes",dest.stat().st_size,
          "SHA256",hashlib.sha256(dest.read_bytes()).hexdigest())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial",default=DEFAULT_SERIAL)
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("sync-test",help="Harmless input-device write check")
    tap_parser=sub.add_parser("tap",help="Tap touchscreen at x,y; can change recovery UI")
    tap_parser.add_argument("x",type=int);tap_parser.add_argument("y",type=int)
    cap=sub.add_parser("capture",help="Trigger R19 RAM capture then ADB pull PNG")
    cap.add_argument("--output",default=str(pathlib.Path(__file__).with_name("xoom-remote-capture.png")))
    args=parser.parse_args()
    if not args.serial:
        parser.error("--serial or XOOM_SERIAL must specify the authorized device")
    if args.action=="sync-test":sync(args.serial)
    elif args.action=="tap":tap(args.serial,args.x,args.y)
    elif args.action=="capture":capture(args.serial,args.output)

if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
        print("ERROR:",error,file=sys.stderr)
        sys.exit(1)