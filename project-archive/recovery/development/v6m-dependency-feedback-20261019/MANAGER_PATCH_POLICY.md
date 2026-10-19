# v6M Manager extension plan
In the existing v6L Desktop Commander Start arm, the recovery-owned helper
reports TIME_SYNC_NEEDED when synchronization was required and satisfied.
The existing Manager's STARTED_WITH_TIME_SYNC status conditional must match
this marker, not the old misleading TIME_SYNC_AUTO_STARTED name.

Immediately after resolver returns READY: publish PREPARING_RUNTIME to the
already-created /tmp/xoom-toolkit/deps/desktop-commander.state via atomic
private temp/rename before executing unchanged '$PROBE prepare'.

Immediately before 'setprop ctl.start xoomdcagent', publish STARTING_AGENT.
No other package's start path changes. The native TWRP executable observes
phase and notice files while waiting for the Start operation to finish.

Timeout policy: Wi-Fi 30s, in-progress Time Sync 25s and two 20s max one-shot
attempts. Pending Start does NOT survive those bounds, recovery reboot or
user Stop. Do not automatically launch a remotely accessible service hours
after an unsuccessful request. Let the user explicitly Retry after an error.
