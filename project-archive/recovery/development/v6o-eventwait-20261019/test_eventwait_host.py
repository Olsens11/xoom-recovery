#!/usr/bin/env python3
"""Kernel inotify integration tests: Linux host, no device writes."""
from pathlib import Path
import os,subprocess,tempfile,threading,time,json
DIR=Path('/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019')
SRC=DIR/'xoom-toolkit-eventwait.c'
results={}
def run_case(name,ready_before=False,mode='wifi',delay=.25,
             signals=None,timeout=3,expect=0,missing_dir=False):
    with tempfile.TemporaryDirectory(prefix='xoom-event-qa-') as temp:
        root=Path(temp)
        (root/'network').mkdir()
        (root/'sync').mkdir()
        (root/'probe.sh').write_text(
            '#!/bin/sh\n'
            'case "$1:$2:$3" in\n'
            'state:wifi-runtime:WIFI_READY) [ -e "'+str(root/'network/.wifi-ready')+'" ] ;;\n'
            'state:time-sync:SYNCED) [ "$(cat "'+str(root/'sync/status')+'" 2>/dev/null)" = SYNCED ] ;;\n'
            '*)exit 2;;\n'
            'esac\n')
        exe=root/'eventwait'
        args=['gcc','-O2','-Wall','-Werror','-std=c99','-D_POSIX_C_SOURCE=200809L',
              f'-DXOOM_WIFI_DIR="{root/"network"}"',
              f'-DXOOM_SYNC_DIR="{root/"sync"}"',
              f'-DXOOM_SCRIPT="{root/"probe.sh"}"',
              '-DXOOM_SHELL="/bin/sh"',
              str(SRC),'-o',str(exe)]
        subprocess.run(args,check=True,capture_output=True)
        if ready_before:
            if mode=='wifi':(root/'network/.wifi-ready').touch()
            else:(root/'sync/status').write_text('SYNCED\n')
        if missing_dir:(root/'network').rmdir()
        def send():
            time.sleep(delay)
            if signals is not None:
                for kind,wait in signals:
                    p=root/('network' if mode=='wifi' else 'sync')/('status' if mode=='sync' else '.wifi-ready')
                    if kind=='ready':
                        if mode=='wifi':p.touch()
                        else:p.write_text('SYNCED\n')
                    elif kind=='not-ready':
                        if mode=='wifi':(root/'network/unrelated').write_text('1\n')
                        else:p.write_text('STARTING\n')
                    time.sleep(wait)
        if signals is not None:
            thread=threading.Thread(target=send,daemon=True);thread.start()
        ts=time.monotonic()
        done=subprocess.run([str(exe),mode,str(timeout)],capture_output=True,timeout=timeout+4)
        elapsed=time.monotonic()-ts
        assert done.returncode==expect,(name,done.returncode,expect,done.stderr)
        if signals and signals[-1][0]=='ready':
            assert elapsed < timeout-.3,(name,'slow despite notification',elapsed)
        if expect==1:assert elapsed>=timeout-.15,(name,'premature timeout',elapsed)
        if expect==0 and ready_before:assert elapsed<.5,(name,'delayed immediate readiness',elapsed)
        results[name]={'result':'PASS','seconds':round(elapsed,3)}
run_case('wifi_already_ready',ready_before=True)
run_case('wifi_async_change',signals=[('ready',0)])
run_case('sync_already_complete',mode='sync',ready_before=True)
run_case('sync_async_completion',mode='sync',signals=[('ready',0)])
run_case('nonterminal_then_complete',mode='sync',signals=[('not-ready',.15),('ready',0)])
run_case('event_without_readiness_ignored',mode='wifi',signals=[('not-ready',.2),('ready',0)])
run_case('true_timeout_no_event',expect=1,timeout=1,signals=[])
run_case('notifier_parent_missing_fallback',missing_dir=True,expect=3)
# Bad user input is rejected without subscribing.
with tempfile.TemporaryDirectory() as t:
    d=Path(t);(d/'network').mkdir();(d/'sync').mkdir()
    src=(d/'probe.sh');src.write_text('#!/bin/sh\nexit 1\n')
    out=d/'waiter'
    subprocess.run(['gcc','-std=c99','-D_POSIX_C_SOURCE=200809L',
     f'-DXOOM_WIFI_DIR="{d/"network"}"',f'-DXOOM_SYNC_DIR="{d/"sync"}"',
     f'-DXOOM_SCRIPT="{src}"','-DXOOM_SHELL="/bin/sh"',str(SRC),'-o',str(out)],check=True)
    for args in [['strange','2'],['wifi','500'],['wifi','invalid']]:
        p=subprocess.run([str(out),*args],timeout=2)
        assert p.returncode==2
    results['rejects_invalid_mode_and_budgets']={'result':'PASS'}
report={'scope':'real Linux kernel inotify on host; not physical Xoom',
 'check_count':len(results),'checks':results}
(DIR/'HOST_EVENTWAIT_KERNEL_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print('HOST_EVENTWAIT_KERNEL_PASS',len(results))
